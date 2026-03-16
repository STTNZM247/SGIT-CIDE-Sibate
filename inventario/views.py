from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import render

from .models import Catalogo, Disponibilidad, Producto


@login_required
def dashboard(request):
    q = (request.GET.get('q') or '').strip()
    cat_id = (request.GET.get('categoria') or '').strip()
    bajo_stock = (request.GET.get('bajo_stock') or '').strip() == '1'

    productos_qs = Producto.objects.select_related('id_cat_fk')

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

    productos = productos_qs.order_by('-fch_registro')[:12]

    total_productos = Producto.objects.count()
    productos_bajo_stock = Disponibilidad.objects.filter(stock__lte=5).count()

    catalogos = (
        Catalogo.objects.annotate(
            total_productos=models.Count('producto')
        ).order_by('nombre_catalogo')[:8]
    )

    return render(
        request,
        'inventario/dashboard.html',
        {
            'q': q,
            'categoria_activa': cat_id,
            'bajo_stock': bajo_stock,
            'catalogos': catalogos,
            'productos': productos,
            'total_productos': total_productos,
            'productos_bajo_stock': productos_bajo_stock,
        },
    )

