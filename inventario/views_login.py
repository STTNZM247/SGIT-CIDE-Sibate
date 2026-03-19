from django.contrib.auth.views import LoginView
from django.shortcuts import redirect

class RolRedirectLoginView(LoginView):
    def get_success_url(self):
        user = self.request.user
        if hasattr(user, 'id_rol_fk') and user.id_rol_fk:
            nombre_rol = (user.id_rol_fk.nombre_rol or '').lower()
            if nombre_rol == 'almacenista':
                return '/almacenista/'
            # Puedes agregar más roles aquí si lo necesitas
        return super().get_success_url()
