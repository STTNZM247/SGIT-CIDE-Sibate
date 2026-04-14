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
    return request.user.id_rol_fk and request.user.id_rol_fk.nombre_rol in ["usuario", "aprendiz", "instructor"]


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
