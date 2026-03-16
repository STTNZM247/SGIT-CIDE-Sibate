from django.contrib import admin
from .models import Categoria, Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
	list_display = ('id', 'nombre')
	search_fields = ('nombre',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
	list_display = ('id', 'codigo', 'nombre', 'categoria', 'stock', 'activo')
	list_filter = ('activo', 'categoria')
	search_fields = ('codigo', 'nombre')
