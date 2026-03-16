from django.contrib import admin
from .models import Auditorio, Catalogo, Disponibilidad, Producto, Rol, UsuCat, Usuario


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('id_rol', 'fch_registro')


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id_usu', 'cc', 'nombre', 'apellido', 'correo', 'id_rol_fk')
    search_fields = ('cc', 'nombre', 'apellido', 'correo')
    list_filter = ('id_rol_fk',)


@admin.register(Catalogo)
class CatalogoAdmin(admin.ModelAdmin):
    list_display = ('id_cat', 'nombre_catalogo')
    search_fields = ('nombre_catalogo',)


@admin.register(UsuCat)
class UsuCatAdmin(admin.ModelAdmin):
    list_display = ('id_usu_cat', 'id_usuario_fk', 'id_cat_fk', 'fch_registro')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id_prod', 'nombre_producto', 'id_cat_fk', 'fch_registro')
    search_fields = ('nombre_producto',)
    list_filter = ('id_cat_fk',)


@admin.register(Disponibilidad)
class DisponibilidadAdmin(admin.ModelAdmin):
    list_display = ('id_disp', 'id_prod_fk', 'cantidad', 'stock')
    list_filter = ('id_prod_fk',)


@admin.register(Auditorio)
class AuditorioAdmin(admin.ModelAdmin):
    list_display = ('id_aud', 'nombre_auditorio', 'id_usu_cat_fk')
    search_fields = ('nombre_auditorio',)
