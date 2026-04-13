import secrets
from datetime import timedelta

from django.http import Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from .models import Catalogo, DetallePedido, Disponibilidad, Notificacion, Pedido, PedidoEvidencia, Producto, Rol
from .forms import ProductoForm


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
    return render(request, 'inventario/almacenista/panel_almacenista.html')
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db import transaction
from django.db.models import OuterRef, Subquery
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CatalogoForm, ProductoForm, UsuarioPerfilForm
from .models import Catalogo, DetallePedido, Disponibilidad, Pedido, PedidoEvidencia, Producto, Usuario, Rol


def _user_role(request):
    if not request.user.is_authenticated or not request.user.id_rol_fk:
        return None
    return request.user.id_rol_fk.nombre_rol


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
            catalogo.delete()
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
        producto.delete()
        messages.success(request, f'Producto "{nombre}" eliminado correctamente.')

    return redirect('productos_catalogo', cat_id=cat_id)



@login_required
def dashboard(request):
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
        ids_bajo = Disponibilidad.objects.filter(cantidad__lte=5).values_list('id_prod_fk_id', flat=True)
        productos_qs = productos_qs.filter(id_prod__in=ids_bajo)

    productos = list(productos_qs.order_by('-fch_registro', '-id_prod'))

    total_productos = Producto.objects.count()
    productos_bajo_stock = Disponibilidad.objects.filter(cantidad__lte=5).count()

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
        'inventario/dashboard/index.html',
        {
            'q': q,
            'categoria_activa': cat_id,
            'bajo_stock': bajo_stock,
            'catalogos': catalogos,
            'productos': productos,
            'secciones_catalogo': secciones_catalogo,
            'total_productos': total_productos,
            'productos_bajo_stock': productos_bajo_stock,
        },
    )


@login_required
def perfil_usuario(request):
    usuario = request.user
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
    return render(request, 'inventario/usuario/perfil_usuario.html', {'form': form, 'usuario': usuario})


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
def prestamos_panel(request):
    if not request.user.id_rol_fk or request.user.id_rol_fk.nombre_rol not in ['admin', 'almacenista']:
        return redirect('dashboard')

    ahora = timezone.now()
    prestamos = list(
        Pedido.objects
        .filter(estado__in=['entregado', 'rechazado'])
        .select_related('id_usuario_fk')
        .prefetch_related('detalles')
        .order_by('fecha_devolucion', '-fch_registro')
    )

    for prestamo in prestamos:
        detalles = list(prestamo.detalles.all())
        # Los cancelados nunca se entregaron: sin vencimiento
        if prestamo.estado == 'rechazado':
            prestamo.fecha_devolucion_display = None
            prestamo.es_vencido = False
            prestamo.dias_restantes = None
            prestamo.dias_vencido = 0
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
            else:
                prestamo.fecha_devolucion_display = None
                prestamo.es_vencido = False
                prestamo.dias_restantes = None
                prestamo.dias_vencido = 0
        else:
            prestamo.fecha_devolucion_display = prestamo.fecha_devolucion
            if prestamo.fecha_devolucion:
                prestamo.es_vencido = prestamo.fecha_devolucion < ahora
                delta = prestamo.fecha_devolucion - ahora
                prestamo.dias_restantes = delta.days
                prestamo.dias_vencido = abs(delta.days) if prestamo.es_vencido else 0
            else:
                prestamo.es_vencido = False
                prestamo.dias_restantes = None
                prestamo.dias_vencido = 0
        prestamo.detalles_lista = detalles

    # Ordenar: vencidos primero, luego por fecha de devolución más próxima
    prestamos.sort(key=lambda p: (
        not p.es_vencido,
        p.fecha_devolucion_display or ahora.replace(year=9999),
    ))

    total_cancelados = sum(1 for p in prestamos if p.estado == 'rechazado')
    total_vencidos = sum(1 for p in prestamos if p.es_vencido)
    total_activos = len(prestamos) - total_cancelados
    total_al_dia = total_activos - total_vencidos

    filtro = (request.GET.get('filtro') or 'todos').strip().lower()
    if filtro not in {'todos', 'vencido', 'al-dia', 'cancelado'}:
        filtro = 'todos'

    if filtro == 'vencido':
        prestamos = [p for p in prestamos if p.es_vencido]
    elif filtro == 'al-dia':
        prestamos = [p for p in prestamos if not p.es_vencido and p.estado != 'rechazado']
    elif filtro == 'cancelado':
        prestamos = [p for p in prestamos if p.estado == 'rechazado']

    return render(request, 'inventario/prestamos/panel_prestamos.html', {
        'prestamos': prestamos,
        'filtro_activo': filtro,
        'total_vencidos': total_vencidos,
        'total_al_dia': total_al_dia,
        'total_cancelados': total_cancelados,
        'total_activos': total_activos,
        'ahora': ahora,
    })

@login_required
def pedidos_panel(request):
    if not request.user.id_rol_fk or request.user.id_rol_fk.nombre_rol not in ['admin', 'almacenista']:
        return redirect('dashboard')
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

    messages.success(request, f'Pedido #{pedido.id_pedido} procesado. Codigo de entrega generado por 2 horas.')
    _crear_notificacion(
        usuario=pedido.id_usuario_fk,
        tipo='esperando_entrega',
        titulo='Tu pedido está listo para entrega',
        mensaje=f'Tu pedido #{pedido.id_pedido} fue aprobado y está esperando ser entregado. '
                f'Dirígete al almacén con tu código de entrega.',
        pedido_id=pedido.id_pedido,
    )
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

        DetallePedido.objects.filter(id_pedido_fk=pedido).update(
            estado_detalle='entregado',
            fch_ult_act=now,
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
    return render(request, 'inventario/auditorias/panel_auditorias.html')

@login_required
def gestion_usuarios_panel(request):
    query = request.GET.get('q', '').strip()
    usuarios = Usuario.objects.all().select_related('id_rol_fk').order_by('nombre', 'apellido')
    if query:
        usuarios = usuarios.filter(
            models.Q(nombre__icontains=query) |
            models.Q(apellido__icontains=query) |
            models.Q(correo__icontains=query) |
            models.Q(cc__icontains=query)
        )
    roles = Rol.objects.all().order_by('nombre_rol')
    return render(request, 'inventario/usuarios/panel_usuarios.html', {
        'usuarios': usuarios,
        'query': query,
        'roles': roles,
    })


from django.views.decorators.http import require_POST
@login_required
@require_POST
def crear_usuario(request):
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
    messages.success(request, 'Usuario creado correctamente.')
    return redirect('gestion_usuarios_panel')

@login_required
@require_POST
def editar_rol_usuario(request, usuario_id):
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
    messages.success(request, 'Rol actualizado correctamente.')
    return redirect('gestion_usuarios_panel')


# ─────────────────────────────────────────────────────────────────────────────
# Panel de Notificaciones (usuario)
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def notificaciones_panel(request):
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
    _crear_notificacion(
        usuario=pedido.id_usuario_fk,
        tipo='aviso_devolucion',
        titulo='Aviso de devolución pendiente',
        mensaje=f'El almacenista solicita que devuelvas los materiales del pedido #{pedido.id_pedido}. '
                f'Por favor, acércate al almacén a la brevedad posible.',
        pedido_id=pedido.id_pedido,
    )
    messages.success(request, f'Aviso de devolución enviado al usuario del pedido #{pedido_id}.')
    return redirect('prestamos_panel')


