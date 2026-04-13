from .models import Notificacion


def notificaciones_no_leidas(request):
    if request.user.is_authenticated:
        count = Notificacion.objects.filter(
            id_usuario_fk=request.user,
            leida=False,
        ).count()
        return {'notif_no_leidas': count}
    return {'notif_no_leidas': 0}
