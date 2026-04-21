from datetime import timedelta

from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.core import mail
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from .middleware import ActiveUserRequiredMiddleware
from .models import PasswordResetToken, Rol, TipoDoc, Usuario
from .views_login import RolRedirectLoginView
from .views_usuario import panel_usuario


class GestionEstadoUsuarioTests(TestCase):
    def setUp(self):
        self.rol_admin = Rol.objects.create(nombre_rol='admin')
        self.rol_usuario = Rol.objects.create(nombre_rol='usuario')

        self.admin = Usuario.objects.create(
            correo='admin@sena.edu.co',
            nombre='Admin',
            apellido='Principal',
            id_rol_fk=self.rol_admin,
            is_active=True,
            is_staff=True,
        )
        self.admin.set_password('Admin123!')
        self.admin.save()

        self.usuario = Usuario.objects.create(
            correo='usuario@sena.edu.co',
            nombre='Usuario',
            apellido='Prueba',
            id_rol_fk=self.rol_usuario,
            is_active=True,
        )
        self.usuario.set_password('Usuario123!')
        self.usuario.save()

    def test_admin_can_toggle_user_status(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            reverse('toggle_estado_usuario', args=[self.usuario.id_usu]),
        )

        self.usuario.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.usuario.is_active)

    def test_inactive_user_sees_specific_login_message(self):
        self.usuario.is_active = False
        self.usuario.save(update_fields=['is_active'])

        request = RequestFactory().post(reverse('login'), {
            'username': self.usuario.correo,
            'password': 'Usuario123!',
        })
        request.user = AnonymousUser()
        request._dont_enforce_csrf_checks = True

        session_middleware = SessionMiddleware(lambda req: None)
        session_middleware.process_request(request)
        request.session.save()

        message_middleware = MessageMiddleware(lambda req: None)
        message_middleware.process_request(request)

        response = RolRedirectLoginView.as_view(template_name='inventario/login/login.html')(request)
        form = response.context_data['form']

        self.assertEqual(response.status_code, 200)
        self.assertIn('Usuario inactivo. Por favor comunícate con un administrador.', form.non_field_errors())

    def test_wrong_credentials_show_clear_message(self):
        request = RequestFactory().post(reverse('login'), {
            'username': self.usuario.correo,
            'password': 'ClaveErrada123',
        })
        request.user = AnonymousUser()
        request._dont_enforce_csrf_checks = True

        session_middleware = SessionMiddleware(lambda req: None)
        session_middleware.process_request(request)
        request.session.save()

        message_middleware = MessageMiddleware(lambda req: None)
        message_middleware.process_request(request)

        response = RolRedirectLoginView.as_view(template_name='inventario/login/login.html')(request)
        form = response.context_data['form']

        self.assertEqual(response.status_code, 200)
        self.assertIn('Correo o contraseña incorrectos.', form.non_field_errors())

    def test_superuser_without_role_redirects_to_dashboard(self):
        superuser = Usuario.objects.create(
            correo='root@sena.edu.co',
            nombre='Root',
            apellido='Admin',
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        superuser.set_password('SuperAdmin123!')
        superuser.save()

        request = RequestFactory().get(reverse('login'))
        request.user = superuser

        view = RolRedirectLoginView()
        view.request = request

        self.assertEqual(view.get_success_url(), reverse('dashboard'))

    def test_user_without_role_can_access_panel_usuario(self):
        usuario_sin_rol = Usuario.objects.create(
            correo='sinrol@sena.edu.co',
            nombre='Sin',
            apellido='Rol',
            is_active=True,
        )
        usuario_sin_rol.set_password('Usuario123!')
        usuario_sin_rol.save()

        request = RequestFactory().get(reverse('panel_usuario'))
        request.user = usuario_sin_rol

        response = panel_usuario(request)

        self.assertEqual(response.status_code, 200)

    def test_public_registration_creates_usuario_role_account(self):
        tipo_doc, _ = TipoDoc.objects.get_or_create(codigo='CC', defaults={'nombre': 'Cedula de ciudadania'})

        response = self.client.post(reverse('registro_publico'), {
            'id_tipo_doc_fk': str(tipo_doc.id_tipo_doc),
            'cc': '10203040',
            'nombre': 'Nuevo',
            'apellido': 'Usuario',
            'correo': 'nuevo@sena.edu.co',
            'password1': 'NuevaClave123!',
            'password2': 'NuevaClave123!',
        })

        nuevo = Usuario.objects.get(correo='nuevo@sena.edu.co')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))
        self.assertTrue(nuevo.check_password('NuevaClave123!'))
        self.assertEqual(nuevo.id_rol_fk.nombre_rol, 'usuario')
        self.assertEqual(nuevo.id_tipo_doc_fk.codigo, 'CC')
        self.assertTrue(nuevo.is_active)

    def test_recovery_sends_email_with_reset_link(self):
        response = self.client.post(reverse('recuperar_acceso'), {
            'correo': self.usuario.correo,
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.usuario.correo, mail.outbox[0].to)
        self.assertIn('/login/restablecer/', mail.outbox[0].body)
        self.assertEqual(PasswordResetToken.objects.filter(usuario=self.usuario, usado_en__isnull=True).count(), 1)

    def test_reset_link_updates_password_and_expires(self):
        token = PasswordResetToken.create_for_user(self.usuario)

        response = self.client.post(reverse('restablecer_password', args=[token.token]), {
            'password1': 'Recuperada123!',
            'password2': 'Recuperada123!',
        })

        self.usuario.refresh_from_db()
        token.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))
        self.assertTrue(self.usuario.check_password('Recuperada123!'))
        self.assertIsNotNone(token.usado_en)

        expirado = PasswordResetToken.create_for_user(self.usuario)
        expirado.expira_en = timezone.now() - timedelta(minutes=1)
        expirado.save(update_fields=['expira_en'])

        expired_response = self.client.get(reverse('restablecer_password', args=[expirado.token]))
        self.assertEqual(expired_response.status_code, 302)
        self.assertEqual(expired_response.url, reverse('recuperar_acceso'))

    def test_authenticated_pages_are_marked_no_store(self):
        request = RequestFactory().get(reverse('dashboard'))
        request.user = self.admin

        middleware = ActiveUserRequiredMiddleware(lambda req: HttpResponse('ok'))
        response = middleware(request)
        cache_header = response.get('Cache-Control', '')

        self.assertIn('no-store', cache_header)
        self.assertIn('no-cache', cache_header)
        self.assertEqual(response.get('Pragma'), 'no-cache')

    def test_logout_invalidates_dashboard_access(self):
        self.client.force_login(self.admin)

        logout_response = self.client.post(reverse('logout'))
        dashboard_response = self.client.get(reverse('dashboard'))

        self.assertEqual(logout_response.status_code, 302)
        self.assertIn('no-store', logout_response.get('Cache-Control', ''))
        self.assertEqual(dashboard_response.status_code, 302)
        self.assertIn(reverse('login'), dashboard_response.url)
