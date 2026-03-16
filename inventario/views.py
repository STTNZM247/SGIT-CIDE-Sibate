from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import render
from .models import Categoria, Producto


@login_required
def dashboard(request):
	q = (request.GET.get('q') or '').strip()
	ambiente = (request.GET.get('ambiente') or '').strip()
	categoria_id = (request.GET.get('categoria') or '').strip()
	bajo_stock = (request.GET.get('bajo_stock') or '').strip() == '1'

	productos_qs = Producto.objects.select_related('categoria').filter(activo=True)

	if categoria_id.isdigit():
		productos_qs = productos_qs.filter(categoria_id=int(categoria_id))

	if bajo_stock:
		productos_qs = productos_qs.filter(stock__lte=models.F('stock_minimo'))

	if q:
		productos_qs = productos_qs.filter(
			models.Q(nombre__icontains=q)
			| models.Q(codigo__icontains=q)
			| models.Q(categoria__nombre__icontains=q)
		)

	productos = productos_qs.order_by('-creado_en')[:12]

	total_productos = Producto.objects.filter(activo=True).count()
	productos_bajo_stock = Producto.objects.filter(
		activo=True,
		stock__lte=models.F('stock_minimo'),
	).count()

	categorias = (
		Categoria.objects.annotate(
			total_productos=models.Count(
				'productos',
				filter=models.Q(productos__activo=True),
			)
		)
		.order_by('nombre')[:8]
	)

	return render(
		request,
		'inventario/dashboard.html',
		{
			'q': q,
			'ambiente': ambiente,
			'categoria_activa': categoria_id,
			'bajo_stock': bajo_stock,
			'categorias': categorias,
			'productos': productos,
			'total_productos': total_productos,
			'productos_bajo_stock': productos_bajo_stock,
		},
	)
