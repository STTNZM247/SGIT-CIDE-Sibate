from django.db import models
from django.shortcuts import render
from .models import Producto


def dashboard(request):
	total_productos = Producto.objects.count()
	productos_bajo_stock = Producto.objects.filter(stock__lte=models.F('stock_minimo')).count()

	return render(
		request,
		'inventario/dashboard.html',
		{
			'total_productos': total_productos,
			'productos_bajo_stock': productos_bajo_stock,
		},
	)
