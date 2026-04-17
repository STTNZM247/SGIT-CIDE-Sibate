from django.contrib.auth.views import LoginView
from django.urls import reverse

from .forms import CorreoAuthenticationForm


class RolRedirectLoginView(LoginView):
    authentication_form = CorreoAuthenticationForm

    def get_success_url(self):
        if getattr(self.request.user, 'is_superuser', False) or getattr(self.request.user, 'is_staff', False):
            return reverse('dashboard')

        rol = (getattr(getattr(self.request.user, 'id_rol_fk', None), 'nombre_rol', '') or '').strip().lower()

        if rol == 'admin':
            return reverse('dashboard')
        if rol == 'almacenista':
            return reverse('panel_almacenista')
        return reverse('panel_usuario')
