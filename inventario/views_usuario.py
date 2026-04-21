from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.db.models import OuterRef, Subquery
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_POST
from datetime import timedelta
import secrets

from .models import CarritoItem, DetallePedido, Disponibilidad, Notificacion, Pedido, Producto
from .views import _auto_cancelar_pedidos_pendientes_vencidos, _crear_notificacion, _notificar_staff, _registrar_auditoria


DEVOLUCION_CODIGO_SEGUNDOS = 60


def _usuario_cliente(request):
    if not request.user.is_authenticated:
        return False
    if getattr(request.user, 'is_superuser', False) or getattr(request.user, 'is_staff', False):
        return False

    rol = (getattr(getattr(request.user, 'id_rol_fk', None), 'nombre_rol', '') or '').strip().lower()
    return rol in ['', 'usuario', 'aprendiz', 'instructor']


def _asegurar_codigo_devolucion(pedido, now):
    if pedido.estado != 'entregado':
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

        total_unidades += cantidad
        if producto.stock_actual and producto.stock_actual > 0:
            productos_disponibles += 1
        else:
            productos_sin_stock += 1

        carrito_items.append({
            'producto': producto,
            'cantidad': cantidad,
            'supera_stock': supera_stock,
        })

    carrito_valido = bool(carrito_items) and all(
        item['cantidad'] > 0 and not item['supera_stock'] and (item['producto'].stock_actual or 0) > 0
        for item in carrito_items
    )

    return {
        'carrito_items': carrito_items,
        'total_productos': len(carrito_items),
        'total_unidades': total_unidades,
        'productos_disponibles': productos_disponibles,
        'productos_sin_stock': productos_sin_stock,
        'carrito_valido': carrito_valido,
    }


@login_required
def carrito_usuario(request):
    if not _usuario_cliente(request):
        return redirect('dashboard')
    return render(request, 'inventario/usuario/carrito_usuario.html', _build_carrito_context(request))

@login_required
def usuario_eliminar_carrito(request, prod_id):
    eliminado, _ = CarritoItem.objects.filter(id_usuario_fk=request.user, id_prod_fk_id=prod_id).delete()
    if eliminado:
        messages.success(request, 'Producto eliminado del carrito.')
    return redirect('carrito_usuario')


@login_required
@require_POST
def usuario_realizar_pedido(request):
    if not _usuario_cliente(request):
        return redirect('dashboard')

    context = _build_carrito_context(request)
    carrito_items = context['carrito_items']

    if not carrito_items:
        messages.error(request, 'No hay productos en el carrito para generar un pedido.')
        return redirect('carrito_usuario')

    if not context['carrito_valido']:
        messages.error(request, 'Revisa las cantidades del carrito antes de realizar el pedido.')
        return redirect('carrito_usuario')

    # --- Datos del préstamo ---
    area_ubicacion = request.POST.get('area_ubicacion', '').strip()
    tipo_devolucion = request.POST.get('tipo_devolucion', '').strip()
    foto_carnet = request.FILES.get('foto_carnet')

    if not area_ubicacion:
        messages.error(request, 'Debes indicar el área o ambiente donde se usarán los productos.')
        return redirect('carrito_usuario')

    if not foto_carnet:
        messages.error(request, 'Debes subir la foto de tu carnet institucional SENA.')
        return redirect('carrito_usuario')

    if tipo_devolucion not in ('mismo_dia', 'por_dias'):
        messages.error(request, 'Debes seleccionar una opción de devolución (mismo día o por días).')
        return redirect('carrito_usuario')

    # Construir fecha_devolucion según el tipo elegido
    now_tz = timezone.localtime()
    fecha_devolucion_global = None

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
            foto_carnet=foto_carnet,
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
        elif pedido.estado == 'entregado':
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

        # ¿Está vencido? (entregado, con fecha de devolución pasada, no devuelto aún)
        pedido.esta_vencido = (
            pedido.estado == 'entregado'
            and pedido.fecha_devolucion is not None
            and pedido.fecha_devolucion < ahora
        )

    estado_activo = (request.GET.get('estado') or 'todos').strip().lower()
    estados_validos = {'todos', 'pendiente', 'esperando-entrega', 'entregado', 'devuelto', 'rechazado', 'cancelado'}
    if estado_activo not in estados_validos:
        estado_activo = 'todos'

    filtro_estado_real = {
        'pendiente': 'pendiente',
        'esperando-entrega': 'esperando entrega',
        'entregado': 'entregado',
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

        if pedido.estado != 'entregado':
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
    productos_qs = Producto.objects.select_related('id_cat_fk').annotate(stock_actual=Subquery(disp_qs.values('cantidad')[:1]))
    q = request.GET.get('q', '').strip()
    if q:
        from django.db.models import Q
        productos_qs = productos_qs.filter(
            Q(nombre_producto__icontains=q) | Q(descripcion__icontains=q)
        )
    productos = productos_qs.order_by('nombre_producto')
    return render(request, 'inventario/usuario/panel_usuario.html', {'productos': productos})

@login_required
def producto_detalle_usuario(request, prod_id):
    if not _usuario_cliente(request):
        return redirect('dashboard')
    producto = get_object_or_404(Producto, pk=prod_id)
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
    return render(request, 'inventario/usuario/producto_detalle_usuario.html', {
        'producto': producto,
        'sugerencias': sugerencias,
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

        if pedido.estado != 'entregado':
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
        pedido.fch_ult_act = ahora
        pedido.save(update_fields=['fecha_devolucion', 'extensiones_plazo', 'notif_vencimiento_enviada', 'fch_ult_act'])

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
