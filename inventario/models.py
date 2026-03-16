from django.db import models


class Categoria(models.Model):
	nombre = models.CharField(max_length=100, unique=True)
	descripcion = models.TextField(blank=True)

	def __str__(self):
		return self.nombre


class Producto(models.Model):
	categoria = models.ForeignKey(
		Categoria,
		on_delete=models.PROTECT,
		related_name='productos',
	)
	nombre = models.CharField(max_length=150)
	codigo = models.CharField(max_length=50, unique=True)
	stock = models.PositiveIntegerField(default=0)
	stock_minimo = models.PositiveIntegerField(default=1)
	activo = models.BooleanField(default=True)
	creado_en = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'{self.codigo} - {self.nombre}'
