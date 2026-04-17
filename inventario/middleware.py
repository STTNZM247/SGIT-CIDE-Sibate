from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect


class ActiveUserRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if getattr(request, 'user', None) and request.user.is_authenticated and not request.user.is_active:
            logout(request)
            messages.error(request, 'Usuario inactivo. Por favor comunícate con un administrador.')
            return redirect('login')

        return self.get_response(request)
