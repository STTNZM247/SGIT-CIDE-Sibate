from django.contrib.auth.views import LoginView
from django.urls import reverse

from .forms import CorreoAuthenticationForm
from .models import Rol


class RolRedirectLoginView(LoginView):
    authentication_form = CorreoAuthenticationForm

    def _ensure_staff_role(self):
        user = self.request.user
        if not user.is_authenticated:
            return

        if (getattr(user, 'is_superuser', False) or getattr(user, 'is_staff', False)) and not getattr(user, 'id_rol_fk_id', None):
            rol_admin, _ = Rol.objects.get_or_create(nombre_rol='admin')
            user.id_rol_fk = rol_admin
            user.save(update_fields=['id_rol_fk'])

    def get_success_url(self):
        self._ensure_staff_role()

        if getattr(self.request.user, 'is_superuser', False) or getattr(self.request.user, 'is_staff', False):
            return reverse('dashboard')

        rol = (getattr(getattr(self.request.user, 'id_rol_fk', None), 'nombre_rol', '') or '').strip().lower()

        if rol in {'admin', 'administrador'}:
            return reverse('dashboard')
        if rol in {'almacenista', 'almacen'}:
            return reverse('panel_almacenista')
        return reverse('panel_usuario')
