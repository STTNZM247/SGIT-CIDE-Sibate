from django.db.models import Sum

from .models import CarritoItem, Notificacion


def notificaciones_no_leidas(request):
    if request.user.is_authenticated:
        notif_count = Notificacion.objects.filter(
            id_usuario_fk=request.user,
            leida=False,
        ).count()
        carrito_total = (
            CarritoItem.objects.filter(id_usuario_fk=request.user)
            .aggregate(total=Sum('cantidad'))
            .get('total')
            or 0
        )
        return {
            'notif_no_leidas': notif_count,
            'carrito_cantidad_nav': carrito_total,
        }
    return {
        'notif_no_leidas': 0,
        'carrito_cantidad_nav': 0,
    }
