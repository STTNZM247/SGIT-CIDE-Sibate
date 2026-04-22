import csv
import io
import os
import secrets
import textwrap
from collections import defaultdict
from datetime import date, timedelta

from django.conf import settings
from django.http import Http404, HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from .models import AuditoriaLog, Catalogo, DetallePedido, Disponibilidad, Notificacion, Pedido, PedidoEvidencia, Producto, Rol, Usuario
from .forms import ProductoForm


DEVOLUCION_CODIGO_SEGUNDOS = 60


def _crear_notificacion(usuario, tipo, titulo, mensaje, pedido_id=None):
    """Crea una notificación para el usuario de forma segura (nunca lanza excepción)."""
    try:
        Notificacion.objects.create(
            id_usuario_fk=usuario,
            tipo=tipo,
            titulo=titulo,
            mensaje=mensaje,
            id_pedido_ref=pedido_id,
        )
    except Exception:
        pass


def _notificar_staff(tipo, titulo, mensaje, pedido_id=None):
    """Envía una notificación a todos los usuarios con rol admin o almacenista."""
    try:
        from .models import Usuario as _Usuario
        staff = _Usuario.objects.filter(
            id_rol_fk__nombre_rol__in=['admin', 'almacenista'],
            is_active=True,
        )
        Notificacion.objects.bulk_create([
            Notificacion(
                id_usuario_fk=u,
                tipo=tipo,
                titulo=titulo,
                mensaje=mensaje,
                id_pedido_ref=pedido_id,
            )
            for u in staff
        ])
    except Exception:
        pass


def _tiempo_vencido(fecha_devolucion, ahora):
    """Devuelve texto humanizado de cuánto tiempo lleva vencido. Ej: 'hace 2 horas', 'hace 3 días'."""
    diff = ahora - fecha_devolucion
    total_seg = int(diff.total_seconds())
    if total_seg < 60:
        return 'hace unos segundos'
    minutos = total_seg // 60
    if minutos < 60:
        return f'hace {minutos} min'
    horas = minutos // 60
    if horas < 24:
        return f'hace {horas} h {minutos % 60} min' if minutos % 60 else f'hace {horas} h'
    dias = horas // 24
    horas_rest = horas % 24
    if dias == 1:
        return f'hace 1 día' + (f' y {horas_rest} h' if horas_rest else '')
    return f'hace {dias} días' + (f' y {horas_rest} h' if horas_rest else '')


def _tiempo_restante(fecha_devolucion, ahora):
    """Devuelve texto humanizado del tiempo que queda. Ej: '2 h 30 min', '3 días'."""
    diff = fecha_devolucion - ahora
    total_seg = int(diff.total_seconds())
    if total_seg <= 0:
        return ''
    minutos = total_seg // 60
    if minutos < 60:
        return f'{minutos} min'
    horas = minutos // 60
    if horas < 24:
        return f'{horas} h {minutos % 60} min' if minutos % 60 else f'{horas} h'
    dias = horas // 24
    horas_rest = horas % 24
    if dias == 1:
        return '1 día' + (f' y {horas_rest} h' if horas_rest else '')
    return f'{dias} días' + (f' y {horas_rest} h' if horas_rest else '')


def _registrar_auditoria(request, accion, entidad, entidad_id=None, descripcion=''):
    usuario = None
    if request and getattr(request, 'user', None) and request.user.is_authenticated:
        usuario = request.user
    rol = None
    if usuario and getattr(usuario, 'id_rol_fk', None):
        rol = usuario.id_rol_fk.nombre_rol

    actor = 'sistema'
    if usuario and usuario.is_authenticated:
        nombre = f'{getattr(usuario, "nombre", "") or ""} {getattr(usuario, "apellido", "") or ""}'.strip()
        actor = nombre or getattr(usuario, 'correo', None) or f'usuario#{getattr(usuario, "pk", "")}'

    descripcion_final = (descripcion or '').strip()
    actor_tag = f'Actor: {actor}' + (f' ({rol})' if rol else '')
    if descripcion_final:
        descripcion_final = f'{descripcion_final} | {actor_tag}'
    else:
        descripcion_final = actor_tag

    ip = ''
    if request:
        ip = request.META.get('HTTP_X_FORWARDED_FOR', '') or request.META.get('REMOTE_ADDR', '')
    if ',' in ip:
        ip = ip.split(',')[0].strip()

    try:
        AuditoriaLog.objects.create(
            accion=accion,
            entidad=entidad,
            entidad_id=str(entidad_id) if entidad_id is not None else None,
            descripcion=descripcion_final,
            id_usuario_fk=usuario if usuario and usuario.is_authenticated else None,
            rol_usuario=rol,
            ip_origen=ip[:45] if ip else None,
        )
    except Exception:
        # Evita romper el flujo principal si la tabla de auditoria aun no existe.
        pass


def _auto_cancelar_pedidos_pendientes_vencidos():
    now = timezone.localtime()
    with transaction.atomic():
        pedidos = list(
            Pedido.objects
            .select_for_update()
            .select_related('id_usuario_fk')
            .filter(
                estado='pendiente',
                fecha_devolucion__isnull=False,
                fecha_devolucion__lte=now,
            )
        )

        if not pedidos:
            return 0

        pedido_ids = [p.id_pedido for p in pedidos]
        Pedido.objects.filter(id_pedido__in=pedido_ids).update(
            estado='cancelado',
            fch_ult_act=now,
        )
        DetallePedido.objects.filter(id_pedido_fk_id__in=pedido_ids).update(
            estado_detalle='cancelado',
            fch_ult_act=now,
        )

    for pedido in pedidos:
        _crear_notificacion(
            usuario=pedido.id_usuario_fk,
            tipo='rechazado',
            titulo='Pedido cancelado automáticamente',
            mensaje=(
                f'Tu pedido #{pedido.id_pedido} fue cancelado automáticamente porque '
                'la hora/fecha límite de entrega se venció antes de ser aprobado por almacén.'
            ),
            pedido_id=pedido.id_pedido,
        )
        _registrar_auditoria(
            None,
            accion='actualizar',
            entidad='pedido',
            entidad_id=pedido.id_pedido,
            descripcion=f'Pedido #{pedido.id_pedido} cancelado automáticamente por vencimiento en estado pendiente.',
        )

    return len(pedidos)


def _sumar_stock_disponibilidad(detalle, now):
    if not detalle.id_prod_fk_id:
        return

    disp = (
        Disponibilidad.objects
        .select_for_update()
        .filter(id_prod_fk_id=detalle.id_prod_fk_id)
        .order_by('-id_disp')
        .first()
    )

    if not disp:
        Disponibilidad.objects.create(
            id_prod_fk=detalle.id_prod_fk,
            cantidad=detalle.cantidad_solicitada,
            stock=detalle.cantidad_solicitada,
            descr_dispo='Stock restaurado por devolución de préstamo.',
            fch_registro=now,
            fch_ult_act=now,
        )
        return

    if disp.cantidad is not None:
        disp.cantidad += detalle.cantidad_solicitada
        update_fields = ['cantidad', 'fch_ult_act']
    elif disp.stock is not None:
        disp.stock += detalle.cantidad_solicitada
        update_fields = ['stock', 'fch_ult_act']
    else:
        disp.cantidad = detalle.cantidad_solicitada
        update_fields = ['cantidad', 'fch_ult_act']

    disp.fch_ult_act = now
    disp.save(update_fields=update_fields)


def _renovar_codigo_devolucion(pedido, now):
    pedido.codigo_entrega = f'{secrets.randbelow(1000000):06d}'
    pedido.codigo_expira_en = now + timedelta(seconds=DEVOLUCION_CODIGO_SEGUNDOS)
    pedido.fch_ult_act = now
    pedido.save(update_fields=['codigo_entrega', 'codigo_expira_en', 'fch_ult_act'])


@login_required
def producto_editar(request, prod_id):
    # Solo admin puede editar
    if not (request.user.is_authenticated and request.user.id_rol_fk and request.user.id_rol_fk.nombre_rol == 'admin'):
        messages.error(request, 'No tienes permisos para editar productos.')
        return redirect('producto_detalle', prod_id=prod_id)

    producto = get_object_or_404(Producto, pk=prod_id)
    catalogos = Catalogo.objects.all().order_by('nombre_catalogo')
    disp = (
        Disponibilidad.objects
        .filter(id_prod_fk=producto)
        .order_by('-id_disp')
        .first()
    )
    if request.method == 'POST':
        nombre = request.POST.get('nombre_producto', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        id_cat_fk = request.POST.get('id_cat_fk')
        stock = request.POST.get('stock')
        cantidad = request.POST.get('cantidad')
        descr_dispo = request.POST.get('descr_dispo', '').strip()
        fot_prod = request.FILES.get('fot_prod')
        # Validaciones mínimas
        if not nombre or not id_cat_fk or stock is None or cantidad is None:
            messages.error(request, 'Completa todos los campos obligatorios.')
        else:
            producto.nombre_producto = nombre
            producto.descripcion = descripcion
            producto.id_cat_fk_id = id_cat_fk
            if fot_prod:
                producto.fot_prod = fot_prod
            producto.fch_ult_act = timezone.now()
            producto.save()
            # Actualizar disponibilidad
            if disp:
                disp.stock = stock
                disp.cantidad = cantidad
                disp.descr_dispo = descr_dispo
                disp.fch_ult_act = timezone.now()
                disp.save()
            else:
                Disponibilidad.objects.create(
                    id_prod_fk=producto,
                    stock=stock,
                    cantidad=cantidad,
                    descr_dispo=descr_dispo,
                    fch_registro=timezone.now(),
                    fch_ult_act=timezone.now(),
                )
            messages.success(request, 'Producto actualizado correctamente.')
            return redirect('producto_detalle', prod_id=producto.id_prod)
    return render(request, 'inventario/catalogo/producto_editar.html', {
        'producto': producto,
        'catalogos': catalogos,
        'disponibilidad': disp,
    })

@login_required
def producto_detalle(request, prod_id):
    if not _is_admin_or_almacenista(request):
        return redirect('panel_usuario')

    from .models import Producto, Disponibilidad
    try:
        producto = Producto.objects.select_related('id_cat_fk').get(pk=prod_id)
    except Producto.DoesNotExist:
        raise Http404('Producto no encontrado')
    disp = (
        Disponibilidad.objects
        .filter(id_prod_fk=producto)
        .order_by('-id_disp')
        .first()
    )
    return render(request, 'inventario/catalogo/producto_detalle.html', {
        'producto': producto,
        'catalogo': producto.id_cat_fk,
        'disponibilidad': disp,
    })

# Panel de almacenista
from django.contrib.auth.decorators import login_required

@login_required
def panel_almacenista(request):
    if not _is_admin_or_almacenista(request):
        return redirect('panel_usuario')
    return redirect('inventario_panel')
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db import transaction
from django.db.models import OuterRef, Subquery
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .db_compat import usuario_supports_tipo_doc
from .forms import CatalogoForm, ProductoForm, UsuarioPerfilForm
from .models import AuditoriaLog, Catalogo, DetallePedido, Disponibilidad, Pedido, PedidoEvidencia, Producto, Usuario, Rol, VerificacionSenaToken


def _user_role(request):
    if not request.user.is_authenticated:
        return None
    if getattr(request.user, 'is_superuser', False) or getattr(request.user, 'is_staff', False):
        return 'admin'

    rol = (getattr(getattr(request.user, 'id_rol_fk', None), 'nombre_rol', '') or '').strip().lower()
    if rol in {'admin', 'administrador'}:
        return 'admin'
    if rol in {'almacenista', 'almacen'}:
        return 'almacenista'
    if rol in {'', 'usuario', 'aprendiz', 'instructor'}:
        return 'usuario'
    return rol


def _is_admin(request):
    return _user_role(request) == 'admin'


def _is_admin_or_almacenista(request):
    return _user_role(request) in ['admin', 'almacenista']


@login_required
def catalogo(request):
    if not _is_admin_or_almacenista(request):
        return redirect('dashboard')

    catalogos = (
        Catalogo.objects
        .annotate(total_productos=models.Count('producto'))
        .order_by('nombre_catalogo')
    )
    cat_form = CatalogoForm()
    prod_form = ProductoForm()
    return render(
        request,
        'inventario/catalogo/catalogo.html',
        {
            'catalogos': catalogos,
            'cat_form': cat_form,
            'prod_form': prod_form,
            'puede_gestionar_catalogo': _is_admin(request),
        },
    )


@login_required
def registrar_catalogo(request):
    if not _is_admin(request):
        messages.error(request, 'Solo el administrador puede registrar catalogos.')
        return redirect('catalogo')

    if request.method == 'POST':
        form = CatalogoForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.fch_registro = timezone.now()
            obj.fch_ult_act = timezone.now()
            obj.save()
            _registrar_auditoria(
                request,
                accion='crear',
                entidad='catalogo',
                entidad_id=obj.id_cat,
                descripcion=f'Se creó el catálogo "{obj.nombre_catalogo}".',
            )
            messages.success(request, f'Catálogo "{obj.nombre_catalogo}" registrado correctamente.')
        else:
            messages.error(request, 'Error al registrar el catálogo. Revisa los campos.')
    return redirect('catalogo')


@login_required
def registrar_producto(request):
    if not _is_admin(request):
        messages.error(request, 'Solo el administrador puede registrar productos.')
        return redirect('catalogo')

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.fch_registro = timezone.now()
            obj.fch_ult_act = timezone.now()
            obj.save()
            _registrar_auditoria(
                request,
                accion='crear',
                entidad='producto',
                entidad_id=obj.id_prod,
                descripcion=f'Se creó el producto "{obj.nombre_producto}".',
            )

            stock_inicial = form.cleaned_data.get('stock_inicial') or 0
            descr_dispo = form.cleaned_data.get('descr_dispo') or ''
            Disponibilidad.objects.create(
                id_prod_fk=obj,
                cantidad=stock_inicial,
                stock=stock_inicial,
                descr_dispo=descr_dispo,
                fch_registro=timezone.now(),
                fch_ult_act=timezone.now(),
            )

            messages.success(request, f'Producto "{obj.nombre_producto}" registrado correctamente.')
        else:
            messages.error(request, 'Error al registrar el producto. Revisa los campos.')
    return redirect('catalogo')


@login_required
def eliminar_catalogo(request, cat_id):
    if not _is_admin(request):
        messages.error(request, 'Solo el administrador puede eliminar catalogos.')
        return redirect('catalogo')

    catalogo = get_object_or_404(Catalogo, pk=cat_id)

    if request.method == 'POST':
        if Producto.objects.filter(id_cat_fk=catalogo).exists():
            messages.error(
                request,
                f'No se puede eliminar el catálogo "{catalogo.nombre_catalogo}" porque tiene productos registrados.',
            )
        else:
            nombre = catalogo.nombre_catalogo
            catalogo_id = catalogo.id_cat
            catalogo.delete()
            _registrar_auditoria(
                request,
                accion='eliminar',
                entidad='catalogo',
                entidad_id=catalogo_id,
                descripcion=f'Se eliminó el catálogo "{nombre}".',
            )
            messages.success(request, f'Catálogo "{nombre}" eliminado correctamente.')

    return redirect('catalogo')


@login_required
def productos_catalogo(request, cat_id):
    if not _is_admin_or_almacenista(request):
        return redirect('dashboard')

    catalogo = get_object_or_404(Catalogo, pk=cat_id)
    disp_qs = Disponibilidad.objects.filter(id_prod_fk=OuterRef('pk')).order_by('-id_disp')
    productos = (
        Producto.objects
        .filter(id_cat_fk=catalogo)
        .annotate(
            stock_actual=Subquery(disp_qs.values('stock')[:1]),
            cantidad_total=Subquery(disp_qs.values('cantidad')[:1]),
            descr_dispo_actual=Subquery(disp_qs.values('descr_dispo')[:1]),
        )
        .order_by('nombre_producto')
    )
    return render(
        request,
        'inventario/catalogo/productos_catalogo.html',
        {
            'catalogo': catalogo,
            'productos': productos,
            'puede_gestionar_catalogo': _is_admin(request),
        },
    )


@login_required
def eliminar_producto(request, cat_id, prod_id):
    if not _is_admin(request):
        messages.error(request, 'Solo el administrador puede eliminar productos.')
        return redirect('productos_catalogo', cat_id=cat_id)

    catalogo = get_object_or_404(Catalogo, pk=cat_id)
    producto = get_object_or_404(Producto, pk=prod_id, id_cat_fk=catalogo)

    if request.method == 'POST':
        nombre = producto.nombre_producto
        producto_id = producto.id_prod
        producto.delete()
        _registrar_auditoria(
            request,
            accion='eliminar',
            entidad='producto',
            entidad_id=producto_id,
            descripcion=f'Se eliminó el producto "{nombre}".',
        )
        messages.success(request, f'Producto "{nombre}" eliminado correctamente.')

    return redirect('productos_catalogo', cat_id=cat_id)



@login_required
def dashboard(request):
    if not _is_admin(request):
        if _user_role(request) == 'almacenista':
            return redirect('inventario_panel')
        return redirect('panel_usuario')

    _auto_cancelar_pedidos_pendientes_vencidos()

    ahora = timezone.localtime()
    anio_actual = ahora.year
    mes_actual = ahora.month
    disp_qs = Disponibilidad.objects.filter(id_prod_fk=OuterRef('pk')).order_by('-id_disp')

    alertas_stock_bajo_raw = list(
        Producto.objects
        .select_related('id_cat_fk')
        .annotate(stock_actual=Subquery(disp_qs.values('stock')[:1]))
        .filter(stock_actual__isnull=False, stock_actual__lt=5)
        .order_by('stock_actual', 'nombre_producto')[:8]
    )

    alertas_stock_bajo = []
    for item in alertas_stock_bajo_raw:
        stock = int(item.stock_actual or 0)
        nivel = 'Critico' if stock <= 2 else 'Bajo'
        detalle = 'Reposicion urgente' if stock <= 2 else 'Planificar reposicion'
        alertas_stock_bajo.append({
            'nombre_producto': item.nombre_producto,
            'catalogo': item.id_cat_fk.nombre_catalogo if item.id_cat_fk else 'Sin catalogo',
            'stock_actual': stock,
            'nivel': nivel,
            'detalle': detalle,
        })

    alertas_cantidad_baja_raw = list(
        Producto.objects
        .select_related('id_cat_fk')
        .annotate(cantidad_actual=Subquery(disp_qs.values('cantidad')[:1]))
        .filter(cantidad_actual__isnull=False, cantidad_actual__lt=5)
        .order_by('cantidad_actual', 'nombre_producto')[:8]
    )

    alertas_cantidad_baja = []
    for item in alertas_cantidad_baja_raw:
        cantidad = int(item.cantidad_actual or 0)
        nivel = 'Critico' if cantidad <= 2 else 'Bajo'
        detalle = 'Revisar disponibilidad inmediata' if cantidad <= 2 else 'Programar abastecimiento'
        alertas_cantidad_baja.append({
            'nombre_producto': item.nombre_producto,
            'catalogo': item.id_cat_fk.nombre_catalogo if item.id_cat_fk else 'Sin catalogo',
            'cantidad_actual': cantidad,
            'nivel': nivel,
            'detalle': detalle,
        })

    productos_con_existencia = list(
        Producto.objects
        .select_related('id_cat_fk')
        .annotate(
            stock_actual=Subquery(disp_qs.values('stock')[:1]),
            cantidad_actual=Subquery(disp_qs.values('cantidad')[:1]),
        )
        .order_by('nombre_producto')
    )

    total_stock_general = 0
    total_cantidad_general = 0
    productos_deficit_base = []
    for item in productos_con_existencia:
        stock = max(int(item.stock_actual or 0), 0)
        cantidad = max(int(item.cantidad_actual or 0), 0)
        total_stock_general += stock
        total_cantidad_general += cantidad

        if cantidad < stock:
            productos_deficit_base.append({
                'producto_id': item.id_prod,
                'nombre_producto': item.nombre_producto or f'Producto {item.id_prod}',
                'catalogo': item.id_cat_fk.nombre_catalogo if item.id_cat_fk else 'Sin catalogo',
                'stock_actual': stock,
                'cantidad_actual': cantidad,
                'faltante': stock - cantidad,
            })

    deficit_producto_ids = [item['producto_id'] for item in productos_deficit_base]
    detalle_por_producto = defaultdict(dict)
    if deficit_producto_ids:
        resumen_detalles = (
            DetallePedido.objects
            .filter(
                id_prod_fk_id__in=deficit_producto_ids,
                id_pedido_fk__estado__in=['entregado', 'pendiente', 'esperando entrega'],
            )
            .values('id_prod_fk_id', 'id_pedido_fk__estado')
            .annotate(
                total=models.Sum('cantidad_solicitada'),
                pedido_ref=models.Max('id_pedido_fk_id'),
            )
        )
        for item in resumen_detalles:
            detalle_por_producto[item['id_prod_fk_id']][item['id_pedido_fk__estado']] = {
                'total': int(item['total'] or 0),
                'pedido_ref': item['pedido_ref'],
            }

    productos_deficit = []
    for base in productos_deficit_base:
        estados = detalle_por_producto.get(base['producto_id'], {})
        entregado = estados.get('entregado', {})
        pendiente = estados.get('pendiente', {})
        esperando = estados.get('esperando entrega', {})

        motivo = f'Diferencia inventario: faltan {base["faltante"]} und por ajuste de disponibilidad.'
        pedido_ref = None

        if int(entregado.get('total', 0)) > 0:
            motivo = f'En prestamos activos: {entregado["total"]} und comprometidas.'
            pedido_ref = entregado.get('pedido_ref')
        elif int(pendiente.get('total', 0)) > 0 or int(esperando.get('total', 0)) > 0:
            total_comprometido = int(pendiente.get('total', 0)) + int(esperando.get('total', 0))
            motivo = f'Comprometido en pedidos por entregar: {total_comprometido} und.'
            pedido_ref = esperando.get('pedido_ref') or pendiente.get('pedido_ref')

        productos_deficit.append({
            **base,
            'motivo': motivo,
            'pedido_ref': pedido_ref,
        })

    productos_deficit.sort(key=lambda item: (-item['faltante'], item['cantidad_actual'], item['nombre_producto']))

    pie_stock_cantidad_segmentos = []
    pie_stock_cantidad_tramos = []
    total_stock_cantidad = total_stock_general + total_cantidad_general
    tramo_acumulado = 0.0
    if total_stock_cantidad > 0:
        segmentos = [
            ('Stock total', total_stock_general, '#2d6cdf'),
            ('Cantidad total', total_cantidad_general, '#22a06b'),
        ]
        for etiqueta, cantidad, color in segmentos:
            if cantidad <= 0:
                continue
            porcentaje = round((cantidad / total_stock_cantidad) * 100, 1)
            inicio = tramo_acumulado
            tramo_acumulado += porcentaje
            pie_stock_cantidad_tramos.append(f'{color} {inicio:.2f}% {tramo_acumulado:.2f}%')
            pie_stock_cantidad_segmentos.append({
                'label': etiqueta,
                'cantidad': cantidad,
                'porcentaje': porcentaje,
                'color': color,
            })

    pie_stock_cantidad_conic = (
        'conic-gradient(' + (', '.join(pie_stock_cantidad_tramos) if pie_stock_cantidad_tramos else '#dce5de 0% 100%') + ')'
    )

    total_productos = Producto.objects.count()
    prestamos_activos = Pedido.objects.filter(estado='entregado').count()
    month_keys, resumen_mensual = _resumen_pedidos_mensual(ahora, meses=12)
    key_actual = (anio_actual, mes_actual)
    estado_conteos = resumen_mensual.get(key_actual, {
        'pendiente': 0,
        'esperando entrega': 0,
        'entregado': 0,
        'devuelto': 0,
        'cancelado': 0,
    })
    pedidos_mes_actual = sum(estado_conteos.values())
    pendientes_preview_limit = 6
    pedidos_pendientes_total = Pedido.objects.filter(estado='pendiente').count()
    pedidos_pendientes_qs = (
        Pedido.objects
        .filter(estado='pendiente')
        .select_related('id_usuario_fk')
        .prefetch_related('detalles')
        .order_by('fch_registro', 'id_pedido')[:pendientes_preview_limit]
    )

    resumen_pendientes = []
    for pedido in pedidos_pendientes_qs:
        detalles = list(pedido.detalles.all())
        if detalles:
            producto_label = detalles[0].nombre_producto or f'Producto {detalles[0].id_prod_fk_id}'
            if len(detalles) > 1:
                producto_label = f'{producto_label} +{len(detalles)-1}'
        else:
            producto_label = 'Sin productos'

        usuario_label = (
            f'{pedido.id_usuario_fk.nombre or ""} {pedido.id_usuario_fk.apellido or ""}'.strip()
            if pedido.id_usuario_fk_id else ''
        )
        if not usuario_label:
            usuario_label = pedido.id_usuario_fk.correo if pedido.id_usuario_fk_id else 'Sin usuario'

        resumen_pendientes.append({
            'id_pedido': pedido.id_pedido,
            'usuario': usuario_label,
            'producto': producto_label,
            'fecha_solicitud': pedido.fch_registro,
            'fecha_entrega': pedido.fecha_devolucion,
            'codigo_confirmacion': pedido.codigo_entrega or '--',
            'estado': 'Pendiente',
        })

    usuarios_solicitud_manual_qs = (
        Usuario.objects
        .filter(verificacion_sena_estado='solicitada')
        .order_by('verificacion_sena_solicitada_en', 'id_usu')
    )
    usuarios_solicitud_manual_total = usuarios_solicitud_manual_qs.count()
    usuarios_solicitud_manual = []
    for usuario in usuarios_solicitud_manual_qs[:8]:
        nombre_usuario = (f'{usuario.nombre or ""} {usuario.apellido or ""}'.strip() or usuario.correo or f'Usuario {usuario.pk}')
        intento_url = ''
        if getattr(usuario, 'verificacion_sena_imagen', None):
            try:
                intento_url = usuario.verificacion_sena_imagen.url
            except Exception:
                intento_url = ''

        usuarios_solicitud_manual.append({
            'id': usuario.pk,
            'nombre': nombre_usuario,
            'correo': usuario.correo or '-',
            'documento': usuario.cc or '-',
            'estado': usuario.get_verificacion_sena_estado_display(),
            'observacion': (usuario.verificacion_sena_observacion or '').strip(),
            'solicitada_en': usuario.verificacion_sena_solicitada_en,
            'intento_url': intento_url,
        })

    usuarios_solicitud_manual_modal = []
    for usuario in usuarios_solicitud_manual_qs:
        nombre_usuario = (f'{usuario.nombre or ""} {usuario.apellido or ""}'.strip() or usuario.correo or f'Usuario {usuario.pk}')
        intento_url = ''
        if getattr(usuario, 'verificacion_sena_imagen', None):
            try:
                intento_url = usuario.verificacion_sena_imagen.url
            except Exception:
                intento_url = ''

        usuarios_solicitud_manual_modal.append({
            'id': usuario.pk,
            'nombre': nombre_usuario,
            'correo': usuario.correo or '-',
            'documento': usuario.cc or '-',
            'estado': usuario.get_verificacion_sena_estado_display(),
            'observacion': (usuario.verificacion_sena_observacion or '').strip(),
            'solicitada_en': usuario.verificacion_sena_solicitada_en,
            'intento_url': intento_url,
        })

    usuarios_documento_validacion_qs = (
        Usuario.objects
        .filter(verificacion_sena_estado='documento_cargado')
        .order_by('verificacion_sena_solicitada_en', 'id_usu')
    )
    usuarios_documento_validacion_total = usuarios_documento_validacion_qs.count()
    usuarios_documento_validacion = []
    for usuario in usuarios_documento_validacion_qs[:12]:
        nombre_usuario = (f'{usuario.nombre or ""} {usuario.apellido or ""}'.strip() or usuario.correo or f'Usuario {usuario.pk}')

        intento_url = ''
        if getattr(usuario, 'verificacion_sena_imagen', None):
            try:
                intento_url = usuario.verificacion_sena_imagen.url
            except Exception:
                intento_url = ''

        documento_url = ''
        if getattr(usuario, 'verificacion_sena_documento', None):
            try:
                documento_url = usuario.verificacion_sena_documento.url
            except Exception:
                documento_url = ''

        usuarios_documento_validacion.append({
            'id': usuario.pk,
            'nombre': nombre_usuario,
            'correo': usuario.correo or '-',
            'documento': usuario.cc or '-',
            'estado': usuario.get_verificacion_sena_estado_display(),
            'observacion': (usuario.verificacion_sena_observacion or '').strip(),
            'solicitada_en': usuario.verificacion_sena_solicitada_en,
            'intento_url': intento_url,
            'documento_url': documento_url,
        })
    productos_en_mora = (
        DetallePedido.objects
        .filter(
            id_pedido_fk__estado='entregado',
            fecha_devolucion__isnull=False,
            fecha_devolucion__lt=ahora,
        )
        .exclude(estado_detalle__in=['devuelto', 'cancelado', 'rechazado', 'no_disponible'])
        .aggregate(total=models.Sum('cantidad_solicitada'))
        .get('total') or 0
    )

    estados_pedido = [
        ('pendiente', 'Pendientes', '#2d6cdf'),
        ('esperando entrega', 'Esperando entrega', '#26a7c6'),
        ('entregado', 'Prestados', '#57c271'),
        ('devuelto', 'Devueltos', '#e88a2a'),
        ('cancelado', 'Cancelados', '#cf3f5b'),
    ]
    prestamos_mes_actual = estado_conteos.get('entregado', 0)

    total_pedidos_mes = sum(estado_conteos.values())
    pie_segmentos = []
    pie_tramos = []
    acumulado = 0.0
    if total_pedidos_mes > 0:
        for clave, etiqueta, color in estados_pedido:
            cantidad = estado_conteos.get(clave, 0)
            if cantidad <= 0:
                continue
            porcentaje = round((cantidad / total_pedidos_mes) * 100, 1)
            inicio = acumulado
            acumulado += porcentaje
            pie_tramos.append(f'{color} {inicio:.2f}% {acumulado:.2f}%')
            pie_segmentos.append({
                'label': etiqueta,
                'cantidad': cantidad,
                'porcentaje': porcentaje,
                'color': color,
            })

    pie_conic = 'conic-gradient(' + (', '.join(pie_tramos) if pie_tramos else '#dce5de 0% 100%') + ')'

    tendencia = _construir_tendencia_mensual(ahora, meses=12)
    nombres_meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

    return render(
        request,
        'inventario/dashboard/index.html',
        {
            'total_productos': total_productos,
            'total_stock_general': total_stock_general,
            'total_cantidad_general': total_cantidad_general,
            'pie_stock_cantidad_segmentos': pie_stock_cantidad_segmentos,
            'pie_stock_cantidad_conic': pie_stock_cantidad_conic,
            'productos_deficit': productos_deficit[:20],
            'total_productos_deficit': len(productos_deficit),
            'prestamos_activos': prestamos_activos,
            'pedidos_mes_actual': pedidos_mes_actual,
            'pedidos_pendientes_total': pedidos_pendientes_total,
            'hay_mas_pendientes': pedidos_pendientes_total > pendientes_preview_limit,
            'resumen_pendientes': resumen_pendientes,
            'usuarios_solicitud_manual': usuarios_solicitud_manual,
            'usuarios_solicitud_manual_modal': usuarios_solicitud_manual_modal,
            'usuarios_solicitud_manual_total': usuarios_solicitud_manual_total,
            'usuarios_documento_validacion': usuarios_documento_validacion,
            'usuarios_documento_validacion_total': usuarios_documento_validacion_total,
            'prestamos_mes_actual': prestamos_mes_actual,
            'productos_en_mora': productos_en_mora,
            'alertas_stock_bajo': alertas_stock_bajo,
            'alertas_cantidad_baja': alertas_cantidad_baja,
            'pie_segmentos': pie_segmentos,
            'pie_conic': pie_conic,
            'total_pedidos_mes': total_pedidos_mes,
            'tendencia': tendencia,
            'mes_reporte': ahora.strftime('%Y-%m'),
            'mes_actual_label': f'{nombres_meses[mes_actual - 1]} {anio_actual}',
        },
    )


def _construir_tendencia_mensual(ahora, meses=12):
    month_keys, resumen_mensual = _resumen_pedidos_mensual(ahora, meses=meses)
    nombres_meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

    tendencia = []
    for y, m in month_keys:
        data = resumen_mensual.get((y, m), {})
        tendencia.append({
            'year': y,
            'month': m,
            'label': f'{nombres_meses[m - 1]} {str(y)[2:]}',
            'prestamos': data.get('entregado', 0),
            'pendientes': data.get('pendiente', 0),
            'devueltos': data.get('devuelto', 0),
            'cancelados': data.get('cancelado', 0),
        })
    return tendencia


def _resumen_pedidos_mensual(ahora, meses=12):
    def _mes_menos(base_year, base_month, minus_steps):
        total = base_year * 12 + (base_month - 1) - minus_steps
        return total // 12, (total % 12) + 1

    month_keys = [_mes_menos(ahora.year, ahora.month, offset) for offset in range(meses - 1, -1, -1)]
    month_keys = [key for key in month_keys if key[0] >= 2026]
    if not month_keys:
        month_keys = [(ahora.year, ahora.month)]
    month_set = set(month_keys)

    base = {
        'pendiente': 0,
        'esperando entrega': 0,
        'entregado': 0,
        'devuelto': 0,
        'cancelado': 0,
    }
    resumen = {key: dict(base) for key in month_keys}

    pedidos = Pedido.objects.exclude(fch_registro__isnull=True).only('estado', 'fch_registro')
    for pedido in pedidos:
        dt = pedido.fch_registro
        if not dt:
            continue
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_current_timezone())
        dt_local = timezone.localtime(dt)
        key = (dt_local.year, dt_local.month)
        if key not in month_set:
            continue
        estado = (pedido.estado or '').strip().lower()
        if estado == 'rechazado':
            estado = 'cancelado'
        if estado in resumen[key]:
            resumen[key][estado] += 1

    return month_keys, resumen


@login_required
def dashboard_tendencia_data(request):
    if not _is_admin(request):
        return JsonResponse({'ok': False, 'error': 'No autorizado.'}, status=403)

    _auto_cancelar_pedidos_pendientes_vencidos()

    ahora = timezone.localtime()
    tendencia = _construir_tendencia_mensual(ahora, meses=12)
    return JsonResponse({
        'ok': True,
        'tendencia': tendencia,
        'updated_at': ahora.strftime('%Y-%m-%d %H:%M:%S'),
    })


@login_required
def dashboard_tendencia_detalle(request):
    if not _is_admin(request):
        return JsonResponse({'ok': False, 'error': 'No autorizado.'}, status=403)

    _auto_cancelar_pedidos_pendientes_vencidos()

    try:
        year = int(request.GET.get('year', '0'))
        month = int(request.GET.get('month', '0'))
    except (TypeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'Parámetros inválidos.'}, status=400)

    serie = (request.GET.get('serie') or '').strip().lower()
    if not (1900 <= year <= 2200 and 1 <= month <= 12):
        return JsonResponse({'ok': False, 'error': 'Periodo inválido.'}, status=400)

    if serie not in {'pendientes', 'prestamos', 'devueltos', 'cancelados'}:
        return JsonResponse({'ok': False, 'error': 'Serie inválida.'}, status=400)

    estado_target = {
        'pendientes': {'pendiente'},
        'prestamos': {'entregado'},
        'devueltos': {'devuelto'},
        'cancelados': {'cancelado', 'rechazado'},
    }[serie]

    pedidos = (
        Pedido.objects
        .exclude(fch_registro__isnull=True)
        .select_related('id_usuario_fk__id_rol_fk')
        .only('id_pedido', 'estado', 'fch_registro', 'id_usuario_fk__nombre', 'id_usuario_fk__apellido', 'id_usuario_fk__correo', 'id_usuario_fk__id_rol_fk__nombre_rol')
    )

    pedidos_filtrados = []
    for pedido in pedidos:
        dt = pedido.fch_registro
        if not dt:
            continue
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_current_timezone())
        dt_local = timezone.localtime(dt)
        if dt_local.year != year or dt_local.month != month:
            continue
        if (pedido.estado or '').strip().lower() not in estado_target:
            continue
        pedidos_filtrados.append(pedido)

    ids_pedido = [p.id_pedido for p in pedidos_filtrados]
    logs = AuditoriaLog.objects.none()
    if ids_pedido:
        logs = (
            AuditoriaLog.objects
            .filter(entidad_id__in=[str(pid) for pid in ids_pedido], entidad__in=['pedido', 'prestamo'])
            .select_related('id_usuario_fk__id_rol_fk')
            .order_by('-fch_registro', '-id_log')
        )

    ultimo_log_por_pedido = {}
    for log in logs:
        try:
            pid = int(log.entidad_id)
        except (TypeError, ValueError):
            continue
        if pid not in ultimo_log_por_pedido:
            ultimo_log_por_pedido[pid] = log

    detalle = []
    for pedido in pedidos_filtrados:
        log = ultimo_log_por_pedido.get(pedido.id_pedido)
        if log and log.id_usuario_fk:
            nombre = f'{log.id_usuario_fk.nombre or ""} {log.id_usuario_fk.apellido or ""}'.strip()
            actor = nombre or log.id_usuario_fk.correo or f'Usuario #{log.id_usuario_fk_id}'
            rol = log.rol_usuario or (log.id_usuario_fk.id_rol_fk.nombre_rol if getattr(log.id_usuario_fk, 'id_rol_fk', None) else '-')
            hora = timezone.localtime(log.fch_registro).strftime('%d/%m/%Y %H:%M') if log.fch_registro else '-'
            descripcion = log.descripcion or '-'
        else:
            usuario = pedido.id_usuario_fk
            nombre = f'{usuario.nombre or ""} {usuario.apellido or ""}'.strip() if usuario else ''
            actor = nombre or (usuario.correo if usuario else '-')
            rol = usuario.id_rol_fk.nombre_rol if usuario and getattr(usuario, 'id_rol_fk', None) else '-'
            hora = timezone.localtime(pedido.fch_registro).strftime('%d/%m/%Y %H:%M') if pedido.fch_registro else '-'
            descripcion = f'Pedido #{pedido.id_pedido} en estado {pedido.estado or "-"}.'

        detalle.append({
            'pedido_id': pedido.id_pedido,
            'usuario': actor,
            'rol': rol,
            'hora': hora,
            'descripcion': descripcion,
            'estado': pedido.estado,
        })

    return JsonResponse({
        'ok': True,
        'serie': serie,
        'year': year,
        'month': month,
        'total': len(detalle),
        'items': detalle,
    })


def inventario_panel(request):
    if not _is_admin_or_almacenista(request):
        return redirect('panel_usuario')

    q = (request.GET.get('q') or '').strip()
    cat_id = (request.GET.get('categoria') or '').strip()
    bajo_stock = (request.GET.get('bajo_stock') or '').strip() == '1'
    disp_qs = Disponibilidad.objects.filter(id_prod_fk=OuterRef('pk')).order_by('-id_disp')

    productos_qs = (
        Producto.objects
        .select_related('id_cat_fk')
        .annotate(
            stock_actual=Subquery(disp_qs.values('stock')[:1]),
            cantidad_actual=Subquery(disp_qs.values('cantidad')[:1]),
        )
    )

    if cat_id.isdigit():
        productos_qs = productos_qs.filter(id_cat_fk_id=int(cat_id))

    if q:
        productos_qs = productos_qs.filter(
            models.Q(nombre_producto__icontains=q)
            | models.Q(id_cat_fk__nombre_catalogo__icontains=q)
        )

    if bajo_stock:
        productos_qs = productos_qs.filter(stock_actual__lte=5)

    productos = list(productos_qs.order_by('-fch_registro', '-id_prod'))

    catalogos = (
        Catalogo.objects.annotate(
            total_productos=models.Count('producto')
        ).order_by('nombre_catalogo')
    )

    productos_por_catalogo = {}
    for prod in productos:
        productos_por_catalogo.setdefault(prod.id_cat_fk_id, []).append(prod)

    secciones_catalogo = [
        {
            'catalogo': cat,
            'productos': productos_por_catalogo.get(cat.id_cat, []),
        }
        for cat in catalogos
        if productos_por_catalogo.get(cat.id_cat)
    ]

    return render(
        request,
        'inventario/dashboard/inventario_panel.html',
        {
            'q': q,
            'categoria_activa': cat_id,
            'bajo_stock': bajo_stock,
            'catalogos': catalogos,
            'productos': productos,
            'secciones_catalogo': secciones_catalogo,
        },
    )


def _mes_reporte_desde_request(request):
    mes_param = (request.GET.get('mes') or '').strip()
    ahora = timezone.localtime()
    if len(mes_param) == 7 and mes_param[4] == '-':
        try:
            anio = int(mes_param[:4])
            mes = int(mes_param[5:7])
            if 1 <= mes <= 12:
                return anio, mes
        except (TypeError, ValueError):
            pass
    return ahora.year, ahora.month


def _obtener_prestamos_mes(anio, mes):
    pedidos_qs = (
        Pedido.objects
        .exclude(fch_registro__isnull=True)
        .select_related('id_usuario_fk__id_rol_fk')
        .prefetch_related('detalles')
        .order_by('-fch_registro', '-id_pedido')
    )

    pedidos_filtrados = []
    for pedido in pedidos_qs:
        dt = pedido.fch_registro
        if not dt:
            continue
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_current_timezone())
        dt_local = timezone.localtime(dt)
        if dt_local.year == anio and dt_local.month == mes:
            pedidos_filtrados.append(pedido)

    return pedidos_filtrados


def _categoria_pedido_reporte(estado):
    estado_limpio = (estado or '').strip().lower()
    if estado_limpio in ['entregado', 'devuelto']:
        return 'REALIZADO'
    if estado_limpio in ['cancelado', 'rechazado']:
        return 'CANCELADO'
    return 'EN PROCESO'


def _resumen_productos_pedido(pedido, max_items=None, multiline=False):
    detalles = list(getattr(pedido, 'detalles', []).all()) if hasattr(getattr(pedido, 'detalles', None), 'all') else []
    if not detalles:
        return 'Sin detalle'

    nombres = []
    for idx, det in enumerate(detalles, start=1):
        nombre = (det.nombre_producto or '').strip() or f'Producto {det.id_prod_fk_id or "-"}'
        cantidad = int(det.cantidad_solicitada or 0)
        estado = (det.estado_detalle or '').strip()
        sufijo_estado = f' [{estado}]' if estado else ''
        nombres.append(f'{idx}. {nombre} x{cantidad}{sufijo_estado}')

    if max_items is not None and max_items >= 0:
        nombres = nombres[:max_items]
        if len(detalles) > max_items:
            nombres.append(f'+{len(detalles) - max_items} más')

    separador = '\n' if multiline else ' | '
    return separador.join(nombres)


def _build_pdf_text_report(lines):
    def _escape(texto):
        return (texto or '').replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')

    contenido = ['BT', '/F1 10 Tf', '14 TL', '40 800 Td']
    for idx, linea in enumerate(lines[:55]):
        if idx == 0:
            contenido.append(f'({_escape(linea)}) Tj')
        else:
            contenido.append('T*')
            contenido.append(f'({_escape(linea)}) Tj')
    contenido.append('ET')

    stream_data = '\n'.join(contenido).encode('latin-1', errors='replace')
    obj1 = b'1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n'
    obj2 = b'2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n'
    obj3 = (
        b'3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] '
        b'/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>endobj\n'
    )
    obj4 = b'4 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n'
    obj5 = b'5 0 obj<< /Length ' + str(len(stream_data)).encode('ascii') + b' >>stream\n' + stream_data + b'\nendstream endobj\n'

    objects = [obj1, obj2, obj3, obj4, obj5]
    pdf = b'%PDF-1.4\n'
    offsets = []
    for obj in objects:
        offsets.append(len(pdf))
        pdf += obj

    xref_start = len(pdf)
    pdf += b'xref\n0 6\n0000000000 65535 f \n'
    for off in offsets:
        pdf += f'{off:010d} 00000 n \n'.encode('ascii')
    pdf += b'trailer<< /Size 6 /Root 1 0 R >>\nstartxref\n'
    pdf += str(xref_start).encode('ascii') + b'\n%%EOF'
    return pdf


@login_required
def reporte_prestamos_excel(request):
    if not _is_admin_or_almacenista(request):
        return redirect('panel_usuario')

    anio, mes = _mes_reporte_desde_request(request)
    prestamos = _obtener_prestamos_mes(anio, mes)
    secciones = {
        'REALIZADO': [],
        'CANCELADO': [],
        'EN PROCESO': [],
    }
    for pedido in prestamos:
        secciones[_categoria_pedido_reporte(pedido.estado)].append(pedido)

    try:
        from openpyxl import Workbook
        from openpyxl.drawing.image import Image as XLImage
        from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    except Exception:
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="reporte_prestamos_{anio}_{mes:02d}.csv"'
        response.write('\ufeff')

        writer = csv.writer(response, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow([f'Reporte mensual de pedidos - {anio}-{mes:02d}'])
        writer.writerow(['Generado', timezone.localtime().strftime('%d/%m/%Y %H:%M')])
        writer.writerow([])
        writer.writerow(['Resumen'])
        writer.writerow(['Realizados', len(secciones['REALIZADO'])])
        writer.writerow(['Cancelados', len(secciones['CANCELADO'])])
        writer.writerow(['En proceso', len(secciones['EN PROCESO'])])
        writer.writerow(['Total', len(prestamos)])
        writer.writerow([])

        encabezado = [
            'Categoria', 'Pedido', 'Fecha registro', 'Estado pedido', 'Usuario', 'Rol',
            'Total productos', 'Total unidades', 'Item', 'Producto', 'Cantidad solicitada',
            'Estado detalle', 'Area', 'Fecha devolucion'
        ]

        for nombre_seccion in ['REALIZADO', 'CANCELADO', 'EN PROCESO']:
            items = secciones[nombre_seccion]
            writer.writerow([f'SECCION: {nombre_seccion} ({len(items)})'])
            writer.writerow(encabezado)

            for pedido in items:
                usuario = pedido.id_usuario_fk
                nombre_usuario = ((usuario.nombre or '') + ' ' + (usuario.apellido or '')).strip() or (usuario.correo or '')
                rol = usuario.id_rol_fk.nombre_rol if usuario.id_rol_fk else 'sin rol'
                fecha_registro = timezone.localtime(pedido.fch_registro).strftime('%d/%m/%Y %H:%M') if pedido.fch_registro else '-'
                fecha_devolucion = timezone.localtime(pedido.fecha_devolucion).strftime('%d/%m/%Y %H:%M') if pedido.fecha_devolucion else '-'
                area = (pedido.area_ubicacion or '').replace('\n', ' ').replace(';', ',')

                detalles = list(pedido.detalles.all()) if hasattr(pedido, 'detalles') else []
                if not detalles:
                    writer.writerow([
                        nombre_seccion,
                        pedido.id_pedido,
                        fecha_registro,
                        pedido.estado,
                        nombre_usuario,
                        rol,
                        pedido.total_productos,
                        pedido.total_unidades,
                        '-',
                        'Sin detalle',
                        0,
                        '-',
                        area,
                        fecha_devolucion,
                    ])
                    continue

                for idx, det in enumerate(detalles, start=1):
                    producto = ((det.nombre_producto or '').strip() or f'Producto {det.id_prod_fk_id or "-"}').replace(';', ',')
                    writer.writerow([
                        nombre_seccion,
                        pedido.id_pedido,
                        fecha_registro,
                        pedido.estado,
                        nombre_usuario,
                        rol,
                        pedido.total_productos,
                        pedido.total_unidades,
                        idx,
                        producto,
                        int(det.cantidad_solicitada or 0),
                        (det.estado_detalle or '-').replace(';', ','),
                        area,
                        fecha_devolucion,
                    ])
            writer.writerow([])
        return response

    wb = Workbook()
    ws = wb.active
    ws.title = 'Reporte pedidos'

    widths = [15, 10, 19, 16, 22, 12, 14, 14, 8, 34, 16, 16, 20, 19]
    for idx, w in enumerate(widths, start=1):
        ws.column_dimensions[chr(64 + idx)].width = w

    thin = Side(style='thin', color='CFE4D2')
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    fill_title = PatternFill('solid', fgColor='DFF4E5')
    fill_section = PatternFill('solid', fgColor='ECF8F0')
    fill_head = PatternFill('solid', fgColor='E5F4E9')
    fill_alt = PatternFill('solid', fgColor='F7FCF8')

    font_title = Font(name='Calibri', size=16, bold=True, color='1D6B3A')
    font_sub = Font(name='Calibri', size=11, bold=True, color='2A5E3F')
    font_head = Font(name='Calibri', size=10, bold=True, color='235438')
    font_cell = Font(name='Calibri', size=10, color='1F4330')

    row = 1
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=14)
    ws.cell(row=row, column=1, value=f'Reporte mensual de pedidos - {anio}-{mes:02d}')
    ws.cell(row=row, column=1).font = font_title
    ws.cell(row=row, column=1).fill = fill_title
    ws.cell(row=row, column=1).alignment = Alignment(horizontal='left', vertical='center')
    ws.row_dimensions[row].height = 28

    row += 1
    ws.cell(row=row, column=1, value='Generado')
    ws.cell(row=row, column=2, value=timezone.localtime().strftime('%d/%m/%Y %H:%M'))
    ws.cell(row=row, column=1).font = font_sub
    ws.cell(row=row, column=2).font = font_sub

    logo_candidates = [
        os.path.join(settings.BASE_DIR, 'logoSena.png'),
        os.path.join(settings.BASE_DIR, 'inventario', 'static', 'inventario', 'img', 'logoSena.png'),
    ]
    for logo_path in logo_candidates:
        if not os.path.exists(logo_path):
            continue
        try:
            logo = XLImage(logo_path)
            logo.width = 64
            logo.height = 64
            ws.add_image(logo, 'N1')
            break
        except Exception:
            continue

    row += 2
    ws.cell(row=row, column=1, value='Resumen').font = font_sub
    resumen_items = [
        ('Realizados', len(secciones['REALIZADO'])),
        ('Cancelados', len(secciones['CANCELADO'])),
        ('En proceso', len(secciones['EN PROCESO'])),
        ('Total', len(prestamos)),
    ]
    for nombre, cantidad in resumen_items:
        row += 1
        ws.cell(row=row, column=1, value=nombre).font = font_cell
        ws.cell(row=row, column=2, value=cantidad).font = font_cell

    row += 2
    encabezado = [
        'Categoria', 'Pedido', 'Fecha registro', 'Estado pedido', 'Usuario', 'Rol',
        'Total productos', 'Total unidades', 'Item', 'Producto', 'Cantidad solicitada',
        'Estado detalle', 'Area', 'Fecha devolucion'
    ]

    for nombre_seccion in ['REALIZADO', 'CANCELADO', 'EN PROCESO']:
        items = secciones[nombre_seccion]

        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=14)
        ws.cell(row=row, column=1, value=f'SECCION: {nombre_seccion} ({len(items)})')
        ws.cell(row=row, column=1).font = font_sub
        ws.cell(row=row, column=1).fill = fill_section
        ws.cell(row=row, column=1).alignment = Alignment(horizontal='left', vertical='center')
        row += 1

        for col, name in enumerate(encabezado, start=1):
            c = ws.cell(row=row, column=col, value=name)
            c.font = font_head
            c.fill = fill_head
            c.border = border
            c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        row += 1

        data_start = row
        for pedido in items:
            usuario = pedido.id_usuario_fk
            nombre_usuario = ((usuario.nombre or '') + ' ' + (usuario.apellido or '')).strip() or (usuario.correo or '')
            rol = usuario.id_rol_fk.nombre_rol if usuario.id_rol_fk else 'sin rol'
            fecha_registro = timezone.localtime(pedido.fch_registro).strftime('%d/%m/%Y %H:%M') if pedido.fch_registro else '-'
            fecha_devolucion = timezone.localtime(pedido.fecha_devolucion).strftime('%d/%m/%Y %H:%M') if pedido.fecha_devolucion else '-'
            area = (pedido.area_ubicacion or '').replace('\n', ' ')
            detalles = list(pedido.detalles.all()) if hasattr(pedido, 'detalles') else []

            if not detalles:
                detalles = [None]

            for idx, det in enumerate(detalles, start=1):
                producto = 'Sin detalle'
                cantidad_det = 0
                estado_det = '-'
                if det is not None:
                    producto = (det.nombre_producto or '').strip() or f'Producto {det.id_prod_fk_id or "-"}'
                    cantidad_det = int(det.cantidad_solicitada or 0)
                    estado_det = det.estado_detalle or '-'

                row_values = [
                    nombre_seccion,
                    pedido.id_pedido,
                    fecha_registro,
                    pedido.estado,
                    nombre_usuario,
                    rol,
                    pedido.total_productos,
                    pedido.total_unidades,
                    idx if det is not None else '-',
                    producto,
                    cantidad_det,
                    estado_det,
                    area,
                    fecha_devolucion,
                ]

                for col, value in enumerate(row_values, start=1):
                    c = ws.cell(row=row, column=col, value=value)
                    c.font = font_cell
                    c.border = border
                    c.alignment = Alignment(vertical='top', wrap_text=True)
                if (row - data_start) % 2 == 1:
                    for col in range(1, 15):
                        ws.cell(row=row, column=col).fill = fill_alt
                row += 1

        row += 1

    ws.freeze_panes = 'A12'

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename="reporte_prestamos_{anio}_{mes:02d}.xlsx"'
    return response


@login_required
def reporte_prestamos_pdf(request):
    if not _is_admin_or_almacenista(request):
        return redirect('panel_usuario')

    anio, mes = _mes_reporte_desde_request(request)
    prestamos = list(_obtener_prestamos_mes(anio, mes))

    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        messages.error(request, 'No se pudo generar el PDF porque Pillow no está disponible en el servidor.')
        return redirect('dashboard')

    secciones = {
        'REALIZADO': [],
        'CANCELADO': [],
        'EN PROCESO': [],
    }
    for pedido in prestamos:
        secciones[_categoria_pedido_reporte(pedido.estado)].append(pedido)

    page_w, page_h = 1754, 1240
    margin_x = 36
    header_h = 126
    row_h = 70

    col_pedido = 70
    col_fecha = 150
    col_estado = 120
    col_usuario = 220
    col_rol = 110
    col_productos = 70
    col_unidades = 80
    col_detalle = 360
    col_devolucion = 150
    col_area = 352

    x_pedido = margin_x
    x_fecha = x_pedido + col_pedido
    x_estado = x_fecha + col_fecha
    x_usuario = x_estado + col_estado
    x_rol = x_usuario + col_usuario
    x_productos = x_rol + col_rol
    x_unidades = x_productos + col_productos
    x_detalle = x_unidades + col_unidades
    x_devolucion = x_detalle + col_detalle
    x_area = x_devolucion + col_devolucion
    x_end = x_area + col_area

    def _load_font(size, bold=False):
        candidates = []
        windir = os.environ.get('WINDIR', 'C:\\Windows')
        if bold:
            candidates.extend([
                os.path.join(windir, 'Fonts', 'arialbd.ttf'),
                os.path.join(windir, 'Fonts', 'segoeuib.ttf'),
            ])
        else:
            candidates.extend([
                os.path.join(windir, 'Fonts', 'arial.ttf'),
                os.path.join(windir, 'Fonts', 'segoeui.ttf'),
            ])
        for path in candidates:
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
        return ImageFont.load_default()

    font_title = _load_font(32, bold=True)
    font_sub = _load_font(19, bold=False)
    font_head = _load_font(17, bold=True)
    font_cell = _load_font(15, bold=False)

    pages = []
    page = None
    draw = None
    y = 0
    page_number = 0

    def _new_page():
        nonlocal page, draw, y, page_number
        page_number += 1
        page = Image.new('RGB', (page_w, page_h), 'white')
        draw = ImageDraw.Draw(page)

        draw.rectangle((margin_x, 28, x_end, 28 + header_h), outline='#2d7a49', width=2)

        logo_candidates = [
            os.path.join(settings.BASE_DIR, 'logoSena.png'),
            os.path.join(settings.BASE_DIR, 'inventario', 'static', 'inventario', 'img', 'logoSena.png'),
        ]
        logo_pasted = False
        for logo_path in logo_candidates:
            if not os.path.exists(logo_path):
                continue
            try:
                with Image.open(logo_path) as logo_src:
                    logo = logo_src.convert('RGBA')
                    logo.thumbnail((86, 86), Image.Resampling.LANCZOS)
                    page.paste(logo, (margin_x + 12, 46), logo)
                logo_pasted = True
                break
            except Exception:
                continue

        title_x = margin_x + (118 if logo_pasted else 16)
        draw.text((title_x, 48), f'REPORTE MENSUAL DE PEDIDOS - {anio}-{mes:02d}', fill='#1b6e3a', font=font_title)
        draw.text(
            (title_x, 94),
            f'Generado: {timezone.localtime().strftime("%d/%m/%Y %H:%M")} | Página {page_number}',
            fill='#4d7f62',
            font=font_sub,
        )

        y = 28 + header_h + 16

    def _draw_table_header(top_y):
        draw.rectangle((margin_x, top_y, x_end, top_y + 30), outline='#8cb99a', width=1, fill='#ecf7ef')
        draw.text((x_pedido + 6, top_y + 7), 'ID', fill='#205335', font=font_head)
        draw.text((x_fecha + 6, top_y + 7), 'FECHA', fill='#205335', font=font_head)
        draw.text((x_estado + 6, top_y + 7), 'ESTADO', fill='#205335', font=font_head)
        draw.text((x_usuario + 6, top_y + 7), 'USUARIO', fill='#205335', font=font_head)
        draw.text((x_rol + 6, top_y + 7), 'ROL', fill='#205335', font=font_head)
        draw.text((x_productos + 6, top_y + 7), 'PROD', fill='#205335', font=font_head)
        draw.text((x_unidades + 6, top_y + 7), 'UNDS', fill='#205335', font=font_head)
        draw.text((x_detalle + 6, top_y + 7), 'DETALLE PRODUCTOS', fill='#205335', font=font_head)
        draw.text((x_devolucion + 6, top_y + 7), 'DEVOLUCION', fill='#205335', font=font_head)
        draw.text((x_area + 6, top_y + 7), 'AREA', fill='#205335', font=font_head)
        return top_y + 30

    def _wrap_lines(texto, width_chars):
        bruto = (texto or '').strip() or '-'
        bloques = bruto.splitlines() or ['-']
        lines = []
        for bloque in bloques:
            limpio = (bloque or '').strip() or '-'
            lines.extend(textwrap.wrap(limpio, width=width_chars) or ['-'])
        return lines

    def _draw_wrapped_text(texto, x, top_y, width_chars, max_lines=2):
        lines = _wrap_lines(texto, width_chars)
        if max_lines is not None:
            lines = lines[:max_lines]
        for idx, line in enumerate(lines):
            draw.text((x, top_y + 7 + idx * 18), line, fill='#244f35', font=font_cell)

    _new_page()
    resumen_realizados = len(secciones['REALIZADO'])
    resumen_cancelados = len(secciones['CANCELADO'])
    resumen_proceso = len(secciones['EN PROCESO'])
    draw.text(
        (margin_x, y),
        f'Resumen -> Realizados: {resumen_realizados}  |  Cancelados: {resumen_cancelados}  |  En proceso: {resumen_proceso}  |  Total: {len(prestamos)}',
        fill='#2f6844',
        font=font_sub,
    )
    y += 34

    for sec_nombre in ['REALIZADO', 'CANCELADO', 'EN PROCESO']:
        items = secciones[sec_nombre]
        if y + 64 > page_h - 30:
            pages.append(page)
            _new_page()

        draw.rectangle((margin_x, y, x_end, y + 34), outline='#b7d5bf', width=1, fill='#f3fbf5')
        draw.text((margin_x + 10, y + 8), f'SECCION: {sec_nombre} ({len(items)})', fill='#245a39', font=font_head)
        y += 34
        y = _draw_table_header(y)

        if not items:
            if y + row_h > page_h - 30:
                pages.append(page)
                _new_page()
                y = _draw_table_header(y)
            draw.rectangle((margin_x, y, x_end, y + row_h), outline='#d2e2d6', width=1)
            draw.text((margin_x + 12, y + 24), 'Sin pedidos en esta sección.', fill='#5f7d67', font=font_cell)
            y += row_h
            y += 10
            continue

        for idx, pedido in enumerate(items):
            detalle_completo = _resumen_productos_pedido(pedido, multiline=True)
            detalle_lines = _wrap_lines(detalle_completo, 45)
            area_lines = _wrap_lines((pedido.area_ubicacion or '-').replace('\n', ' '), 41)
            fecha_lines = _wrap_lines(
                timezone.localtime(pedido.fch_registro).strftime('%Y-%m-%d %H:%M') if pedido.fch_registro else '-',
                16,
            )

            lineas_necesarias = max(len(detalle_lines), len(area_lines), len(fecha_lines), 2)
            row_h_actual = max(row_h, 12 + lineas_necesarias * 18)

            if y + row_h_actual > page_h - 30:
                pages.append(page)
                _new_page()
                y = _draw_table_header(y)

            bg = '#ffffff' if idx % 2 == 0 else '#f8fcf9'
            draw.rectangle((margin_x, y, x_end, y + row_h_actual), outline='#d2e2d6', width=1, fill=bg)
            for x_line in [x_fecha, x_estado, x_usuario, x_rol, x_productos, x_unidades, x_detalle, x_devolucion, x_area]:
                draw.line((x_line, y, x_line, y + row_h_actual), fill='#dcebdd', width=1)

            usuario = pedido.id_usuario_fk
            nombre_usuario = ((usuario.nombre or '') + ' ' + (usuario.apellido or '')).strip() or (usuario.correo or '-')
            rol = usuario.id_rol_fk.nombre_rol if usuario and usuario.id_rol_fk else '-'
            fecha_txt = timezone.localtime(pedido.fch_registro).strftime('%Y-%m-%d %H:%M') if pedido.fch_registro else '-'
            devolucion_txt = timezone.localtime(pedido.fecha_devolucion).strftime('%Y-%m-%d %H:%M') if pedido.fecha_devolucion else '-'

            draw.text((x_pedido + 6, y + 24), str(pedido.id_pedido), fill='#23543a', font=font_cell)
            _draw_wrapped_text(fecha_txt, x_fecha + 6, y, width_chars=16, max_lines=2)
            _draw_wrapped_text((pedido.estado or '-').title(), x_estado + 6, y, width_chars=14, max_lines=2)
            _draw_wrapped_text(nombre_usuario, x_usuario + 6, y, width_chars=25, max_lines=2)
            _draw_wrapped_text(rol, x_rol + 6, y, width_chars=11, max_lines=2)
            draw.text((x_productos + 20, y + 24), str(pedido.total_productos or 0), fill='#23543a', font=font_cell)
            draw.text((x_unidades + 20, y + 24), str(pedido.total_unidades or 0), fill='#23543a', font=font_cell)
            _draw_wrapped_text(detalle_completo, x_detalle + 6, y, width_chars=45, max_lines=None)
            _draw_wrapped_text(devolucion_txt, x_devolucion + 6, y, width_chars=15, max_lines=2)
            _draw_wrapped_text((pedido.area_ubicacion or '-').replace('\n', ' '), x_area + 6, y, width_chars=41, max_lines=None)

            y += row_h_actual

        y += 10

    if page is not None:
        pages.append(page)

    buffer = io.BytesIO()
    pages[0].save(buffer, format='PDF', save_all=True, append_images=pages[1:])
    pdf_bytes = buffer.getvalue()
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_prestamos_{anio}_{mes:02d}.pdf"'
    return response


@login_required
def reporte_stock_bajo_pdf(request):
    if not _is_admin_or_almacenista(request):
        return redirect('panel_usuario')

    from django.db.models.functions import Coalesce

    try:
        from PIL import Image, ImageDraw, ImageFont, ImageOps
    except Exception:
        messages.error(request, 'No se pudo generar el PDF porque Pillow no está disponible en el servidor.')
        return redirect('dashboard')

    disp_qs = Disponibilidad.objects.filter(id_prod_fk=OuterRef('pk')).order_by('-id_disp')
    productos_qs = (
        Producto.objects
        .select_related('id_cat_fk')
        .annotate(
            stock_actual=Coalesce(Subquery(disp_qs.values('stock')[:1]), 0),
            cantidad_actual=Coalesce(Subquery(disp_qs.values('cantidad')[:1]), 0),
        )
        .filter(
            models.Q(stock_actual__lt=5)
            | models.Q(cantidad_actual__lt=5)
        )
        .order_by('stock_actual', 'cantidad_actual', 'nombre_producto')
    )

    productos = list(productos_qs)
    if not productos:
        messages.info(request, 'No hay productos con stock o cantidad baja para exportar.')
        return redirect('dashboard')

    # A4 horizontal para que la tabla salga amplia y legible en impresión.
    page_w, page_h = 1754, 1240
    margin_x = 44
    y_start = 200
    row_h = 148

    col_check = 58
    col_img = 130
    col_title = 300
    col_desc = 560
    col_cant = 120
    col_stock = 120
    col_estado = 220
    col_compra = 158

    x_check = margin_x
    x_img = x_check + col_check
    x_title = x_img + col_img
    x_desc = x_title + col_title
    x_cant = x_desc + col_desc
    x_stock = x_cant + col_cant
    x_estado = x_stock + col_stock
    x_compra = x_estado + col_estado
    x_end = x_compra + col_compra

    def _load_font(size, bold=False):
        candidates = []
        windir = os.environ.get('WINDIR', 'C:\\Windows')
        if bold:
            candidates.extend([
                os.path.join(windir, 'Fonts', 'arialbd.ttf'),
                os.path.join(windir, 'Fonts', 'segoeuib.ttf'),
            ])
        else:
            candidates.extend([
                os.path.join(windir, 'Fonts', 'arial.ttf'),
                os.path.join(windir, 'Fonts', 'segoeui.ttf'),
            ])

        for path in candidates:
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
        return ImageFont.load_default()

    font_title = _load_font(42, bold=True)
    font_sub = _load_font(22, bold=False)
    font_head = _load_font(20, bold=True)
    font_cell = _load_font(18, bold=False)
    font_small = _load_font(16, bold=False)

    pages = []
    page = None
    draw = None
    y = y_start
    page_number = 0

    def _new_page():
        nonlocal page, draw, y, page_number
        page_number += 1
        page = Image.new('RGB', (page_w, page_h), 'white')
        draw = ImageDraw.Draw(page)

        header_top = 48
        header_bottom = 170
        draw.rectangle((margin_x, header_top, x_end, header_bottom), outline='#1f3f67', width=3)

        logo_candidates = [
            os.path.join(settings.BASE_DIR, 'logoSena.png'),
            os.path.join(settings.BASE_DIR, 'inventario', 'static', 'inventario', 'img', 'logoSena.png'),
        ]
        logo_pasted = False
        for logo_path in logo_candidates:
            if not os.path.exists(logo_path):
                continue
            try:
                with Image.open(logo_path) as logo_src:
                    logo = logo_src.convert('RGBA')
                    logo.thumbnail((98, 98), Image.Resampling.LANCZOS)
                    logo_x = margin_x + 16
                    logo_y = header_top + 12
                    page.paste(logo, (logo_x, logo_y), logo)
                logo_pasted = True
                break
            except Exception:
                continue

        title_x = margin_x + (132 if logo_pasted else 18)
        draw.text(
            (title_x, header_top + 28),
            'RECIBO SENA DE PRODUCTOS EN ALERTA',
            fill='#00843d',
            font=font_title,
        )
        draw.text(
            (title_x, header_top + 82),
            f'Generado: {timezone.localtime().strftime("%d/%m/%Y %H:%M")}  |  Página {page_number}',
            fill='#3e5f82',
            font=font_sub,
        )

        draw.rectangle((margin_x, y_start - 38, x_end, y_start), outline='#7f96b2', width=1, fill='#f2f7fd')
        draw.text((x_check + 18, y_start - 29), 'X', fill='#25496c', font=font_head)
        draw.text((x_img + 20, y_start - 29), 'IMAGEN', fill='#25496c', font=font_head)
        draw.text((x_title + 10, y_start - 29), 'TITULO', fill='#25496c', font=font_head)
        draw.text((x_desc + 10, y_start - 29), 'DESCRIPCION', fill='#25496c', font=font_head)
        draw.text((x_cant + 15, y_start - 29), 'CANTIDAD', fill='#25496c', font=font_head)
        draw.text((x_stock + 24, y_start - 29), 'STOCK', fill='#25496c', font=font_head)
        draw.text((x_estado + 12, y_start - 29), 'MOTIVO', fill='#25496c', font=font_head)
        draw.text((x_compra + 12, y_start - 29), 'COMPRA', fill='#25496c', font=font_head)

        y = y_start

    def _draw_cell_box(top_y):
        draw.rectangle((margin_x, top_y, x_end, top_y + row_h), outline='#c7d4e4', width=1)
        draw.line((x_img, top_y, x_img, top_y + row_h), fill='#d2ddec', width=1)
        draw.line((x_title, top_y, x_title, top_y + row_h), fill='#d2ddec', width=1)
        draw.line((x_desc, top_y, x_desc, top_y + row_h), fill='#d2ddec', width=1)
        draw.line((x_cant, top_y, x_cant, top_y + row_h), fill='#d2ddec', width=1)
        draw.line((x_stock, top_y, x_stock, top_y + row_h), fill='#d2ddec', width=1)
        draw.line((x_estado, top_y, x_estado, top_y + row_h), fill='#d2ddec', width=1)
        draw.line((x_compra, top_y, x_compra, top_y + row_h), fill='#d2ddec', width=1)

        # Cuadro de check para marcar con esfero.
        draw.rectangle((x_check + 18, top_y + 54, x_check + 42, top_y + 78), outline='#2a4b6f', width=2)

    def _draw_wrapped(texto, x, top_y, width_chars=42, max_lines=4, fill='#1f3856', font=None, line_h=22):
        limpio = (texto or '').strip()
        if not limpio:
            limpio = '-'
        lines = textwrap.wrap(limpio, width=width_chars)[:max_lines]
        use_font = font or font_cell
        for idx, line in enumerate(lines):
            draw.text((x, top_y + 10 + idx * line_h), line, fill=fill, font=use_font)

    _new_page()
    for prod in productos:
        if y + row_h > page_h - 80:
            pages.append(page)
            _new_page()

        _draw_cell_box(y)

        stock = int(prod.stock_actual or 0)
        cantidad = int(prod.cantidad_actual or 0)
        if cantidad < stock:
            estado_txt = f'Faltan {stock - cantidad} und'
        elif stock < 5 and cantidad < 5:
            estado_txt = 'Stock y cantidad bajos'
        elif stock < 5:
            estado_txt = 'Stock bajo'
        else:
            estado_txt = 'Cantidad baja'

        # Imagen del producto.
        if getattr(prod, 'fot_prod', None):
            try:
                ruta_imagen = prod.fot_prod.path
                if os.path.exists(ruta_imagen):
                    with Image.open(ruta_imagen) as img_src:
                        thumb = ImageOps.fit(img_src.convert('RGB'), (106, 106), method=Image.Resampling.LANCZOS)
                        page.paste(thumb, (x_img + 12, y + 20))
            except Exception:
                draw.rectangle((x_img + 12, y + 20, x_img + 118, y + 126), outline='#c8d6e7', width=1)
                draw.text((x_img + 28, y + 68), 'Sin img', fill='#6e839d', font=font_small)
        else:
            draw.rectangle((x_img + 12, y + 20, x_img + 118, y + 126), outline='#c8d6e7', width=1)
            draw.text((x_img + 28, y + 68), 'Sin img', fill='#6e839d', font=font_small)

        _draw_wrapped(prod.nombre_producto, x_title + 10, y, width_chars=30, max_lines=3, font=font_cell, line_h=24)
        _draw_wrapped(prod.descripcion, x_desc + 10, y, width_chars=58, max_lines=5, font=font_small, line_h=20)
        draw.text((x_cant + 44, y + 60), str(cantidad), fill='#1f3856', font=font_head)
        draw.text((x_stock + 44, y + 60), str(stock), fill='#1f3856', font=font_head)
        _draw_wrapped(estado_txt, x_estado + 10, y, width_chars=22, max_lines=4, font=font_small, line_h=20)

        # Espacio para que escriban la cantidad comprada a mano.
        draw.line((x_compra + 12, y + 70, x_end - 14, y + 70), fill='#355a82', width=1)
        draw.text((x_compra + 12, y + 82), 'cantidad comprada', fill='#6f86a2', font=font_small)

        y += row_h

    if page is not None:
        pages.append(page)

    buffer = io.BytesIO()
    pages[0].save(buffer, format='PDF', save_all=True, append_images=pages[1:])
    pdf_bytes = buffer.getvalue()

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="recibo_stock_bajo_{timezone.localtime().strftime("%Y%m%d_%H%M")}.pdf"'
    )
    return response


@login_required
def perfil_usuario(request):
    usuario = request.user
    tipo_doc_habilitado = usuario_supports_tipo_doc(Usuario)
    if request.method == 'POST':
        form = UsuarioPerfilForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('perfil_usuario')
        else:
            messages.error(request, 'Corrige los errores en el formulario.')
    else:
        form = UsuarioPerfilForm(instance=usuario)

    pedidos_qs = Pedido.objects.filter(id_usuario_fk=usuario).order_by('-fch_registro', '-id_pedido')
    pedido_stats = {
        'total': pedidos_qs.count(),
        'pendientes': pedidos_qs.filter(estado='pendiente').count(),
        'entregados': pedidos_qs.filter(estado__in=['entregado', 'devuelto']).count(),
        'cancelados': pedidos_qs.filter(estado__in=['cancelado', 'rechazado']).count(),
    }
    pedidos_recientes = list(pedidos_qs[:5])

    return render(request, 'inventario/usuario/perfil_usuario.html', {
        'form': form,
        'usuario': usuario,
        'tipo_doc_habilitado': tipo_doc_habilitado,
        'pedido_stats': pedido_stats,
        'pedidos_recientes': pedidos_recientes,
    })


@login_required
def perfil_actualizar_banner(request):
    """Endpoint AJAX para guardar solo el banner/portada del perfil."""
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Método no permitido.'}, status=405)
    archivo = request.FILES.get('banner_usu')
    if not archivo:
        return JsonResponse({'ok': False, 'error': 'No se recibió ninguna imagen.'}, status=400)
    if not archivo.content_type.startswith('image/'):
        return JsonResponse({'ok': False, 'error': 'El archivo debe ser una imagen.'}, status=400)
    usuario = request.user
    # Eliminar banner anterior para evitar archivos huérfanos
    if usuario.banner_usu:
        try:
            usuario.banner_usu.delete(save=False)
        except Exception:
            pass
    usuario.banner_usu = archivo
    usuario.save(update_fields=['banner_usu'])
    return JsonResponse({'ok': True, 'url': usuario.banner_usu.url})


@login_required
def perfil_actualizar_tema(request):
    """Endpoint AJAX para guardar la preferencia de tema del usuario en la BD."""
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Método no permitido.'}, status=405)
    tema = (request.POST.get('tema') or '').strip().lower()
    if tema not in ('claro', 'oscuro'):
        return JsonResponse({'ok': False, 'error': 'Valor de tema inválido.'}, status=400)
    request.user.tema = tema
    request.user.save(update_fields=['tema'])
    return JsonResponse({'ok': True, 'tema': tema})


@login_required
def prestamos_panel(request):
    if not request.user.id_rol_fk or request.user.id_rol_fk.nombre_rol not in ['admin', 'almacenista']:
        return redirect('dashboard')

    ahora = timezone.now()
    prestamos = list(
        Pedido.objects
        .filter(estado__in=['entregado', 'devuelto', 'rechazado'])
        .select_related('id_usuario_fk')
        .prefetch_related('detalles')
        .order_by('fecha_devolucion', '-fch_registro')
    )

    for prestamo in prestamos:
        detalles = list(prestamo.detalles.all())
        prestamo.detalles_entregados = [
            detalle for detalle in detalles
            if detalle.estado_detalle not in ['no_disponible', 'rechazado', 'cancelado']
        ]
        prestamo.fecha_cierre_display = prestamo.fch_ult_act

        # Los cancelados nunca se entregaron: sin vencimiento
        if prestamo.estado in ['rechazado', 'devuelto']:
            prestamo.fecha_devolucion_display = None
            prestamo.es_vencido = False
            prestamo.dias_restantes = None
            prestamo.dias_vencido = 0
            prestamo.tiempo_vencido_str = ''
            prestamo.tiempo_restante_str = ''
            prestamo.detalles_lista = detalles
            continue

        if prestamo.tipo_devolucion == 'individual':
            fechas = [d.fecha_devolucion for d in detalles if d.fecha_devolucion]
            if fechas:
                fecha_ref = min(fechas)
                prestamo.fecha_devolucion_display = fecha_ref
                prestamo.es_vencido = fecha_ref < ahora
                delta = fecha_ref - ahora
                prestamo.dias_restantes = delta.days
                prestamo.dias_vencido = abs(delta.days) if prestamo.es_vencido else 0
                prestamo.tiempo_vencido_str = _tiempo_vencido(fecha_ref, ahora) if prestamo.es_vencido else ''
                prestamo.tiempo_restante_str = _tiempo_restante(fecha_ref, ahora) if not prestamo.es_vencido else ''
            else:
                prestamo.fecha_devolucion_display = None
                prestamo.es_vencido = False
                prestamo.dias_restantes = None
                prestamo.dias_vencido = 0
                prestamo.tiempo_vencido_str = ''
                prestamo.tiempo_restante_str = ''
        else:
            prestamo.fecha_devolucion_display = prestamo.fecha_devolucion
            if prestamo.fecha_devolucion:
                prestamo.es_vencido = prestamo.fecha_devolucion < ahora
                delta = prestamo.fecha_devolucion - ahora
                prestamo.dias_restantes = delta.days
                prestamo.dias_vencido = abs(delta.days) if prestamo.es_vencido else 0
                prestamo.tiempo_vencido_str = _tiempo_vencido(prestamo.fecha_devolucion, ahora) if prestamo.es_vencido else ''
                prestamo.tiempo_restante_str = _tiempo_restante(prestamo.fecha_devolucion, ahora) if not prestamo.es_vencido else ''
            else:
                prestamo.es_vencido = False
                prestamo.dias_restantes = None
                prestamo.dias_vencido = 0
                prestamo.tiempo_vencido_str = ''
                prestamo.tiempo_restante_str = ''
        prestamo.detalles_lista = detalles

    # Ordenar: activos vencidos primero, luego activos al día, después devueltos y cancelados.
    prestamos.sort(key=lambda p: (
        0 if p.estado == 'entregado' and p.es_vencido else 1 if p.estado == 'entregado' else 2 if p.estado == 'devuelto' else 3,
        p.fecha_devolucion_display or ahora.replace(year=9999),
        -(p.fecha_cierre_display.timestamp()) if p.fecha_cierre_display else 0,
    ))

    total_cancelados = sum(1 for p in prestamos if p.estado == 'rechazado')
    total_devueltos = sum(1 for p in prestamos if p.estado == 'devuelto')
    total_vencidos = sum(1 for p in prestamos if p.estado == 'entregado' and p.es_vencido)
    total_activos = sum(1 for p in prestamos if p.estado == 'entregado')
    total_al_dia = total_activos - total_vencidos

    filtro = (request.GET.get('filtro') or 'todos').strip().lower()
    if filtro not in {'todos', 'vencido', 'al-dia', 'devuelto', 'cancelado'}:
        filtro = 'todos'

    if filtro == 'vencido':
        prestamos = [p for p in prestamos if p.estado == 'entregado' and p.es_vencido]
    elif filtro == 'al-dia':
        prestamos = [p for p in prestamos if p.estado == 'entregado' and not p.es_vencido]
    elif filtro == 'devuelto':
        prestamos = [p for p in prestamos if p.estado == 'devuelto']
    elif filtro == 'cancelado':
        prestamos = [p for p in prestamos if p.estado == 'rechazado']

    return render(request, 'inventario/prestamos/panel_prestamos.html', {
        'prestamos': prestamos,
        'filtro_activo': filtro,
        'total_vencidos': total_vencidos,
        'total_al_dia': total_al_dia,
        'total_cancelados': total_cancelados,
        'total_devueltos': total_devueltos,
        'total_activos': total_activos,
        'ahora': ahora,
    })

@login_required
def pedidos_panel(request):
    if not request.user.id_rol_fk or request.user.id_rol_fk.nombre_rol not in ['admin', 'almacenista']:
        return redirect('dashboard')

    _auto_cancelar_pedidos_pendientes_vencidos()

    pedidos = (
        Pedido.objects
        .filter(estado__in=['pendiente', 'esperando entrega'])
        .select_related('id_usuario_fk')
        .prefetch_related('detalles')
        .order_by('-fch_registro', '-id_pedido')
    )
    return render(request, 'inventario/pedidos/panel_pedidos.html', {
        'pedidos': pedidos,
    })


@login_required
def pedido_detalle_panel(request, pedido_id):
    if not request.user.id_rol_fk or request.user.id_rol_fk.nombre_rol not in ['admin', 'almacenista']:
        return redirect('dashboard')

    _auto_cancelar_pedidos_pendientes_vencidos()

    pedido = get_object_or_404(
        Pedido.objects.select_related('id_usuario_fk').prefetch_related('detalles__id_prod_fk', 'evidencias'),
        pk=pedido_id,
    )

    for detalle in pedido.detalles.all():
        detalle.cantidad_disponible_actual = 0
        if detalle.id_prod_fk_id:
            disp_actual = (
                Disponibilidad.objects
                .filter(id_prod_fk_id=detalle.id_prod_fk_id)
                .order_by('-id_disp')
                .first()
            )
            if disp_actual:
                detalle.cantidad_disponible_actual = (
                    disp_actual.cantidad if disp_actual.cantidad is not None else (disp_actual.stock or 0)
                )

    return render(request, 'inventario/pedidos/pedido_detalle.html', {
        'pedido': pedido,
    })


@login_required
def pedido_marcar_esperando_entrega(request, pedido_id):
    if not request.user.id_rol_fk or request.user.id_rol_fk.nombre_rol not in ['admin', 'almacenista']:
        return redirect('dashboard')

    if request.method != 'POST':
        return redirect('pedido_detalle_panel', pedido_id=pedido_id)

    with transaction.atomic():
        pedido = get_object_or_404(
            Pedido.objects.select_for_update(),
            pk=pedido_id,
        )

        if pedido.estado != 'pendiente':
            messages.error(request, 'Este pedido ya fue procesado previamente.')
            return redirect('pedido_detalle_panel', pedido_id=pedido_id)

        detalles = list(
            DetallePedido.objects
            .select_for_update()
            .select_related('id_prod_fk')
            .filter(id_pedido_fk=pedido)
            .exclude(estado_detalle='no_disponible')
            .order_by('id_det_pedido')
        )

        if not detalles:
            messages.error(request, 'El pedido no tiene productos disponibles para procesar.')
            return redirect('pedido_detalle_panel', pedido_id=pedido_id)

        disponibilidad_por_detalle = {}
        errores = []

        for detalle in detalles:
            if not detalle.id_prod_fk_id:
                errores.append(f'Producto sin referencia en detalle #{detalle.id_det_pedido}.')
                continue

            disp = (
                Disponibilidad.objects
                .select_for_update()
                .filter(id_prod_fk_id=detalle.id_prod_fk_id)
                .order_by('-id_disp')
                .first()
            )

            if not disp:
                errores.append(f'Sin disponibilidad para {detalle.nombre_producto}.')
                continue

            disponible = disp.cantidad if disp.cantidad is not None else (disp.stock or 0)
            if disponible < detalle.cantidad_solicitada:
                errores.append(
                    f'Cantidad insuficiente en {detalle.nombre_producto} (solicita {detalle.cantidad_solicitada}, disponible {disponible}).'
                )
                continue

            disponibilidad_por_detalle[detalle.id_det_pedido] = disp

        if errores:
            messages.error(request, 'No se pudo procesar el pedido: ' + ' '.join(errores))
            return redirect('pedido_detalle_panel', pedido_id=pedido_id)

        now = timezone.now()
        for detalle in detalles:
            disp = disponibilidad_por_detalle.get(detalle.id_det_pedido)
            if not disp:
                continue

            solicitado = detalle.cantidad_solicitada
            if disp.cantidad is not None:
                disp.cantidad = max(disp.cantidad - solicitado, 0)
            disp.fch_ult_act = now
            disp.save(update_fields=['cantidad', 'fch_ult_act'])

            detalle.estado_detalle = 'esperando entrega'
            detalle.fch_ult_act = now
            detalle.save(update_fields=['estado_detalle', 'fch_ult_act'])

        codigo_entrega = f'{secrets.randbelow(1000000):06d}'
        pedido.estado = 'esperando entrega'
        pedido.codigo_entrega = codigo_entrega
        pedido.codigo_expira_en = now + timedelta(hours=2)
        pedido.fch_ult_act = now
        pedido.save(update_fields=['estado', 'codigo_entrega', 'codigo_expira_en', 'fch_ult_act'])

    _registrar_auditoria(
        request,
        accion='actualizar',
        entidad='pedido',
        entidad_id=pedido.id_pedido,
        descripcion=f'Pedido #{pedido.id_pedido} pasó a esperando entrega.',
    )
    messages.success(request, f'Pedido #{pedido.id_pedido} procesado. Codigo de entrega generado por 2 horas.')
    _crear_notificacion(
        usuario=pedido.id_usuario_fk,
        tipo='esperando_entrega',
        titulo='Tu pedido está listo para entrega',
        mensaje=f'Tu pedido #{pedido.id_pedido} fue aprobado y está esperando ser entregado. '
                f'Dirígete al almacén con tu código de entrega.',
        pedido_id=pedido.id_pedido,
    )

    # ── Correo: pedido listo para recoger ────────────────────────────────
    try:
        from django.core.mail import EmailMultiAlternatives
        usuario = pedido.id_usuario_fk
        correo_dest = getattr(usuario, 'correo', None) or getattr(usuario, 'email', None)
        if correo_dest:
            nombre = getattr(usuario, 'nombre', '') or str(usuario)
            fecha_str = pedido.fecha_devolucion.strftime('%d/%m/%Y a las %H:%M') if pedido.fecha_devolucion else 'Sin fecha definida'
            base_url = 'https://almacensedelacolonia.pythonanywhere.com'
            detalles_list = list(pedido.detalles.exclude(estado_detalle__in=['no_disponible', 'rechazado', 'cancelado']).select_related('id_prod_fk'))
            filas_html = ''
            lista_txt = ''
            for d in detalles_list:
                prod = d.id_prod_fk
                img_url = f'{base_url}{settings.MEDIA_URL}{prod.fot_prod}' if prod and prod.fot_prod else ''
                img_tag = (f'<img src="{img_url}" width="44" height="44" style="border-radius:6px;object-fit:cover;">'
                           if img_url else '<div style="width:44px;height:44px;background:#e8f5e9;border-radius:6px;display:inline-block;">📦</div>')
                filas_html += f'<tr><td style="padding:10px 12px;border-bottom:1px solid #f0f0f0;width:60px;">{img_tag}</td><td style="padding:10px 12px;border-bottom:1px solid #f0f0f0;font-size:14px;color:#333;">{d.nombre_producto}</td><td style="padding:10px 12px;border-bottom:1px solid #f0f0f0;font-size:14px;color:#555;text-align:center;">x{d.cantidad_solicitada}</td></tr>'
                lista_txt += f'  - {d.nombre_producto} x{d.cantidad_solicitada}\n'
            tabla = f'<p style="font-size:15px;font-weight:700;color:#1a2e1a;margin:20px 0 8px;">📦 Productos a recoger:</p><table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e0e0e0;border-radius:8px;overflow:hidden;"><thead><tr style="background:#f5f5f5;"><th style="padding:10px 12px;text-align:left;font-size:13px;color:#666;width:60px;">Foto</th><th style="padding:10px 12px;text-align:left;font-size:13px;color:#666;">Producto</th><th style="padding:10px 12px;text-align:center;font-size:13px;color:#666;">Cant.</th></tr></thead><tbody>{filas_html}</tbody></table>' if filas_html else ''
            asunto = f'🎉 Tu pedido #{pedido.id_pedido} está listo para recoger | Almacén SENA Sibaté'
            txt = f'Hola {nombre},\n\nTu pedido #{pedido.id_pedido} fue aprobado y está listo para ser retirado en el almacén.\n\nProductos a recoger:\n{lista_txt}\nFecha de devolución: {fecha_str}\n\nDirígete al almacén y muestra tu código de entrega.\n\n— Almacén SENA Sibaté'
            html = f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f4f4f4;font-family:Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f4;padding:32px 0;">
<tr><td align="center"><table width="600" cellpadding="0" cellspacing="0"
  style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:600px;width:100%;">
<tr><td style="background:#2196F3;padding:28px 32px;text-align:center;">
  <p style="margin:0;color:#fff;font-size:13px;opacity:0.85;">SENA — Almacén Sibaté</p>
  <h1 style="margin:8px 0 0;color:#fff;font-size:24px;">🎉 ¡Tu pedido está listo!</h1>
</td></tr>
<tr><td style="padding:32px;">
  <p style="font-size:16px;color:#333;">Hola <strong>{nombre}</strong>,</p>
  <p style="font-size:15px;color:#444;line-height:1.6;">Tu pedido <strong>#{pedido.id_pedido}</strong> fue <strong>aprobado</strong> y ya está listo para ser retirado en el almacén.</p>
  {tabla}
  <table width="100%" cellpadding="0" cellspacing="0" style="margin:20px 0;"><tr>
    <td style="background:#e3f2fd;border-left:4px solid #2196F3;border-radius:6px;padding:14px 18px;">
      <p style="margin:0 0 6px;font-size:14px;color:#333;">📅 Fecha de devolución: <strong>{fecha_str}</strong></p>
      <p style="margin:0;font-size:14px;color:#333;">🏪 Dirígete al almacén y muestra tu <strong>código de entrega</strong>.</p>
    </td>
  </tr></table>
  <p style="font-size:13px;color:#888;margin-top:28px;">— Almacén SENA Sibaté</p>
</td></tr>
<tr><td style="background:#f9f9f9;padding:14px 32px;text-align:center;border-top:1px solid #eee;">
  <p style="margin:0;font-size:12px;color:#aaa;">Centro Industrial y de Desarrollo Empresarial – Sibaté, Cundinamarca</p>
</td></tr>
</table></td></tr></table>
</body></html>"""
            msg = EmailMultiAlternatives(asunto, txt, settings.DEFAULT_FROM_EMAIL, [correo_dest])
            msg.attach_alternative(html, 'text/html')
            msg.send()
    except Exception:
        pass  # No bloquear el flujo si el correo falla

    return redirect('pedido_detalle_panel', pedido_id=pedido_id)


@login_required
def pedido_confirmar_entrega_codigo(request, pedido_id):
    if not request.user.id_rol_fk or request.user.id_rol_fk.nombre_rol not in ['admin', 'almacenista']:
        return redirect('dashboard')

    if request.method != 'POST':
        return redirect('pedido_detalle_panel', pedido_id=pedido_id)

    codigo_ingresado = (request.POST.get('codigo_entrega') or '').strip()
    if not (len(codigo_ingresado) == 6 and codigo_ingresado.isdigit()):
        messages.error(request, 'El codigo debe tener 6 digitos numericos.')
        return redirect('pedido_detalle_panel', pedido_id=pedido_id)

    evidencias_subidas = request.FILES.getlist('evidencias_entrega')
    if len(evidencias_subidas) > 8:
        messages.error(request, 'Solo puedes subir hasta 8 fotos de evidencia por entrega.')
        return redirect('pedido_detalle_panel', pedido_id=pedido_id)

    for archivo in evidencias_subidas:
        if not getattr(archivo, 'content_type', '').startswith('image/'):
            messages.error(request, 'Todos los archivos de evidencia deben ser imagenes.')
            return redirect('pedido_detalle_panel', pedido_id=pedido_id)

    with transaction.atomic():
        pedido = get_object_or_404(
            Pedido.objects.select_for_update().prefetch_related('detalles', 'evidencias'),
            pk=pedido_id,
        )

        evidencias_existentes = pedido.evidencias.count()
        if evidencias_existentes + len(evidencias_subidas) > 8:
            messages.error(request, 'Este pedido ya tiene evidencias. El maximo total permitido es 8 fotos.')
            return redirect('pedido_detalle_panel', pedido_id=pedido_id)

        if pedido.estado != 'esperando entrega':
            messages.error(request, 'Solo se puede confirmar entrega en pedidos en estado esperando entrega.')
            return redirect('pedido_detalle_panel', pedido_id=pedido_id)

        if not pedido.codigo_entrega or not pedido.codigo_expira_en:
            messages.error(request, 'Este pedido no tiene codigo de entrega activo.')
            return redirect('pedido_detalle_panel', pedido_id=pedido_id)

        now = timezone.now()
        if now > pedido.codigo_expira_en:
            pedido.codigo_entrega = f'{secrets.randbelow(1000000):06d}'
            pedido.codigo_expira_en = now + timedelta(hours=2)
            pedido.fch_ult_act = now
            pedido.save(update_fields=['codigo_entrega', 'codigo_expira_en', 'fch_ult_act'])
            messages.error(request, 'El codigo estaba vencido. Se genero uno nuevo con vigencia de 2 horas.')
            return redirect('pedido_detalle_panel', pedido_id=pedido_id)

        if codigo_ingresado != pedido.codigo_entrega:
            messages.error(request, 'Codigo incorrecto. No se pudo confirmar la entrega.')
            return redirect('pedido_detalle_panel', pedido_id=pedido_id)

        now = timezone.now()
        if evidencias_subidas:
            PedidoEvidencia.objects.bulk_create([
                PedidoEvidencia(
                    id_pedido_fk=pedido,
                    foto_evidencia=archivo,
                    fch_registro=now,
                )
                for archivo in evidencias_subidas
            ])

        pedido.estado = 'entregado'
        pedido.codigo_entrega = None
        pedido.codigo_expira_en = None
        pedido.fch_ult_act = now
        pedido.save(update_fields=['estado', 'codigo_entrega', 'codigo_expira_en', 'fch_ult_act'])

        DetallePedido.objects.filter(id_pedido_fk=pedido).exclude(
            estado_detalle__in=['no_disponible', 'rechazado', 'cancelado']
        ).update(
            estado_detalle='entregado',
            fch_ult_act=now,
        )

    _registrar_auditoria(
        request,
        accion='actualizar',
        entidad='pedido',
        entidad_id=pedido.id_pedido,
        descripcion=f'Pedido #{pedido.id_pedido} fue confirmado como entregado en almacén.',
    )
    messages.success(request, f'Pedido #{pedido.id_pedido} marcado como entregado.')
    _crear_notificacion(
        usuario=pedido.id_usuario_fk,
        tipo='entregado',
        titulo='Pedido entregado',
        mensaje=f'Tu pedido #{pedido.id_pedido} fue entregado correctamente. '
                f'Recuerda devolver los materiales en la fecha acordada.',
        pedido_id=pedido.id_pedido,
    )
    _notificar_staff(
        tipo='staff_pedido_entregado',
        titulo=f'Pedido #{pedido.id_pedido} entregado',
        mensaje=f'El pedido #{pedido.id_pedido} fue confirmado como entregado por {request.user.nombre or request.user.correo}.',
        pedido_id=pedido.id_pedido,
    )
    return redirect('pedido_detalle_panel', pedido_id=pedido_id)


@login_required
def pedido_marcar_devuelto(request, pedido_id):
    if not request.user.id_rol_fk or request.user.id_rol_fk.nombre_rol not in ['admin', 'almacenista']:
        return redirect('dashboard')

    if request.method != 'POST':
        return redirect('prestamos_panel')

    codigo_ingresado = (request.POST.get('codigo_devolucion') or '').strip()
    if not (len(codigo_ingresado) == 6 and codigo_ingresado.isdigit()):
        messages.error(request, 'Debes ingresar un código de devolución válido de 6 dígitos.')
        return redirect('prestamos_panel')

    with transaction.atomic():
        pedido = get_object_or_404(
            Pedido.objects.select_for_update().prefetch_related('detalles__id_prod_fk'),
            pk=pedido_id,
        )

        if pedido.estado != 'entregado':
            messages.error(request, 'Solo puedes marcar como devuelto un préstamo actualmente entregado.')
            return redirect('prestamos_panel')

        now = timezone.now()

        if not pedido.codigo_entrega or not pedido.codigo_expira_en:
            _renovar_codigo_devolucion(pedido, now)
            messages.error(request, 'No había un código activo. Se generó uno nuevo para el usuario.')
            return redirect('prestamos_panel')

        if now > pedido.codigo_expira_en:
            _renovar_codigo_devolucion(pedido, now)
            messages.error(request, 'El código de devolución venció. Pide al usuario el nuevo código dinámico.')
            return redirect('prestamos_panel')

        if codigo_ingresado != pedido.codigo_entrega:
            messages.error(request, 'Código de devolución incorrecto. Verifica la clave dinámica del usuario.')
            return redirect('prestamos_panel')

        detalles_entregados = list(
            DetallePedido.objects
            .select_for_update()
            .select_related('id_prod_fk')
            .filter(id_pedido_fk=pedido)
            .exclude(estado_detalle__in=['no_disponible', 'rechazado', 'cancelado'])
        )

        for detalle in detalles_entregados:
            _sumar_stock_disponibilidad(detalle, now)

        pedido.estado = 'devuelto'
        pedido.codigo_entrega = None
        pedido.codigo_expira_en = None
        pedido.fch_ult_act = now
        pedido.save(update_fields=['estado', 'codigo_entrega', 'codigo_expira_en', 'fch_ult_act'])

        DetallePedido.objects.filter(id_pedido_fk=pedido).exclude(
            estado_detalle__in=['no_disponible', 'rechazado', 'cancelado']
        ).update(
            estado_detalle='devuelto',
            fch_ult_act=now,
        )

    _registrar_auditoria(
        request,
        accion='actualizar',
        entidad='prestamo',
        entidad_id=pedido.id_pedido,
        descripcion=f'Préstamo #{pedido.id_pedido} recibido en devolución y stock restaurado.',
    )
    messages.success(request, f'Préstamo #{pedido.id_pedido} marcado como devuelto y el stock fue restaurado.')
    return redirect('prestamos_panel')


@login_required
def pedido_rechazar(request, pedido_id):
    if not request.user.id_rol_fk or request.user.id_rol_fk.nombre_rol not in ['admin', 'almacenista']:
        return redirect('dashboard')

    if request.method != 'POST':
        return redirect('pedido_detalle_panel', pedido_id=pedido_id)

    with transaction.atomic():
        pedido = get_object_or_404(Pedido.objects.select_for_update(), pk=pedido_id)

        if pedido.estado != 'pendiente':
            messages.error(request, 'Solo se pueden rechazar pedidos en estado pendiente.')
            return redirect('pedido_detalle_panel', pedido_id=pedido_id)

        now = timezone.now()
        pedido.estado = 'rechazado'
        pedido.fch_ult_act = now
        pedido.save(update_fields=['estado', 'fch_ult_act'])

        DetallePedido.objects.filter(id_pedido_fk=pedido).update(
            estado_detalle='rechazado',
            fch_ult_act=now,
        )

    _registrar_auditoria(
        request,
        accion='actualizar',
        entidad='pedido',
        entidad_id=pedido.id_pedido,
        descripcion=f'Pedido #{pedido.id_pedido} fue cancelado/rechazado por personal de almacén.',
    )
    messages.success(request, f'Pedido #{pedido_id} rechazado correctamente.')
    _crear_notificacion(
        usuario=pedido.id_usuario_fk,
        tipo='rechazado',
        titulo='Pedido rechazado',
        mensaje=f'Tu pedido #{pedido.id_pedido} fue rechazado por el almacenista. '
                f'Si tienes dudas, comunícate con el área de almacén.',
        pedido_id=pedido.id_pedido,
    )
    return redirect('pedido_detalle_panel', pedido_id=pedido_id)


@login_required
def pedido_marcar_no_disponibles(request, pedido_id):
    if not request.user.id_rol_fk or request.user.id_rol_fk.nombre_rol not in ['admin', 'almacenista']:
        return redirect('dashboard')

    if request.method != 'POST':
        return redirect('pedido_detalle_panel', pedido_id=pedido_id)

    detalle_ids_raw = request.POST.getlist('detalle_no_disponible')
    try:
        detalle_ids = [int(d) for d in detalle_ids_raw]
    except (ValueError, TypeError):
        messages.error(request, 'Seleccion de productos invalida.')
        return redirect('pedido_detalle_panel', pedido_id=pedido_id)

    with transaction.atomic():
        pedido = get_object_or_404(Pedido.objects.select_for_update(), pk=pedido_id)

        if pedido.estado != 'pendiente':
            messages.error(request, 'Solo se pueden modificar detalles en pedidos pendientes.')
            return redirect('pedido_detalle_panel', pedido_id=pedido_id)

        now = timezone.now()

        # Restaurar a 'pendiente' los que ya habian sido marcados no_disponible pero no se checkaron
        DetallePedido.objects.filter(
            id_pedido_fk=pedido,
            estado_detalle='no_disponible',
        ).exclude(id_det_pedido__in=detalle_ids).update(
            estado_detalle='pendiente',
            fch_ult_act=now,
        )

        if detalle_ids:
            DetallePedido.objects.filter(
                id_pedido_fk=pedido,
                id_det_pedido__in=detalle_ids,
            ).update(
                estado_detalle='no_disponible',
                fch_ult_act=now,
            )

    total = len(detalle_ids)
    if total:
        _registrar_auditoria(
            request,
            accion='actualizar',
            entidad='pedido',
            entidad_id=pedido.id_pedido,
            descripcion=f'Pedido #{pedido.id_pedido}: {total} producto(s) marcado(s) como no disponible.',
        )
        messages.success(request, f'{total} producto{"s" if total != 1 else ""} marcado{"s" if total != 1 else ""} como no disponible.')
        _crear_notificacion(
            usuario=pedido.id_usuario_fk,
            tipo='no_disponible',
            titulo='Algunos productos no están disponibles',
            mensaje=(
                f'En tu pedido #{pedido.id_pedido}, {total} '
                + ('productos no están disponibles. ' if total != 1 else 'producto no está disponible. ')
                + 'El resto del pedido continúa en proceso.'
            ),
            pedido_id=pedido.id_pedido,
        )
    else:
        messages.success(request, 'Se restauraron todos los productos a estado pendiente.')
    return redirect('pedido_detalle_panel', pedido_id=pedido_id)


@login_required
def auditorias_panel(request):
    if not _is_admin_or_almacenista(request):
        return redirect('dashboard')

    q = (request.GET.get('q') or '').strip()
    accion = (request.GET.get('accion') or '').strip().lower()
    entidad = (request.GET.get('entidad') or '').strip().lower()
    rol = (request.GET.get('rol') or '').strip().lower()

    logs = AuditoriaLog.objects.select_related('id_usuario_fk__id_rol_fk')

    if q:
        logs = logs.filter(
            models.Q(descripcion__icontains=q)
            | models.Q(entidad_id__icontains=q)
            | models.Q(id_usuario_fk__correo__icontains=q)
            | models.Q(id_usuario_fk__nombre__icontains=q)
            | models.Q(id_usuario_fk__apellido__icontains=q)
        )

    if accion:
        logs = logs.filter(accion=accion)
    if entidad:
        logs = logs.filter(entidad=entidad)
    if rol:
        logs = logs.filter(rol_usuario=rol)

    logs = list(logs.order_by('-fch_registro', '-id_log')[:300])
    resumen_accion = {
        'crear': sum(1 for item in logs if item.accion == 'crear'),
        'actualizar': sum(1 for item in logs if item.accion == 'actualizar'),
        'eliminar': sum(1 for item in logs if item.accion == 'eliminar'),
    }

    return render(request, 'inventario/auditorias/panel_auditorias.html', {
        'logs': logs,
        'q': q,
        'accion_activa': accion,
        'entidad_activa': entidad,
        'rol_activo': rol,
        'resumen_accion': resumen_accion,
    })

@login_required
def gestion_usuarios_panel(request):
    if not (request.user.id_rol_fk and request.user.id_rol_fk.nombre_rol == 'admin'):
        messages.error(request, 'Solo el administrador puede gestionar usuarios.')
        return redirect('dashboard')

    query = request.GET.get('q', '').strip()
    base_usuarios = Usuario.objects.all().select_related('id_rol_fk')
    usuarios = base_usuarios.order_by('nombre', 'apellido')
    if query:
        usuarios = usuarios.filter(
            models.Q(nombre__icontains=query) |
            models.Q(apellido__icontains=query) |
            models.Q(correo__icontains=query) |
            models.Q(cc__icontains=query)
        )
    roles = Rol.objects.all().order_by('nombre_rol')
    resumen = {
        'total_usuarios': base_usuarios.count(),
        'total_activos': base_usuarios.filter(is_active=True).count(),
        'total_admins': base_usuarios.filter(id_rol_fk__nombre_rol='admin').count(),
        'total_visibles': usuarios.count(),
    }
    return render(request, 'inventario/usuarios/panel_usuarios.html', {
        'usuarios': usuarios,
        'query': query,
        'roles': roles,
        'resumen': resumen,
    })


from django.views.decorators.http import require_POST
@login_required
@require_POST
def crear_usuario(request):
    if not (request.user.id_rol_fk and request.user.id_rol_fk.nombre_rol == 'admin'):
        messages.error(request, 'Solo el administrador puede crear usuarios.')
        return redirect('gestion_usuarios_panel')

    cc = request.POST.get('cc', '').strip()
    nombre = request.POST.get('nombre', '').strip()
    apellido = request.POST.get('apellido', '').strip()
    correo = request.POST.get('correo', '').strip()
    password = request.POST.get('password', '').strip()
    id_rol_fk = request.POST.get('id_rol_fk')
    if not (cc and nombre and apellido and correo and password and id_rol_fk):
        messages.error(request, 'Todos los campos son obligatorios.')
        return redirect('gestion_usuarios_panel')
    if Usuario.objects.filter(correo=correo).exists():
        messages.error(request, 'Ya existe un usuario con ese correo.')
        return redirect('gestion_usuarios_panel')
    if Usuario.objects.filter(cc=cc).exists():
        messages.error(request, 'Ya existe un usuario con esa cédula.')
        return redirect('gestion_usuarios_panel')
    try:
        rol = Rol.objects.get(pk=id_rol_fk)
    except Rol.DoesNotExist:
        messages.error(request, 'Rol inválido.')
        return redirect('gestion_usuarios_panel')
    usuario = Usuario(
        cc=cc,
        nombre=nombre,
        apellido=apellido,
        correo=correo,
        id_rol_fk=rol,
        is_active=True,
    )
    usuario.set_password(password)
    usuario.save()
    _registrar_auditoria(
        request,
        accion='crear',
        entidad='usuario',
        entidad_id=usuario.id_usu,
        descripcion=f'Se creó el usuario {usuario.correo} con rol {rol.nombre_rol}.',
    )
    return redirect('gestion_usuarios_panel')

@login_required
@require_POST
def editar_rol_usuario(request, usuario_id):
    if not (request.user.id_rol_fk and request.user.id_rol_fk.nombre_rol == 'admin'):
        messages.error(request, 'Solo el administrador puede editar roles.')
        return redirect('gestion_usuarios_panel')

    usuario = Usuario.objects.get(pk=usuario_id)
    nuevo_rol_id = request.POST.get('id_rol_fk')
    if not nuevo_rol_id:
        messages.error(request, 'Debes seleccionar un rol.')
        return redirect('gestion_usuarios_panel')
    try:
        nuevo_rol = Rol.objects.get(pk=nuevo_rol_id)
    except Rol.DoesNotExist:
        messages.error(request, 'Rol inválido.')
        return redirect('gestion_usuarios_panel')
    # No permitir cambiar el rol de admin
    if usuario.id_rol_fk and usuario.id_rol_fk.nombre_rol == 'admin':
        messages.error(request, 'No puedes editar el rol de un usuario admin.')
        return redirect('gestion_usuarios_panel')
    usuario.id_rol_fk = nuevo_rol
    usuario.save()
    _registrar_auditoria(
        request,
        accion='actualizar',
        entidad='usuario',
        entidad_id=usuario.id_usu,
        descripcion=f'Se actualizó el rol del usuario {usuario.correo} a {nuevo_rol.nombre_rol}.',
    )
    return redirect('gestion_usuarios_panel')


@login_required
@require_POST
def toggle_estado_usuario(request, usuario_id):
    if not (request.user.id_rol_fk and request.user.id_rol_fk.nombre_rol == 'admin'):
        messages.error(request, 'No tienes permisos para cambiar el estado de usuarios.')
        return redirect('gestion_usuarios_panel')

    usuario = get_object_or_404(Usuario, pk=usuario_id)

    if usuario.id_usu == request.user.id_usu:
        messages.error(request, 'No puedes desactivar tu propia cuenta desde esta sesión.')
        return redirect('gestion_usuarios_panel')

    usuario.is_active = not usuario.is_active
    usuario.save(update_fields=['is_active'])

    accion = 'activado' if usuario.is_active else 'desactivado'
    _registrar_auditoria(
        request,
        accion='actualizar',
        entidad='usuario',
        entidad_id=usuario.id_usu,
        descripcion=f'Se dejó {accion} el acceso del usuario {usuario.correo}.',
    )
    return redirect('gestion_usuarios_panel')


@login_required
@require_POST
def eliminar_usuario(request, usuario_id):
    if not (request.user.id_rol_fk and request.user.id_rol_fk.nombre_rol == 'admin'):
        messages.error(request, 'No tienes permisos para eliminar usuarios.')
        return redirect('gestion_usuarios_panel')

    usuario = get_object_or_404(Usuario, pk=usuario_id)

    if usuario.id_usu == request.user.id_usu:
        messages.error(request, 'No puedes eliminar tu propia cuenta desde esta sesión.')
        return redirect('gestion_usuarios_panel')

    nombre_completo = ' '.join(filter(None, [usuario.nombre, usuario.apellido])).strip() or 'Sin nombre'
    correo = usuario.correo
    entidad_id = usuario.id_usu

    try:
        usuario.delete()
    except Exception:
        messages.error(request, 'No se pudo eliminar el usuario. Verifica si tiene información relacionada.')
        return redirect('gestion_usuarios_panel')

    _registrar_auditoria(
        request,
        accion='eliminar',
        entidad='usuario',
        entidad_id=entidad_id,
        descripcion=f'Se eliminó el usuario {nombre_completo} ({correo}).',
    )
    messages.success(request, f'Usuario eliminado: {nombre_completo} ({correo}).')
    return redirect('gestion_usuarios_panel')


@login_required
@require_POST
def enviar_enlace_validacion_sena(request, usuario_id):
    next_url = (request.POST.get('next') or request.GET.get('next') or '').strip()

    def _redirect_admin_default():
        if next_url and next_url.startswith('/') and not next_url.startswith('//'):
            return redirect(next_url)
        return redirect('gestion_usuarios_panel')

    if not (request.user.id_rol_fk and request.user.id_rol_fk.nombre_rol == 'admin'):
        messages.error(request, 'Solo el administrador puede enviar enlaces de validación SENA.')
        return _redirect_admin_default()

    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if usuario.verificacion_sena_estado == 'validado':
        messages.success(request, 'Ese usuario ya tiene la validación SENA aprobada.')
        return _redirect_admin_default()

    if usuario.verificacion_sena_estado in {'enlace_enviado', 'documento_cargado'}:
        messages.error(request, 'No puedes reenviar enlace a este usuario hasta que el admin apruebe o rechace su caso.')
        return _redirect_admin_default()

    if usuario.verificacion_sena_estado != 'solicitada':
        messages.error(request, 'Este usuario no tiene una solicitud manual pendiente para enviar enlace.')
        return _redirect_admin_default()

    token = VerificacionSenaToken.create_for_user(usuario)
    upload_url = request.build_absolute_uri(reverse('validacion_sena_carga_manual', args=[token.token]))
    ahora = timezone.now()
    usuario.verificacion_sena_estado = 'enlace_enviado'
    usuario.verificacion_sena_solicitada_en = usuario.verificacion_sena_solicitada_en or ahora
    usuario.verificacion_sena_observacion = 'Administración envió enlace manual para cargar carnet o certificado SENA.'
    usuario.save(update_fields=[
        'verificacion_sena_estado',
        'verificacion_sena_solicitada_en',
        'verificacion_sena_observacion',
    ])

    correo = getattr(usuario, 'correo', None)
    if correo:
        try:
            from django.core.mail import EmailMultiAlternatives

            subject = 'Enlace de validación manual SENA'
            nombre_usuario = usuario.nombre or usuario.correo
            text_content = (
                f'Hola {nombre_usuario},\n\n'
                'El administrador aprobó tu solicitud de validación manual.\n'
                'Usa este enlace único para cargar la foto de tu carnet o un certificado vigente del SENA:\n'
                f'{upload_url}\n\n'
                'El enlace vencerá en 4 horas y solo podrá usarse una vez.'
            )
            html_content = f"""
<!DOCTYPE html>
<html lang=\"es\">
<head><meta charset=\"UTF-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"></head>
<body style=\"margin:0;padding:0;background:#f3f7f2;font-family:Arial,Helvetica,sans-serif;color:#1f2937;\">
  <table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" style=\"padding:24px 12px;\">
    <tr><td align=\"center\">
      <table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" style=\"max-width:640px;background:#ffffff;border-radius:22px;overflow:hidden;box-shadow:0 12px 30px rgba(11,71,55,.12);\">
        <tr><td style=\"background:linear-gradient(135deg,#0b4737,#39A900);padding:28px 32px;color:#fff;\">
          <p style=\"margin:0 0 8px;font-size:13px;letter-spacing:1.6px;font-weight:bold;text-transform:uppercase;opacity:.9;\">SENA · Inventario</p>
          <h1 style=\"margin:0;font-size:28px;line-height:1.15;\">Carga tu evidencia manual</h1>
        </td></tr>
        <tr><td style=\"padding:32px;\">
          <p style=\"margin:0 0 14px;font-size:16px;line-height:1.6;\">Hola <strong>{nombre_usuario}</strong>,</p>
          <p style=\"margin:0 0 18px;font-size:15px;line-height:1.7;color:#475569;\">Ya puedes cargar la foto de tu carnet SENA o un certificado que confirme que estudias en el SENA. Esta revisión será manual.</p>
          <table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" style=\"margin:24px 0;\"><tr><td align=\"center\"><a href=\"{upload_url}\" style=\"display:inline-block;background:#39A900;color:#fff;text-decoration:none;font-weight:700;padding:14px 26px;border-radius:999px;font-size:15px;\">Cargar documento</a></td></tr></table>
          <p style=\"margin:0 0 10px;font-size:14px;line-height:1.7;color:#64748b;\">Si el botón no funciona, usa este enlace:</p>
          <p style=\"margin:0;font-size:13px;line-height:1.7;word-break:break-all;\"><a href=\"{upload_url}\" style=\"color:#0b4737;\">{upload_url}</a></p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>
"""
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                to=[correo],
            )
            email.attach_alternative(html_content, 'text/html')
            email.send(fail_silently=False)
        except Exception:
            messages.error(request, 'No se pudo enviar el correo, pero el enlace quedó generado para reintentar.')

    _crear_notificacion(
        usuario=usuario,
        tipo='enlace_validacion_sena',
        titulo='Enlace de validación SENA enviado',
        mensaje='Revisa tu correo. Te enviamos un enlace único para cargar la foto del carnet o un certificado vigente del SENA.',
    )
    _registrar_auditoria(
        request,
        accion='actualizar',
        entidad='usuario',
        entidad_id=usuario.id_usu,
        descripcion=f'Se envió enlace manual de validación SENA al usuario {usuario.correo}.',
    )
    messages.success(request, f'Se envió el enlace manual de validación a {usuario.correo}.')
    return _redirect_admin_default()


@login_required
@require_POST
def aprobar_validacion_sena(request, usuario_id):
    next_url = (request.POST.get('next') or request.GET.get('next') or '').strip()

    def _redirect_admin_default():
        if next_url and next_url.startswith('/') and not next_url.startswith('//'):
            return redirect(next_url)
        return redirect('gestion_usuarios_panel')

    if not (request.user.id_rol_fk and request.user.id_rol_fk.nombre_rol == 'admin'):
        messages.error(request, 'Solo el administrador puede aprobar validaciones SENA.')
        return _redirect_admin_default()

    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if not usuario.verificacion_sena_documento and not usuario.verificacion_sena_imagen:
        messages.error(request, 'Ese usuario todavía no ha cargado ninguna evidencia para revisar.')
        return _redirect_admin_default()

    usuario.verificacion_sena_estado = 'validado'
    usuario.verificacion_sena_validada_en = timezone.now()
    usuario.verificacion_sena_observacion = 'Validación manual aprobada por administración.'
    usuario.save(update_fields=[
        'verificacion_sena_estado',
        'verificacion_sena_validada_en',
        'verificacion_sena_observacion',
    ])

    _crear_notificacion(
        usuario=usuario,
        tipo='verificacion_sena_aprobada',
        titulo='Validación SENA aprobada',
        mensaje='El administrador aprobó tu verificación manual. Ya puedes realizar pedidos normalmente.',
    )
    _registrar_auditoria(
        request,
        accion='actualizar',
        entidad='usuario',
        entidad_id=usuario.id_usu,
        descripcion=f'Se aprobó manualmente la validación SENA del usuario {usuario.correo}.',
    )
    messages.success(request, f'La validación SENA de {usuario.correo} fue aprobada.')
    return _redirect_admin_default()


@login_required
@require_POST
def rechazar_validacion_sena(request, usuario_id):
    next_url = (request.POST.get('next') or request.GET.get('next') or '').strip()

    def _redirect_admin_default():
        if next_url and next_url.startswith('/') and not next_url.startswith('//'):
            return redirect(next_url)
        return redirect('gestion_usuarios_panel')

    if not (request.user.id_rol_fk and request.user.id_rol_fk.nombre_rol == 'admin'):
        messages.error(request, 'Solo el administrador puede rechazar validaciones SENA.')
        return _redirect_admin_default()

    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if not usuario.verificacion_sena_documento and not usuario.verificacion_sena_imagen:
        messages.error(request, 'Ese usuario todavía no ha cargado ninguna evidencia para revisar.')
        return _redirect_admin_default()

    motivo_rechazo = (request.POST.get('motivo_rechazo') or '').strip()
    observacion = 'Validación manual rechazada por administración.'
    if motivo_rechazo:
        observacion = f'{observacion} Motivo: {motivo_rechazo}'

    usuario.verificacion_sena_estado = 'rechazada'
    usuario.verificacion_sena_observacion = observacion
    usuario.save(update_fields=[
        'verificacion_sena_estado',
        'verificacion_sena_observacion',
    ])

    mensaje_rechazo = 'La revisión manual de tu validación SENA fue rechazada por el administrador.'
    if motivo_rechazo:
        mensaje_rechazo = f'{mensaje_rechazo} Motivo: {motivo_rechazo}'

    _crear_notificacion(
        usuario=usuario,
        tipo='verificacion_sena_rechazada',
        titulo='Validación SENA rechazada',
        mensaje=mensaje_rechazo,
    )
    _registrar_auditoria(
        request,
        accion='actualizar',
        entidad='usuario',
        entidad_id=usuario.id_usu,
        descripcion=f'Se rechazó manualmente la validación SENA del usuario {usuario.correo}. Motivo: {motivo_rechazo or "sin motivo"}.',
    )
    messages.success(request, f'La validación SENA de {usuario.correo} fue rechazada.')
    return _redirect_admin_default()


# ─────────────────────────────────────────────────────────────────────────────
# Panel de Notificaciones (usuario)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def notificaciones_panel(request):
    # Auto-marcar todas como leídas al entrar al panel
    Notificacion.objects.filter(id_usuario_fk=request.user, leida=False).update(leida=True)
    notificaciones = (
        Notificacion.objects
        .filter(id_usuario_fk=request.user)
        .order_by('-fch_registro')
    )
    return render(request, 'inventario/usuario/panel_notificaciones.html', {
        'notificaciones': notificaciones,
    })


@login_required
@require_POST
def notificacion_marcar_leida(request, noti_id):
    noti = get_object_or_404(Notificacion, pk=noti_id, id_usuario_fk=request.user)
    noti.leida = True
    noti.save(update_fields=['leida'])
    return redirect('notificaciones_panel')


@login_required
@require_POST
def notificaciones_marcar_todas_leidas(request):
    Notificacion.objects.filter(id_usuario_fk=request.user, leida=False).update(leida=True)
    return redirect('notificaciones_panel')


# ─────────────────────────────────────────────────────────────────────────────
# Aviso de devolución (almacenista → usuario)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
@require_POST
def pedido_aviso_devolucion(request, pedido_id):
    if not request.user.id_rol_fk or request.user.id_rol_fk.nombre_rol not in ['admin', 'almacenista']:
        return redirect('dashboard')

    pedido = get_object_or_404(Pedido, pk=pedido_id, estado='entregado')
    usuario = pedido.id_usuario_fk
    _registrar_auditoria(
        request,
        accion='actualizar',
        entidad='prestamo',
        entidad_id=pedido.id_pedido,
        descripcion=f'Se envió aviso de devolución para el préstamo #{pedido.id_pedido}.',
    )
    _crear_notificacion(
        usuario=usuario,
        tipo='aviso_devolucion',
        titulo='Aviso de devolución pendiente',
        mensaje=f'El almacenista solicita que devuelvas los materiales del pedido #{pedido.id_pedido}. '
                f'Por favor, acércate al almacén a la brevedad posible.',
        pedido_id=pedido.id_pedido,
    )

    # ── Correo al usuario ─────────────────────────────────────────────────
    correo = getattr(usuario, 'correo', None) or getattr(usuario, 'email', None)
    if correo:
        try:
            from django.core.mail import EmailMultiAlternatives
            nombre = getattr(usuario, 'nombre', '') or str(usuario)
            fecha_str = pedido.fecha_devolucion.strftime('%d/%m/%Y') if pedido.fecha_devolucion else '—'
            remitente = settings.DEFAULT_FROM_EMAIL

            # Productos a devolver (solo los activos, no rechazados/cancelados)
            detalles = list(pedido.detalles.exclude(
                estado_detalle__in=['no_disponible', 'rechazado', 'cancelado']
            ).select_related('id_prod_fk'))

            # URL base para imágenes (usar dominio absoluto para que funcione en correos)
            base_url = 'https://almacensedelacolonia.pythonanywhere.com'

            # Construir filas de productos para el correo
            filas_html = ''
            lista_texto = ''
            for d in detalles:
                prod = d.id_prod_fk
                img_url = (
                    f'{base_url}{settings.MEDIA_URL}{prod.fot_prod}'
                    if prod and prod.fot_prod else ''
                )
                img_tag = (
                    f'<img src="{img_url}" alt="{d.nombre_producto}" '
                    f'width="48" height="48" '
                    f'style="border-radius:6px;object-fit:cover;display:block;">'
                    if img_url else
                    '<div style="width:48px;height:48px;background:#e8f5e9;'
                    'border-radius:6px;display:flex;align-items:center;'
                    'justify-content:center;font-size:20px;">📦</div>'
                )
                filas_html += f"""
                <tr>
                  <td style="padding:10px 12px;border-bottom:1px solid #f0f0f0;width:68px;">
                    {img_tag}
                  </td>
                  <td style="padding:10px 12px;border-bottom:1px solid #f0f0f0;
                              font-size:14px;color:#333;">{d.nombre_producto}</td>
                  <td style="padding:10px 12px;border-bottom:1px solid #f0f0f0;
                              font-size:14px;color:#555;text-align:center;
                              white-space:nowrap;">x{d.cantidad_solicitada}</td>
                </tr>"""
                lista_texto += f'  - {d.nombre_producto} x{d.cantidad_solicitada}\n'

            tabla_productos = f"""
            <p style="font-size:15px;font-weight:700;color:#1a2e1a;margin:24px 0 8px;">
              📋 Productos a devolver:
            </p>
            <table width="100%" cellpadding="0" cellspacing="0"
                   style="border:1px solid #e0e0e0;border-radius:8px;overflow:hidden;">
              <thead>
                <tr style="background:#f5f5f5;">
                  <th style="padding:10px 12px;text-align:left;font-size:13px;
                              color:#666;font-weight:600;width:68px;">Foto</th>
                  <th style="padding:10px 12px;text-align:left;font-size:13px;
                              color:#666;font-weight:600;">Producto</th>
                  <th style="padding:10px 12px;text-align:center;font-size:13px;
                              color:#666;font-weight:600;">Cant.</th>
                </tr>
              </thead>
              <tbody>{filas_html}</tbody>
            </table>""" if detalles else ''

            asunto = f'📦 Recordatorio de devolución – Pedido #{pedido.id_pedido} | Almacén SENA Sibaté'
            texto_plano = (
                f'Hola {nombre},\n\n'
                f'El almacenista te recuerda que debes devolver los materiales del '
                f'pedido #{pedido.id_pedido} (fecha límite: {fecha_str}).\n\n'
                + (f'Productos a devolver:\n{lista_texto}\n' if lista_texto else '')
                + 'Por favor, acércate al almacén a la brevedad posible.\n\n'
                '— Almacén SENA Sibaté'
            )
            html = f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f4f4f4;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f4;padding:32px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0"
             style="background:#fff;border-radius:12px;overflow:hidden;
                    box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:600px;width:100%;">
        <tr>
          <td style="background:#39A900;padding:28px 32px;text-align:center;">
            <p style="margin:0;color:#fff;font-size:13px;opacity:0.85;">SENA — Almacén Sibaté</p>
            <h1 style="margin:8px 0 0;color:#fff;font-size:24px;">📦 Recordatorio de devolución</h1>
          </td>
        </tr>
        <tr>
          <td style="padding:32px;">
            <p style="font-size:16px;color:#333;">Hola <strong>{nombre}</strong>,</p>
            <p style="font-size:15px;color:#444;line-height:1.6;">
              El almacenista te recuerda que tienes pendiente la devolución de los materiales
              del préstamo <strong>#{pedido.id_pedido}</strong>
              {"(fecha límite: <strong>" + fecha_str + "</strong>)" if pedido.fecha_devolucion else ""}.
            </p>
            {tabla_productos}
            <table width="100%" cellpadding="0" cellspacing="0" style="margin:24px 0;">
              <tr>
                <td style="background:#e8f5e9;border-left:4px solid #39A900;
                            border-radius:6px;padding:16px 20px;">
                  <p style="margin:0;font-size:15px;color:#333;">
                    Por favor <strong>acércate al almacén</strong> a la brevedad posible
                    para hacer la devolución.
                  </p>
                </td>
              </tr>
            </table>
            <p style="font-size:13px;color:#888;margin-top:32px;">
              Si ya devolviste los materiales, ignora este mensaje.<br>
              — Almacén SENA Sibaté
            </p>
          </td>
        </tr>
        <tr>
          <td style="background:#f9f9f9;padding:16px 32px;text-align:center;
                      border-top:1px solid #eee;">
            <p style="margin:0;font-size:12px;color:#aaa;">
              Centro Industrial y de Desarrollo Empresarial – Sibaté, Cundinamarca
            </p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""
            msg = EmailMultiAlternatives(asunto, texto_plano, remitente, [correo])
            msg.attach_alternative(html, 'text/html')
            msg.send()
            messages.success(request, f'Aviso enviado al usuario y correo enviado a {correo}.')
        except Exception as e:
            messages.warning(request, f'Aviso interno enviado, pero el correo falló: {e}')
    else:
        messages.success(request, f'Aviso de devolución enviado al usuario del pedido #{pedido_id}.')

    return redirect('prestamos_panel')


