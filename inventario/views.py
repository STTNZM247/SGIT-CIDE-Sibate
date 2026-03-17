from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import OuterRef, Subquery
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CatalogoForm, ProductoForm, UsuarioPerfilForm
from .models import Catalogo, Disponibilidad, Producto, Usuario


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
    return render(request, 'inventario/usuarios/panel_usuarios.html')

