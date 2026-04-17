from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import CorreoAuthenticationForm, RecuperarAccesoForm, RegistroPublicoForm, RestablecerPasswordForm
from .models import PasswordResetToken, Rol


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


def registro_publico(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = RegistroPublicoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Tu cuenta fue creada correctamente. Ya puedes iniciar sesión.')
        return redirect('login')

    return render(request, 'inventario/login/registro.html', {'form': form})


def recuperar_acceso(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = RecuperarAccesoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        usuario = form.usuario
        reset_token = PasswordResetToken.create_for_user(usuario)
        reset_url = request.build_absolute_uri(reverse('restablecer_password', args=[reset_token.token]))

        send_mail(
            subject='Restablecimiento de contraseña - Inventario SENA',
            message=(
                f'Hola {usuario.nombre or usuario.correo},\n\n'
                'Recibimos una solicitud para restablecer tu contraseña.\n'
                f'Usa este enlace único para continuar:\n{reset_url}\n\n'
                'Este enlace expirará en 30 minutos y solo podrá usarse una vez.\n'
                'Si no solicitaste este cambio, puedes ignorar este correo.'
            ),
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
            recipient_list=[usuario.correo],
            fail_silently=False,
        )

        messages.success(request, 'Te enviamos un enlace de restablecimiento a tu correo registrado.')
        return redirect('login')

    return render(request, 'inventario/login/recuperar_acceso.html', {'form': form})


def restablecer_password(request, token):
    if request.user.is_authenticated:
        return redirect('dashboard')

    reset_token = (
        PasswordResetToken.objects
        .select_related('usuario')
        .filter(token=token, usado_en__isnull=True)
        .first()
    )

    if not reset_token or reset_token.expira_en < timezone.now():
        messages.error(request, 'El enlace de restablecimiento ya no es válido o expiró.')
        return redirect('recuperar_acceso')

    form = RestablecerPasswordForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save(reset_token.usuario)
        reset_token.usado_en = timezone.now()
        reset_token.save(update_fields=['usado_en'])
        messages.success(request, 'Tu contraseña fue actualizada correctamente. Ya puedes iniciar sesión.')
        return redirect('login')

    return render(
        request,
        'inventario/login/restablecer_password.html',
        {'form': form, 'reset_token': reset_token},
    )
