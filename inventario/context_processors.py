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
            # Para usuarios: solo pedidos activos que aún no han visto en el panel
            activos_ids = list(
                Pedido.objects.filter(
                    id_usuario_fk=request.user,
                    estado__in=['pendiente', 'esperando entrega'],
                ).values_list('id_pedido', flat=True)
            )
            visto_ids_raw = request.session.get('pedidos_u_visto_ids')
            if visto_ids_raw is None:
                # Nunca ha visitado el panel: mostrar todos los activos
                pedidos_pendientes_nav = len(activos_ids)
            else:
                visto_ids = set(visto_ids_raw)
                pedidos_pendientes_nav = sum(1 for pid in activos_ids if pid not in visto_ids)
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
