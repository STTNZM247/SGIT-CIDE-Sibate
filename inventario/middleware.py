from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils.cache import add_never_cache_headers


class ActiveUserRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def _apply_no_cache(self, request, response):
        path = (getattr(request, 'path', '') or '').lower()
        should_disable_cache = (
            getattr(getattr(request, 'user', None), 'is_authenticated', False)
            or path.startswith('/login')
            or path.startswith('/logout')
        )

        if should_disable_cache:
            add_never_cache_headers(response)
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0, private'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            response['Vary'] = 'Cookie'

        return response

    def __call__(self, request):
        if getattr(request, 'user', None) and request.user.is_authenticated and not request.user.is_active:
            logout(request)
            messages.error(request, 'Usuario inactivo. Por favor comunícate con un administrador.')
            response = redirect('login')
            return self._apply_no_cache(request, response)

        response = self.get_response(request)
        return self._apply_no_cache(request, response)
