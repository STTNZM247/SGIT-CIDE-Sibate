from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

from .db_compat import usuario_missing_optional_fields


class CompatibleModelBackend(ModelBackend):
    def _compatible_queryset(self):
        user_model = get_user_model()
        queryset = user_model._default_manager.all()
        missing_fields = usuario_missing_optional_fields(user_model)
        if missing_fields:
            queryset = queryset.defer(*missing_fields)
        return queryset

    def authenticate(self, request, username=None, password=None, **kwargs):
        user_model = get_user_model()
        if username is None:
            username = kwargs.get(user_model.USERNAME_FIELD)
        if username is None or password is None:
            return None

        user = self._compatible_queryset().filter(correo__iexact=username).first()
        if user is not None and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

    def get_user(self, user_id):
        return self._compatible_queryset().filter(pk=user_id).first()