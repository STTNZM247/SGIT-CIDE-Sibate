from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import reverse

from .models import Rol, Usuario
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
        response = self.client.post(reverse('registro_publico'), {
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
        self.assertTrue(nuevo.is_active)

    def test_recovery_allows_password_reset_by_cc(self):
        self.usuario.cc = '99887766'
        self.usuario.save(update_fields=['cc'])

        response = self.client.post(reverse('recuperar_acceso'), {
            'cc': '99887766',
            'correo': '',
            'password1': 'Recuperada123!',
            'password2': 'Recuperada123!',
        })

        self.usuario.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))
        self.assertTrue(self.usuario.check_password('Recuperada123!'))
