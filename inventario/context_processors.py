from django.db.models import Sum

from .models import CarritoItem, Notificacion, Pedido


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
        pedidos_pendientes_nav = 0
        rol = getattr(getattr(request.user, 'id_rol_fk', None), 'nombre_rol', '')
        if rol in ('admin', 'almacenista'):
            pedidos_pendientes_nav = Pedido.objects.filter(
                estado__in=['pendiente', 'esperando entrega']
            ).count()
        else:
            # Para usuarios: pedidos activos que requieren atención
            pedidos_pendientes_nav = Pedido.objects.filter(
                id_usuario_fk=request.user,
                estado__in=['pendiente', 'esperando entrega'],
            ).count()
        return {
            'notif_no_leidas': notif_count,
            'carrito_cantidad_nav': carrito_total,
            'pedidos_pendientes_nav': pedidos_pendientes_nav,
        }
    return {
        'notif_no_leidas': 0,
        'carrito_cantidad_nav': 0,
        'pedidos_pendientes_nav': 0,
    }
