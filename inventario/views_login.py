from django.contrib.auth.views import LoginView
from django.shortcuts import redirect

class RolRedirectLoginView(LoginView):
    def get_success_url(self):
        return '/usuario/inventario/'
