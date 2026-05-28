from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.db.models import OuterRef, Subquery
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_POST
from datetime import timedelta
import secrets

from .db_compat import get_safe_usuario_value, get_usuario_model_from_instance, usuario_supports_verificacion_sena
from .models import CarritoItem, Catalogo, DetallePedido, Disponibilidad, Notificacion, Pedido, Producto, Subcategoria, VerificacionSenaToken
from .validacion_sena import cargar_captura_desde_data_url
from .views import _auto_cancelar_pedidos_pendientes_vencidos, _crear_notificacion, _expirar_solicitudes_validacion_manual, _notificar_staff, _reabrir_solicitudes_con_enlace_vencido, _registrar_auditoria


DEVOLUCION_CODIGO_SEGUNDOS = 60


def _usuario_cliente(request):
    if not request.user.is_authenticated:
        return False
    if getattr(request.user, 'is_superuser', False) or getattr(request.user, 'is_staff', False):
        return False

    rol = (getattr(getattr(request.user, 'id_rol_fk', None), 'nombre_rol', '') or '').strip().lower()
    return rol in ['', 'usuario', 'aprendiz', 'instructor']


def _asegurar_codigo_devolucion(pedido, now):
    if pedido.estado not in ('entregado', 'vencido'):
        return False

    vigente = bool(
        pedido.codigo_entrega
        and pedido.codigo_expira_en
        and pedido.codigo_expira_en >= now
    )
    if not vigente:
        pedido.codigo_entrega = f'{secrets.randbelow(1000000):06d}'
        pedido.codigo_expira_en = now + timedelta(seconds=DEVOLUCION_CODIGO_SEGUNDOS)
        pedido.fch_ult_act = now
        pedido.save(update_fields=['codigo_entrega', 'codigo_expira_en', 'fch_ult_act'])
    return True


def _usuario_tiene_validacion_sena(usuario):
    usuario_model = get_usuario_model_from_instance(usuario)
    if not usuario_model or not usuario_supports_verificacion_sena(usuario_model):
        return True
    return get_safe_usuario_value(usuario, 'verificacion_sena_estado', 'pendiente') == 'validado'


def _redireccion_validacion_destino(request):
    destino = (request.GET.get('next') or request.POST.get('next') or '').strip()
    permitidos = {reverse('carrito_usuario'), reverse('panel_usuario')}
    return destino if destino in permitidos else reverse('carrito_usuario')


def _migrar_carrito_sesion_a_bd(request):
    carrito_sesion = request.session.get('carrito', {})
    if not carrito_sesion:
        return

    now = timezone.now()
    for prod_id, cantidad in carrito_sesion.items():
        try:
            prod_id_int = int(prod_id)
            cantidad_int = max(int(cantidad), 1)
        except (TypeError, ValueError):
            continue

        producto = Producto.objects.filter(pk=prod_id_int).first()
        if not producto:
            continue

        item, created = CarritoItem.objects.get_or_create(
            id_usuario_fk=request.user,
            id_prod_fk=producto,
            defaults={
                'cantidad': cantidad_int,
                'fch_registro': now,
                'fch_ult_act': now,
            },
        )
        if not created:
            item.cantidad = max(item.cantidad, cantidad_int)
            item.fch_ult_act = now
            item.save(update_fields=['cantidad', 'fch_ult_act'])

    request.session['carrito'] = {}


def _build_carrito_context(request):
    _migrar_carrito_sesion_a_bd(request)

    carrito_items = []
    carrito_items_pedido = []
    total_unidades = 0
    productos_disponibles = 0
    productos_sin_stock = 0

    carrito_qs = (
        CarritoItem.objects
        .select_related('id_prod_fk__id_cat_fk')
        .filter(id_usuario_fk=request.user)
        .order_by('-id_carrito_item')
    )

    for item in carrito_qs:
        producto = item.id_prod_fk
        cantidad = int(item.cantidad)

        disp = Disponibilidad.objects.filter(id_prod_fk=producto).order_by('-id_disp').first()
        producto.stock_actual = (disp.cantidad if disp and disp.cantidad is not None else (disp.stock if disp else 0))
        supera_stock = cantidad > (producto.stock_actual or 0)

        if cantidad > 0:
            total_unidades += cantidad
        if producto.stock_actual and producto.stock_actual > 0:
            productos_disponibles += 1
        else:
            productos_sin_stock += 1

        item_data = {
            'producto': producto,
            'cantidad': cantidad,
            'supera_stock': supera_stock,
        }
        carrito_items.append(item_data)

        if cantidad > 0:
            carrito_items_pedido.append(item_data)

    carrito_valido = bool(carrito_items_pedido) and all(
        not item['supera_stock'] and (item['producto'].stock_actual or 0) > 0
        for item in carrito_items_pedido
    )

    return {
        'carrito_items': carrito_items,
        'carrito_items_pedido': carrito_items_pedido,
        'total_productos': len(carrito_items_pedido),
        'total_unidades': total_unidades,
        'productos_disponibles': productos_disponibles,
        'productos_sin_stock': productos_sin_stock,
        'carrito_valido': carrito_valido,
        'requiere_validacion_sena': not _usuario_tiene_validacion_sena(request.user),
        'verificacion_sena_estado': getattr(request.user, 'verificacion_sena_estado', 'pendiente'),
    }


@login_required
def carrito_usuario(request):
    if not _usuario_cliente(request):
        return redirect('dashboard')
    return render(request, 'inventario/usuario/carrito_usuario.html', _build_carrito_context(request))


@login_required
def validacion_sena(request):
    if not _usuario_cliente(request):
        return redirect('dashboard')

    _expirar_solicitudes_validacion_manual()
    _reabrir_solicitudes_con_enlace_vencido()

    usuario = request.user
    redirect_to = _redireccion_validacion_destino(request)

    if request.method == 'POST':
        foto_validacion = request.FILES.get('foto_validacion')
        if not foto_validacion:
            foto_validacion = cargar_captura_desde_data_url(request.POST.get('foto_validacion_captura'))
        if not foto_validacion:
            messages.error(request, 'Debes enviar una foto del carnet para que el administrador la revise.')
        else:
            usuario.verificacion_sena_imagen = foto_validacion
            usuario.verificacion_sena_estado = 'documento_cargado'
            usuario.verificacion_sena_observacion = 'Foto del carnet enviada al administrador para revisión manual.'
            usuario.save(update_fields=[
                'verificacion_sena_estado',
                'verificacion_sena_imagen',
                'verificacion_sena_observacion',
            ])
            _crear_notificacion(
                usuario=usuario,
                tipo='documento_validacion_sena',
                titulo='Foto enviada para validación SENA',
                mensaje='Tu foto del carnet fue enviada al administrador. Quedará pendiente de revisión manual.',
            )
            _notificar_staff(
                tipo='staff_documento_validacion_sena',
                titulo='Nueva foto para validación SENA',
                mensaje=f'{getattr(usuario, "nombre", "") or getattr(usuario, "correo", "Usuario")} envió su foto de carnet para revisión manual.',
            )
            messages.success(request, 'Tu foto fue enviada al administrador para su revisión. Cuando la apruebe podrás continuar.')
            return redirect(redirect_to)

    return render(request, 'inventario/usuario/validacion_sena.html', {
        'usuario': usuario,
        'redirect_to': redirect_to,
        'estado_validacion': usuario.verificacion_sena_estado,
        'ya_validado': _usuario_tiene_validacion_sena(usuario),
    })


@login_required
@require_POST
def solicitar_validacion_manual(request):
    if not _usuario_cliente(request):
        return redirect('dashboard')

    _expirar_solicitudes_validacion_manual()
    _reabrir_solicitudes_con_enlace_vencido()

    usuario = request.user
    if _usuario_tiene_validacion_sena(usuario):
        messages.success(request, 'Tu cuenta ya está validada para realizar pedidos.')
        return redirect('validacion_sena')

    if usuario.verificacion_sena_estado in {'solicitada', 'enlace_enviado', 'documento_cargado'}:
        messages.success(request, 'Tu solicitud manual ya está en proceso. Revisa tus notificaciones o tu correo.')
        return redirect('validacion_sena')

    motivo = (request.POST.get('motivo_manual') or '').strip()
    usuario.verificacion_sena_estado = 'solicitada'
    usuario.verificacion_sena_solicitada_en = timezone.now()
    usuario.verificacion_sena_observacion = motivo or 'El usuario solicitó validación manual porque no fue posible validar el carnet automáticamente.'
    usuario.save(update_fields=[
        'verificacion_sena_estado',
        'verificacion_sena_solicitada_en',
        'verificacion_sena_observacion',
    ])

    nombre_usuario = (f'{usuario.nombre or ""} {usuario.apellido or ""}'.strip() or usuario.correo)
    _crear_notificacion(
        usuario=usuario,
        tipo='solicitud_validacion_sena',
        titulo='Solicitud de validación SENA enviada',
        mensaje='Tu solicitud fue enviada al administrador. Cuando apruebe la revisión, te llegará un correo con el enlace para cargar tu carnet o certificado.',
    )
    _notificar_staff(
        tipo='staff_solicitud_validacion_sena',
        titulo='Solicitud manual de validación SENA',
        mensaje=f'{nombre_usuario} solicitó validación manual de carnet SENA. Documento registrado: {usuario.cc or "sin documento"}.',
    )
    messages.success(request, 'Tu solicitud manual fue enviada al administrador. Te avisaremos cuando liberen el enlace de carga.')
    return redirect('validacion_sena')


def validacion_sena_carga_manual(request, token):
    token_obj = (
        VerificacionSenaToken.objects
        .select_related('usuario')
        .filter(token=token, usado_en__isnull=True)
        .first()
    )
    token_valido = bool(token_obj and token_obj.expira_en >= timezone.now())
    usuario = token_obj.usuario if token_obj else None
    carga_exitosa = False

    if token_valido and request.method == 'POST':
        soporte = request.FILES.get('documento_soporte')
        if not soporte:
            messages.error(request, 'Debes adjuntar una imagen del carnet o del certificado SENA.')
        elif not (getattr(soporte, 'content_type', '') or '').startswith('image/'):
            messages.error(request, 'El documento manual debe ser una imagen válida.')
        else:
            # Validaci�n autom�tica removida - admin revisa manualmente
            usuario.verificacion_sena_documento = soporte
            usuario.verificacion_sena_estado = 'documento_cargado'
            usuario.verificacion_sena_observacion = 'Documento manual cargado y pendiente de aprobación administrativa.'
            usuario.save(update_fields=[
                'verificacion_sena_documento',
                'verificacion_sena_estado',
                'verificacion_sena_observacion',
            ])
            token_obj.usado_en = timezone.now()
            token_obj.save(update_fields=['usado_en'])
            _crear_notificacion(
                usuario=usuario,
                tipo='documento_validacion_sena',
                titulo='Documento recibido para validación SENA',
                mensaje='Tu documento fue cargado correctamente. El administrador revisará la evidencia y aprobará tu cuenta si coincide.',
            )
            _notificar_staff(
                tipo='staff_documento_validacion_sena',
                titulo='Documento recibido para validación SENA',
                mensaje=f'Se recibió un documento manual de {usuario.nombre or usuario.correo} para validación de identidad SENA.',
            )
            messages.success(request, 'Tu evidencia fue cargada correctamente. Ahora queda pendiente de revisión administrativa.')
            return redirect('login')

    return render(request, 'inventario/login/validacion_sena_manual.html', {
        'token_valido': token_valido,
        'usuario_objetivo': usuario,
        'carga_exitosa': carga_exitosa,
    })

@login_required
def usuario_eliminar_carrito(request, prod_id):
    eliminado, _ = CarritoItem.objects.filter(id_usuario_fk=request.user, id_prod_fk_id=prod_id).delete()
    if eliminado:
        messages.success(request, 'Producto eliminado del carrito.')
    return redirect('carrito_usuario')


@login_required
@require_POST
def usuario_actualizar_cantidad_carrito(request, prod_id):
    if not _usuario_cliente(request):
        return redirect('dashboard')

    item = CarritoItem.objects.filter(id_usuario_fk=request.user, id_prod_fk_id=prod_id).first()
    if not item:
        messages.error(request, 'No se encontró el producto en tu carrito.')
        return redirect('carrito_usuario')

    try:
        cantidad = int(request.POST.get('cantidad', item.cantidad))
    except (TypeError, ValueError):
        cantidad = item.cantidad

    cantidad = max(0, cantidad)
    if cantidad > 999:
        cantidad = 999

    item.cantidad = cantidad
    item.fch_ult_act = timezone.now()
    item.save(update_fields=['cantidad', 'fch_ult_act'])

    return redirect('carrito_usuario')


@login_required
@require_POST
def usuario_realizar_pedido(request):
    if not _usuario_cliente(request):
        return redirect('dashboard')

    context = _build_carrito_context(request)
    carrito_items = context['carrito_items_pedido']

    if not carrito_items:
        messages.error(request, 'No hay productos en el carrito para generar un pedido.')
        return redirect('carrito_usuario')

    if not context['carrito_valido']:
        messages.error(request, 'Revisa las cantidades del carrito antes de realizar el pedido.')
        return redirect('carrito_usuario')

    if not _usuario_tiene_validacion_sena(request.user):
        messages.error(request, 'Valida tu información de carnet SENA para continuar.')
        return redirect(f"{reverse('validacion_sena')}?next={reverse('carrito_usuario')}")

    # --- Datos del préstamo ---
    area_ubicacion = request.POST.get('area_ubicacion', '').strip()
    tipo_devolucion = request.POST.get('tipo_devolucion', '').strip()

    solo_consumo = bool(carrito_items) and all(
        (getattr(item['producto'], 'tipo_bien', 'devolutivo') == 'consumo')
        for item in carrito_items
    )

    if not area_ubicacion:
        messages.error(request, 'Debes indicar el área o ambiente donde se usarán los productos.')
        return redirect('carrito_usuario')

    now_tz = timezone.localtime()
    fecha_devolucion_global = None

    if solo_consumo:
        tipo_devolucion = 'consumo'
        fecha_devolucion_global = None
    else:
        if tipo_devolucion not in ('mismo_dia', 'por_dias'):
            messages.error(request, 'Debes seleccionar una opción de devolución (mismo día o por días).')
            return redirect('carrito_usuario')

        # Construir fecha_devolucion según el tipo elegido
        if tipo_devolucion == 'mismo_dia':
            hora_str = request.POST.get('hora_devolucion', '').strip()
            if not hora_str:
                messages.error(request, 'Debes indicar la hora de devolución para el mismo día.')
                return redirect('carrito_usuario')
            try:
                h, m = [int(x) for x in hora_str.split(':')[:2]]
                fecha_devolucion_global = now_tz.replace(hour=h, minute=m, second=0, microsecond=0)
            except (ValueError, TypeError):
                messages.error(request, 'Hora de devolución inválida.')
                return redirect('carrito_usuario')

            if fecha_devolucion_global <= now_tz:
                messages.error(request, 'La hora de devolución debe ser posterior a la hora actual.')
                return redirect('carrito_usuario')

        else:  # por_dias
            fecha_str = request.POST.get('fecha_devolucion_dias', '').strip()
            if not fecha_str:
                messages.error(request, 'Debes seleccionar el día de devolución.')
                return redirect('carrito_usuario')
            try:
                from datetime import date as _date
                d = _date.fromisoformat(fecha_str)
                from datetime import datetime as _dt
                fecha_devolucion_global = timezone.make_aware(
                    _dt(d.year, d.month, d.day, 17, 0, 0)
                )
            except (ValueError, TypeError):
                messages.error(request, 'Fecha de devolución inválida.')
                return redirect('carrito_usuario')

            if fecha_devolucion_global <= now_tz:
                messages.error(request, 'La fecha de devolución debe ser en el futuro.')
                return redirect('carrito_usuario')

    now = timezone.now()
    with transaction.atomic():
        pedido = Pedido.objects.create(
            id_usuario_fk=request.user,
            estado='pendiente',
            total_productos=context['total_productos'],
            total_unidades=context['total_unidades'],
            area_ubicacion=area_ubicacion,
            tipo_devolucion=tipo_devolucion,
            fecha_devolucion=fecha_devolucion_global,
            fch_registro=now,
            fch_ult_act=now,
        )

        detalles = []
        for item in carrito_items:
            producto = item['producto']
            detalles.append(
                DetallePedido(
                    id_pedido_fk=pedido,
                    id_prod_fk=producto,
                    nombre_producto=producto.nombre_producto or f'Producto {producto.id_prod}',
                    nombre_catalogo=producto.id_cat_fk.nombre_catalogo if producto.id_cat_fk else None,
                    cantidad_solicitada=item['cantidad'],
                    stock_referencia=producto.stock_actual or 0,
                    estado_detalle='pendiente',
                    fecha_devolucion=fecha_devolucion_global,
                    fch_registro=now,
                    fch_ult_act=now,
                )
            )
        DetallePedido.objects.bulk_create(detalles)

    CarritoItem.objects.filter(id_usuario_fk=request.user).delete()
    _registrar_auditoria(
        request,
        accion='crear',
        entidad='pedido',
        entidad_id=pedido.id_pedido,
        descripcion=f'Usuario creó el pedido #{pedido.id_pedido}.',
    )
    _crear_notificacion(
        usuario=request.user,
        tipo='pedido_creado',
        titulo='Pedido recibido',
        mensaje=f'Tu pedido #{pedido.id_pedido} fue enviado correctamente y está siendo revisado por el almacenista. '
                f'Te notificaremos cuando cambie de estado.',
        pedido_id=pedido.id_pedido,
    )
    _notificar_staff(
        tipo='staff_nuevo_pedido',
        titulo=f'Nuevo pedido #{pedido.id_pedido} recibido',
        mensaje=(
            f'{request.user.nombre or ""} {request.user.apellido or ""}'.strip() or request.user.correo
        ) + f' acaba de enviar el pedido #{pedido.id_pedido} con '
            f'{pedido.total_productos} producto{"s" if pedido.total_productos != 1 else ""} '
            f'({pedido.total_unidades} unidad{"es" if pedido.total_unidades != 1 else ""}). '
            f'Área: {pedido.area_ubicacion}.',
        pedido_id=pedido.id_pedido,
    )
    # ── Correo de confirmación al usuario ───────────────────────────────
    try:
        from django.core.mail import EmailMultiAlternatives
        from django.conf import settings as _settings
        correo_dest = getattr(request.user, 'correo', None) or getattr(request.user, 'email', None)
        if correo_dest:
            nombre = getattr(request.user, 'nombre', '') or str(request.user)
            fecha_str = pedido.fecha_devolucion.strftime('%d/%m/%Y a las %H:%M') if pedido.fecha_devolucion else 'Sin fecha definida'
            base_url = 'https://almacensedelacolonia.pythonanywhere.com'
            filas_html = ''
            lista_txt = ''
            for d in detalles:
                prod = getattr(d, 'id_prod_fk', None)
                img_url = f'{base_url}{_settings.MEDIA_URL}{prod.fot_prod}' if prod and prod.fot_prod else ''
                img_tag = (f'<img src="{img_url}" width="44" height="44" style="border-radius:6px;object-fit:cover;">'
                           if img_url else '<div style="width:44px;height:44px;background:#e8f5e9;border-radius:6px;display:inline-block;">📦</div>')
                filas_html += f'<tr><td style="padding:10px 12px;border-bottom:1px solid #f0f0f0;width:60px;">{img_tag}</td><td style="padding:10px 12px;border-bottom:1px solid #f0f0f0;font-size:14px;color:#333;">{d.nombre_producto}</td><td style="padding:10px 12px;border-bottom:1px solid #f0f0f0;font-size:14px;color:#555;text-align:center;">x{d.cantidad_solicitada}</td></tr>'
                lista_txt += f'  - {d.nombre_producto} x{d.cantidad_solicitada}\n'
            tabla = f'<p style="font-size:15px;font-weight:700;color:#1a2e1a;margin:20px 0 8px;">🛒 Productos solicitados:</p><table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e0e0e0;border-radius:8px;overflow:hidden;"><thead><tr style="background:#f5f5f5;"><th style="padding:10px 12px;text-align:left;font-size:13px;color:#666;width:60px;">Foto</th><th style="padding:10px 12px;text-align:left;font-size:13px;color:#666;">Producto</th><th style="padding:10px 12px;text-align:center;font-size:13px;color:#666;">Cant.</th></tr></thead><tbody>{filas_html}</tbody></table>' if filas_html else ''
            asunto = f'✅ Pedido #{pedido.id_pedido} recibido | Almacén SENA Sibaté'
            txt = f'Hola {nombre},\n\nTu pedido #{pedido.id_pedido} fue enviado correctamente y está siendo revisado por el almacenista.\n\nProductos solicitados:\n{lista_txt}\nFecha de devolución: {fecha_str}\n\nTe notificaremos cuando tu pedido esté listo para recoger.\n\n— Almacén SENA Sibaté'
            html = f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f4f4f4;font-family:Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f4;padding:32px 0;">
<tr><td align="center"><table width="600" cellpadding="0" cellspacing="0"
  style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:600px;width:100%;">
<tr><td style="background:#39A900;padding:28px 32px;text-align:center;">
  <p style="margin:0;color:#fff;font-size:13px;opacity:0.85;">SENA — Almacén Sibaté</p>
  <h1 style="margin:8px 0 0;color:#fff;font-size:24px;">✅ Pedido recibido</h1>
</td></tr>
<tr><td style="padding:32px;">
  <p style="font-size:16px;color:#333;">Hola <strong>{nombre}</strong>,</p>
  <p style="font-size:15px;color:#444;line-height:1.6;">Tu pedido <strong>#{pedido.id_pedido}</strong> fue recibido correctamente y está siendo revisado por el almacenista.</p>
  {tabla}
  <table width="100%" cellpadding="0" cellspacing="0" style="margin:20px 0;"><tr>
    <td style="background:#e8f5e9;border-left:4px solid #39A900;border-radius:6px;padding:14px 18px;">
      <p style="margin:0;font-size:14px;color:#333;">📅 Fecha de devolución: <strong>{fecha_str}</strong></p>
    </td>
  </tr></table>
  <p style="font-size:14px;color:#555;">Te notificaremos cuando tu pedido esté <strong>listo para recoger</strong> en el almacén.</p>
  <p style="font-size:13px;color:#888;margin-top:28px;">— Almacén SENA Sibaté</p>
</td></tr>
<tr><td style="background:#f9f9f9;padding:14px 32px;text-align:center;border-top:1px solid #eee;">
  <p style="margin:0;font-size:12px;color:#aaa;">Centro Industrial y de Desarrollo Empresarial – Sibaté, Cundinamarca</p>
</td></tr>
</table></td></tr></table>
</body></html>"""
            msg = EmailMultiAlternatives(asunto, txt, _settings.DEFAULT_FROM_EMAIL, [correo_dest])
            msg.attach_alternative(html, 'text/html')
            msg.send()
    except Exception:
        pass  # No bloquear el flujo si el correo falla

    messages.success(request, f'Pedido #{pedido.id_pedido} enviado correctamente.')
    return redirect('carrito_usuario')


@login_required
def pedidos_usuario(request):
    if not _usuario_cliente(request):
        return redirect('dashboard')

    _auto_cancelar_pedidos_pendientes_vencidos()

    pedidos = list(
        Pedido.objects
        .filter(id_usuario_fk=request.user)
        .prefetch_related('detalles__id_prod_fk', 'evidencias')
        .order_by('-fch_registro', '-id_pedido')
    )
    ahora = timezone.now()
    VENTANA_CANCELACION = timedelta(minutes=10)

    for pedido in pedidos:
        if pedido.estado == 'esperando entrega':
            codigo_vigente = bool(
                pedido.codigo_entrega
                and pedido.codigo_expira_en
                and pedido.codigo_expira_en >= ahora
            )
            if not codigo_vigente:
                pedido.codigo_entrega = f'{secrets.randbelow(1000000):06d}'
                pedido.codigo_expira_en = ahora + timedelta(hours=2)
                pedido.fch_ult_act = ahora
                pedido.save(update_fields=['codigo_entrega', 'codigo_expira_en', 'fch_ult_act'])
                pedido.codigo_vigente = True
            else:
                pedido.codigo_vigente = True
            pedido.devolucion_codigo = None
            pedido.devolucion_segundos = 0
            pedido.devolucion_expira_en = None
        elif pedido.estado in ('entregado', 'vencido'):
            _asegurar_codigo_devolucion(pedido, ahora)
            pedido.codigo_vigente = False
            pedido.devolucion_codigo = pedido.codigo_entrega
            pedido.devolucion_expira_en = pedido.codigo_expira_en
            if pedido.codigo_expira_en:
                pedido.devolucion_segundos = max(int((pedido.codigo_expira_en - ahora).total_seconds()), 0)
            else:
                pedido.devolucion_segundos = 0
        else:
            pedido.codigo_vigente = False
            pedido.devolucion_codigo = None
            pedido.devolucion_segundos = 0
            pedido.devolucion_expira_en = None

        # Ventana de 10 min para cancelar (solo pedidos pendientes con fch_registro válida)
        if pedido.estado == 'pendiente' and pedido.fch_registro:
            expira_cancelacion = pedido.fch_registro + VENTANA_CANCELACION
            segundos = int((expira_cancelacion - ahora).total_seconds())
            pedido.puede_cancelar = segundos > 0
            pedido.segundos_cancelacion = max(segundos, 0)
        else:
            pedido.puede_cancelar = False
            pedido.segundos_cancelacion = 0

        # ¿Está vencido? (entregado o marcado como vencido, con fecha de devolución pasada)
        pedido.esta_vencido = (
            pedido.estado in ('entregado', 'vencido')
            and pedido.fecha_devolucion is not None
            and pedido.fecha_devolucion < ahora
        ) or pedido.estado == 'vencido'

    # Marcar como vistos: guardar IDs de pedidos activos en sesión para el badge de nav
    activos_ids = [p.id_pedido for p in pedidos if p.estado in ('pendiente', 'esperando entrega')]
    request.session['pedidos_u_visto_ids'] = activos_ids

    estado_activo = (request.GET.get('estado') or 'todos').strip().lower()
    estados_validos = {'todos', 'pendiente', 'esperando-entrega', 'entregado', 'vencido', 'devuelto', 'rechazado', 'cancelado'}
    if estado_activo not in estados_validos:
        estado_activo = 'todos'

    filtro_estado_real = {
        'pendiente': 'pendiente',
        'esperando-entrega': 'esperando entrega',
        'entregado': 'entregado',
        'vencido': 'vencido',
        'devuelto': 'devuelto',
        'rechazado': 'rechazado',
        'cancelado': 'cancelado',
    }.get(estado_activo)

    pedidos_filtrados = pedidos
    if filtro_estado_real:
        pedidos_filtrados = [pedido for pedido in pedidos if pedido.estado == filtro_estado_real]

    conteos_estado = {
        'todos': len(pedidos),
        'pendiente': sum(1 for pedido in pedidos if pedido.estado == 'pendiente'),
        'esperando_entrega': sum(1 for pedido in pedidos if pedido.estado == 'esperando entrega'),
        'entregado': sum(1 for pedido in pedidos if pedido.estado == 'entregado'),
        'vencido': sum(1 for pedido in pedidos if pedido.estado == 'vencido'),
        'devuelto': sum(1 for pedido in pedidos if pedido.estado == 'devuelto'),
        'rechazado': sum(1 for pedido in pedidos if pedido.estado == 'rechazado'),
        'cancelado': sum(1 for pedido in pedidos if pedido.estado == 'cancelado'),
    }

    return render(request, 'inventario/usuario/pedidos_usuario.html', {
        'pedidos': pedidos_filtrados,
        'estado_activo': estado_activo,
        'conteos_estado': conteos_estado,
        'ahora': ahora,
    })


@login_required
@require_POST
def pedido_cancelar_usuario(request, pedido_id):
    if not _usuario_cliente(request):
        return redirect('dashboard')

    with transaction.atomic():
        pedido = get_object_or_404(
            Pedido.objects.select_for_update(),
            pk=pedido_id,
            id_usuario_fk=request.user,
        )

        if pedido.estado != 'pendiente':
            messages.error(request, 'Solo puedes cancelar pedidos en estado pendiente.')
            return redirect('pedidos_usuario')

        if not pedido.fch_registro:
            messages.error(request, 'No se pudo verificar la ventana de cancelación.')
            return redirect('pedidos_usuario')

        ahora = timezone.now()
        expira = pedido.fch_registro + timedelta(minutes=10)
        if ahora > expira:
            messages.error(request, 'El plazo de 10 minutos para cancelar este pedido ha vencido.')
            return redirect('pedidos_usuario')

        now = timezone.now()
        pedido.estado = 'cancelado'
        pedido.fch_ult_act = now
        pedido.save(update_fields=['estado', 'fch_ult_act'])

        DetallePedido.objects.filter(id_pedido_fk=pedido).update(
            estado_detalle='cancelado',
            fch_ult_act=now,
        )

    _registrar_auditoria(
        request,
        accion='actualizar',
        entidad='pedido',
        entidad_id=pedido.id_pedido,
        descripcion=f'Pedido #{pedido.id_pedido} cancelado por el usuario en su panel.',
    )
    _crear_notificacion(
        usuario=request.user,
        tipo='rechazado',
        titulo='Pedido cancelado por ti',
        mensaje=f'Cancelaste tu pedido #{pedido.id_pedido}. Si fue un error, deberás crear un nuevo pedido.',
        pedido_id=pedido.id_pedido,
    )
    _notificar_staff(
        tipo='staff_pedido_cancelado',
        titulo=f'Pedido #{pedido.id_pedido} cancelado por el usuario',
        mensaje=(
            f'{request.user.nombre or ""} {request.user.apellido or ""}'.strip() or request.user.correo
        ) + f' canceló su pedido #{pedido.id_pedido}. Ya no es necesario prepararlo.',
        pedido_id=pedido.id_pedido,
    )
    messages.success(request, f'Pedido #{pedido.id_pedido} cancelado correctamente.')
    return redirect('pedidos_usuario')


@login_required
def pedido_codigo_devolucion(request, pedido_id):
    if not _usuario_cliente(request):
        return JsonResponse({'ok': False, 'error': 'No autorizado.'}, status=403)

    if request.method != 'GET':
        return JsonResponse({'ok': False, 'error': 'Método no permitido.'}, status=405)

    with transaction.atomic():
        pedido = get_object_or_404(
            Pedido.objects.select_for_update(),
            pk=pedido_id,
            id_usuario_fk=request.user,
        )

        if pedido.estado not in ('entregado', 'vencido'):
            return JsonResponse({'ok': False, 'error': 'Este pedido no está en estado entregado.'}, status=400)

        now = timezone.now()
        _asegurar_codigo_devolucion(pedido, now)
        segundos = max(int((pedido.codigo_expira_en - now).total_seconds()), 0)

    return JsonResponse({
        'ok': True,
        'codigo': pedido.codigo_entrega,
        'segundos': segundos,
        'server_now': now.isoformat(),
        'expira_en': pedido.codigo_expira_en.isoformat() if pedido.codigo_expira_en else None,
    })


@login_required
def panel_usuario(request):
    # Solo usuarios, aprendices e instructores
    if not _usuario_cliente(request):
        return redirect('dashboard')

    disp_qs = Disponibilidad.objects.filter(id_prod_fk=OuterRef('pk')).order_by('-id_disp')
    productos_qs = (
        Producto.objects
        .select_related('id_cat_fk')
        .prefetch_related('fotos', 'subcategorias')
        .annotate(stock_actual=Subquery(disp_qs.values('cantidad')[:1]))
    )

    q = request.GET.get('q', '').strip()
    if q:
        from django.db.models import Q
        productos_qs = productos_qs.filter(
            Q(nombre_producto__icontains=q) | Q(descripcion__icontains=q)
        )

    cat_id = request.GET.get('cat', '').strip()
    sub_id = request.GET.get('sub', '').strip()

    catalogos = list(Catalogo.objects.order_by('nombre_catalogo'))
    subcategorias = list(
        Subcategoria.objects
        .select_related('id_cat_fk', 'subcategoria_padre')
        .order_by('id_cat_fk_id', 'subcategoria_padre_id', 'nombre_subcategoria')
    )

    cat_sel = None
    sub_sel = None

    if cat_id.isdigit():
        cat_sel = next((c for c in catalogos if c.id_cat == int(cat_id)), None)
        if cat_sel:
            productos_qs = productos_qs.filter(id_cat_fk=cat_sel)

    if sub_id.isdigit():
        sub_sel = next((s for s in subcategorias if s.id_subcat == int(sub_id)), None)
        if sub_sel:
            # Si llega subcat sin cat, inferir catálogo.
            if not cat_sel:
                cat_sel = sub_sel.id_cat_fk
                productos_qs = productos_qs.filter(id_cat_fk=cat_sel)
            productos_qs = productos_qs.filter(subcategorias=sub_sel)

    productos = list(productos_qs.order_by('nombre_producto').distinct())

    for producto in productos:
        rutas_sub = sorted(
            [sub.ruta_completa for sub in producto.subcategorias.all() if getattr(sub, 'ruta_completa', None)]
        )
        if rutas_sub:
            producto.trazabilidad_busqueda = f"{producto.id_cat_fk.nombre_catalogo} / " + " / ".join(rutas_sub)
        else:
            producto.trazabilidad_busqueda = producto.id_cat_fk.nombre_catalogo

    subcats_by_cat = {}
    menu_catalogos = []
    for cat in catalogos:
        cat_subs = [s for s in subcategorias if s.id_cat_fk_id == cat.id_cat]
        padres = [s for s in cat_subs if s.subcategoria_padre_id is None]
        hijos_map = {}
        columnas = []
        for p in padres:
            hijos = [h for h in cat_subs if h.subcategoria_padre_id == p.id_subcat]
            hijos_map[p.id_subcat] = hijos
            columnas.append({
                'padre': p,
                'hijas': hijos,
            })
        subcats_by_cat[cat.id_cat] = {
            'padres': padres,
            'hijos_map': hijos_map,
        }
        menu_catalogos.append({
            'catalogo': cat,
            'columnas': columnas,
        })

    breadcrumb = [
        {'label': 'Inicio', 'url': reverse('panel_usuario')},
        {'label': 'Inventario', 'url': reverse('panel_usuario')},
    ]
    resultado_pertenece = ''
    if cat_sel:
        breadcrumb.append({
            'label': cat_sel.nombre_catalogo,
            'url': f"{reverse('panel_usuario')}?cat={cat_sel.id_cat}",
        })
    if sub_sel:
        ruta = []
        node = sub_sel
        while node:
            ruta.append(node)
            node = node.subcategoria_padre
        for i, node in enumerate(reversed(ruta)):
            if i == len(ruta) - 1:
                breadcrumb.append({'label': node.nombre_subcategoria, 'url': None})
            else:
                breadcrumb.append({
                    'label': node.nombre_subcategoria,
                    'url': f"{reverse('panel_usuario')}?cat={cat_sel.id_cat}&sub={node.id_subcat}",
                })

    if q:
        breadcrumb.append({
            'label': f'Resultados: "{q}"',
            'url': None,
        })

        if sub_sel:
            madre = sub_sel
            while madre and madre.subcategoria_padre:
                madre = madre.subcategoria_padre
            if madre:
                resultado_pertenece = f'Subcategoría madre: {madre.nombre_subcategoria}'
        else:
            categorias = sorted({
                (p.id_cat_fk.nombre_catalogo or '').strip()
                for p in productos
                if getattr(p, 'id_cat_fk', None)
            })
            categorias = [c for c in categorias if c]
            if categorias:
                max_items = 8
                resumen = ' / '.join(categorias[:max_items])
                if len(categorias) > max_items:
                    resumen += ' / ...'
                resultado_pertenece = f'Pertenece a: {resumen}'

    return render(request, 'inventario/usuario/panel_usuario.html', {
        'productos': productos,
        'catalogos': catalogos,
        'menu_catalogos': menu_catalogos,
        'subcats_by_cat': subcats_by_cat,
        'cat_sel': cat_sel,
        'sub_sel': sub_sel,
        'breadcrumb': breadcrumb,
        'resultado_pertenece': resultado_pertenece,
    })

@login_required
def producto_detalle_usuario(request, prod_id):
    if not _usuario_cliente(request):
        return redirect('dashboard')
    producto = get_object_or_404(Producto.objects.prefetch_related('subcategorias'), pk=prod_id)
    disp = (
        Disponibilidad.objects
        .filter(id_prod_fk=producto)
        .order_by('-id_disp')
        .first()
    )
    producto.stock_actual = (disp.cantidad if disp and disp.cantidad is not None else (disp.stock if disp else 0))
    # Sugerencias: productos de la misma categoría, excluyendo el actual, máximo 6 aleatorios
    sugerencias = (
        Producto.objects
        .filter(id_cat_fk=producto.id_cat_fk)
        .exclude(id_prod=producto.id_prod)
        .order_by('?')[:6]
    )

    cat_id = request.GET.get('cat', '').strip()
    sub_id = request.GET.get('sub', '').strip()
    q = request.GET.get('q', '').strip()

    cat_sel = None
    sub_sel = None
    if cat_id.isdigit():
        cat_sel = Catalogo.objects.filter(pk=int(cat_id)).first()
    if sub_id.isdigit():
        sub_sel = Subcategoria.objects.select_related('subcategoria_padre').filter(pk=int(sub_id)).first()

    if not cat_sel:
        cat_sel = producto.id_cat_fk

    panel_url = reverse('panel_usuario')
    panel_qs = []
    if cat_sel:
        panel_qs.append(f'cat={cat_sel.id_cat}')
    if sub_sel:
        panel_qs.append(f'sub={sub_sel.id_subcat}')
    if q:
        panel_qs.append(f'q={q}')
    panel_url_ctx = f"{panel_url}?{'&'.join(panel_qs)}" if panel_qs else panel_url

    breadcrumb = [
        {'label': 'Inicio', 'url': reverse('panel_usuario')},
        {'label': 'Inventario', 'url': panel_url_ctx},
    ]

    if cat_sel:
        breadcrumb.append({
            'label': cat_sel.nombre_catalogo,
            'url': f"{reverse('panel_usuario')}?cat={cat_sel.id_cat}{f'&q={q}' if q else ''}",
        })

    if sub_sel:
        ruta = []
        nodo = sub_sel
        while nodo:
            ruta.append(nodo)
            nodo = nodo.subcategoria_padre
        for node in reversed(ruta):
            breadcrumb.append({
                'label': node.nombre_subcategoria,
                'url': f"{reverse('panel_usuario')}?cat={cat_sel.id_cat}&sub={node.id_subcat}{f'&q={q}' if q else ''}",
            })

    breadcrumb.append({'label': producto.nombre_producto or f'Producto {producto.id_prod}', 'url': None})

    return render(request, 'inventario/usuario/producto_detalle_usuario.html', {
        'producto': producto,
        'sugerencias': sugerencias,
        'panel_url_ctx': panel_url_ctx,
        'breadcrumb': breadcrumb,
    })


MAX_EXTENSIONES = 3
DIAS_EXTENSION = 3   # días que se agrega cada vez que el usuario extiende


@login_required
@require_POST
def pedido_extender_plazo(request, pedido_id):
    """El usuario solicita extender el plazo de devolución (máx. 3 veces, +3 días c/u)."""
    if not _usuario_cliente(request):
        return redirect('dashboard')

    with transaction.atomic():
        pedido = get_object_or_404(
            Pedido.objects.select_for_update(),
            pk=pedido_id,
            id_usuario_fk=request.user,
        )

        if pedido.estado not in ('entregado', 'vencido'):
            messages.error(request, 'Solo puedes extender el plazo de pedidos actualmente entregados.')
            return redirect('pedidos_usuario')

        if pedido.extensiones_plazo >= MAX_EXTENSIONES:
            messages.error(
                request,
                f'Ya usaste los {MAX_EXTENSIONES} plazos disponibles. '
                'Debes devolver los productos a la brevedad posible.'
            )
            return redirect('pedidos_usuario')

        ahora = timezone.now()
        # Si fecha_devolucion ya pasó, extendemos desde ahora; si aún no, desde la fecha original
        base = pedido.fecha_devolucion if pedido.fecha_devolucion and pedido.fecha_devolucion > ahora else ahora
        nueva_fecha = base + timedelta(days=DIAS_EXTENSION)

        pedido.fecha_devolucion = nueva_fecha
        pedido.extensiones_plazo += 1
        pedido.notif_vencimiento_enviada = False   # permitir re-notificar si vuelve a vencer
        pedido.estado = 'entregado'  # reactivar si estaba vencido
        pedido.fch_ult_act = ahora
        pedido.save(update_fields=['fecha_devolucion', 'extensiones_plazo', 'notif_vencimiento_enviada', 'estado', 'fch_ult_act'])

    extensiones_restantes = MAX_EXTENSIONES - pedido.extensiones_plazo
    _crear_notificacion(
        usuario=request.user,
        tipo='aviso_devolucion',
        titulo='Plazo de devolución extendido',
        mensaje=(
            f'Extendiste el plazo del pedido #{pedido.id_pedido}. '
            f'Nueva fecha límite: {nueva_fecha.strftime("%d/%m/%Y %H:%M")}. '
            + (
                f'Te queda{"n" if extensiones_restantes != 1 else ""} '
                f'{extensiones_restantes} extensión{"es" if extensiones_restantes != 1 else ""} disponible{"s" if extensiones_restantes != 1 else ""}.'
                if extensiones_restantes > 0
                else 'No tienes más extensiones disponibles. Debes devolver los productos.'
            )
        ),
        pedido_id=pedido.id_pedido,
    )
    _notificar_staff(
        tipo='aviso_devolucion',
        titulo=f'Pedido #{pedido.id_pedido} – plazo extendido',
        mensaje=(
            f'{request.user.nombre or ""} {request.user.apellido or ""}'.strip() or request.user.correo
        ) + (
            f' extendió el plazo del pedido #{pedido.id_pedido} '
            f'(extensión {pedido.extensiones_plazo}/{MAX_EXTENSIONES}). '
            f'Nueva fecha: {nueva_fecha.strftime("%d/%m/%Y %H:%M")}.'
        ),
        pedido_id=pedido.id_pedido,
    )
    messages.success(
        request,
        f'Plazo extendido hasta el {nueva_fecha.strftime("%d/%m/%Y")}. '
        + (
            f'Te quedan {extensiones_restantes} extensión{"es" if extensiones_restantes != 1 else ""} disponible{"s" if extensiones_restantes != 1 else ""}.'
            if extensiones_restantes > 0
            else 'Esta fue tu última extensión. Debes devolver los productos en la nueva fecha.'
        )
    )
    return redirect('pedidos_usuario')

@login_required
def usuario_agregar_carrito(request, prod_id):
    if request.method == 'POST':
        try:
            cantidad = int(request.POST.get('cantidad', 1))
        except (TypeError, ValueError):
            cantidad = 1
        cantidad = max(cantidad, 1)

        producto = get_object_or_404(Producto, pk=prod_id)
        now = timezone.now()

        item, created = CarritoItem.objects.get_or_create(
            id_usuario_fk=request.user,
            id_prod_fk=producto,
            defaults={
                'cantidad': cantidad,
                'fch_registro': now,
                'fch_ult_act': now,
            },
        )
        if not created:
            item.cantidad += cantidad
            item.fch_ult_act = now
            item.save(update_fields=['cantidad', 'fch_ult_act'])

        messages.success(request, 'Producto agregado al carrito.')
    return redirect('panel_usuario')


