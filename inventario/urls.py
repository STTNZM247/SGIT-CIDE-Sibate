from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from .views import (
    catalogo,
    dashboard,
    eliminar_catalogo,
    eliminar_producto,
    productos_catalogo,
    registrar_catalogo,
    registrar_producto,
)

urlpatterns = [
    path(
        'login/',
        LoginView.as_view(
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
    path('catalogo/', catalogo, name='catalogo'),
    path('catalogo/<int:cat_id>/eliminar/', eliminar_catalogo, name='eliminar_catalogo'),
    path('catalogo/<int:cat_id>/productos/', productos_catalogo, name='productos_catalogo'),
    path('catalogo/<int:cat_id>/productos/<int:prod_id>/eliminar/', eliminar_producto, name='eliminar_producto'),
    path('catalogo/nuevo/', registrar_catalogo, name='registrar_catalogo'),
    path('catalogo/nuevo-producto/', registrar_producto, name='registrar_producto'),
]
