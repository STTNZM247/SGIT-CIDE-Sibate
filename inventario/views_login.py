from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.core.mail import EmailMultiAlternatives
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
          return reverse('inventario_panel')
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

        subject = 'Restablecimiento de contraseña - Inventario SENA'
        text_content = (
            f'Hola {usuario.nombre or usuario.correo},\n\n'
            'Recibimos una solicitud para restablecer tu contraseña.\n'
            f'Usa este enlace único para continuar:\n{reset_url}\n\n'
            'Este enlace expirará en 30 minutos y solo podrá usarse una vez.\n'
            'Si no solicitaste este cambio, puedes ignorar este correo.'
        )
        nombre_usuario = usuario.nombre or usuario.correo
        html_content = f"""
<!DOCTYPE html>
<html lang=\"es\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>Restablecimiento de contraseña</title>
</head>
<body style=\"margin:0;padding:0;background-color:#f4f8f4;font-family:Arial,Helvetica,sans-serif;color:#1f2937;\">
  <table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" style=\"background:#f4f8f4;padding:24px 12px;\">
    <tr>
      <td align=\"center\">
        <table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" style=\"max-width:640px;background:#ffffff;border-radius:20px;overflow:hidden;box-shadow:0 12px 30px rgba(11,71,55,0.12);\">
          <tr>
            <td style=\"background:linear-gradient(135deg,#0b4737,#39A900);padding:28px 32px;color:#ffffff;\">
              <p style=\"margin:0 0 8px;font-size:13px;letter-spacing:1.6px;font-weight:bold;text-transform:uppercase;opacity:.9;\">SENA · Inventario</p>
              <h1 style=\"margin:0;font-size:30px;line-height:1.15;\">Restablece tu contraseña</h1>
            </td>
          </tr>
          <tr>
            <td style=\"padding:32px;\">
              <p style=\"margin:0 0 14px;font-size:16px;line-height:1.6;\">Hola <strong>{nombre_usuario}</strong>,</p>
              <p style=\"margin:0 0 16px;font-size:15px;line-height:1.7;color:#475569;\">Recibimos una solicitud para cambiar la contraseña de tu cuenta en el sistema de inventario.</p>
              <table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" style=\"margin:24px 0;\">
                <tr>
                  <td align=\"center\">
                    <a href=\"{reset_url}\" style=\"display:inline-block;background:#39A900;color:#ffffff;text-decoration:none;font-weight:700;padding:14px 26px;border-radius:999px;font-size:15px;\">Crear nueva contraseña</a>
                  </td>
                </tr>
              </table>
              <div style=\"background:#f0fdf4;border:1px solid #bbf7d0;border-radius:14px;padding:16px 18px;margin:0 0 18px;\">
                <p style=\"margin:0;font-size:14px;line-height:1.7;color:#166534;\"><strong>Importante:</strong> este enlace es único, solo puede usarse una vez y expirará en <strong>30 minutos</strong>.</p>
              </div>
              <p style=\"margin:0 0 12px;font-size:14px;line-height:1.7;color:#64748b;\">Si el botón no funciona, copia y pega este enlace en tu navegador:</p>
              <p style=\"margin:0 0 22px;font-size:13px;line-height:1.7;word-break:break-all;\"><a href=\"{reset_url}\" style=\"color:#0b4737;\">{reset_url}</a></p>
              <p style=\"margin:0;font-size:14px;line-height:1.7;color:#64748b;\">Si no solicitaste este cambio, puedes ignorar este mensaje con tranquilidad.</p>
            </td>
          </tr>
          <tr>
            <td style=\"padding:18px 32px;background:#f8fafc;border-top:1px solid #e2e8f0;color:#64748b;font-size:12px;line-height:1.6;\">Servicio Nacional de Aprendizaje · SENA<br>Sistema de Inventario Sibate</td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
            to=[usuario.correo],
        )
        email.attach_alternative(html_content, 'text/html')
        email.send(fail_silently=False)

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
