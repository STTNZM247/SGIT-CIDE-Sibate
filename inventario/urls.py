from django.contrib.auth.views import LogoutView
from .views_login import RolRedirectLoginView
from django.urls import path

from .views import (
    catalogo,
    dashboard,
    eliminar_catalogo,
    eliminar_producto,
    productos_catalogo,
    registrar_catalogo,
    registrar_producto,
    perfil_usuario,
    prestamos_panel,
    auditorias_panel,
    gestion_usuarios_panel,
    panel_almacenista,
    crear_usuario,
    editar_rol_usuario,
    producto_detalle,
    producto_editar,
)

urlpatterns = [
    path(
        'login/',
        RolRedirectLoginView.as_view(
            template_name='inventario/login/login.html',
            redirect_authenticated_user=True,
        ),
        name='login',
    ),
    path(
        'logout/',
        LogoutView.as_view(next_page='login'),
        name='logout',
    ),
    path('', dashboard, name='dashboard'),
    path('almacenista/', panel_almacenista, name='panel_almacenista'),
    path('catalogo/', catalogo, name='catalogo'),
    path('catalogo/<int:cat_id>/eliminar/', eliminar_catalogo, name='eliminar_catalogo'),
    path('catalogo/<int:cat_id>/productos/', productos_catalogo, name='productos_catalogo'),
    path('producto/<int:prod_id>/', producto_detalle, name='producto_detalle'),
        path('producto/<int:prod_id>/editar/', producto_editar, name='producto_editar'),
    path('catalogo/<int:cat_id>/productos/<int:prod_id>/eliminar/', eliminar_producto, name='eliminar_producto'),
    path('catalogo/nuevo/', registrar_catalogo, name='registrar_catalogo'),
    path('catalogo/nuevo-producto/', registrar_producto, name='registrar_producto'),
    path('perfil/', perfil_usuario, name='perfil_usuario'),
    path('prestamos/', prestamos_panel, name='prestamos_panel'),
    path('auditorias/', auditorias_panel, name='auditorias_panel'),
    path('usuarios/', gestion_usuarios_panel, name='gestion_usuarios_panel'),
    path('usuarios/crear/', crear_usuario, name='crear_usuario'),
    path('usuarios/<int:usuario_id>/editar-rol/', editar_rol_usuario, name='editar_rol_usuario'),
]
