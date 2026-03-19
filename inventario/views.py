
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from .models import Producto, Catalogo, Disponibilidad, Rol
from .forms import ProductoForm
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
from django.http import Http404
from django.contrib.auth.decorators import login_required

# ...existing code...

@login_required
def producto_detalle(request, prod_id):
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
from django.db.models import OuterRef, Subquery
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CatalogoForm, ProductoForm, UsuarioPerfilForm
from .models import Catalogo, Disponibilidad, Producto, Usuario, Rol


@login_required
def catalogo(request):
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
        },
    )


@login_required
def registrar_catalogo(request):
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
        },
    )


@login_required
def eliminar_producto(request, cat_id, prod_id):
    catalogo = get_object_or_404(Catalogo, pk=cat_id)
    producto = get_object_or_404(Producto, pk=prod_id, id_cat_fk=catalogo)

    if request.method == 'POST':
        nombre = producto.nombre_producto
        producto.delete()
        messages.success(request, f'Producto "{nombre}" eliminado correctamente.')

    return redirect('productos_catalogo', cat_id=cat_id)



@login_required
def dashboard(request):
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
        ids_bajo = Disponibilidad.objects.filter(stock__lte=5).values_list('id_prod_fk_id', flat=True)
        productos_qs = productos_qs.filter(id_prod__in=ids_bajo)

    productos = list(productos_qs.order_by('-fch_registro', '-id_prod'))

    total_productos = Producto.objects.count()
    productos_bajo_stock = Disponibilidad.objects.filter(stock__lte=5).count()

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
def prestamos_panel(request):
    return render(request, 'inventario/prestamos/panel_prestamos.html')

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

