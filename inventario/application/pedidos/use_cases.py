"""Casos de uso de pedidos de usuario (capa application).

Migracion gradual: la logica se centraliza aqui y la capa HTTP
en interfaces queda como adaptador del request/response.
"""

from __future__ import annotations

from datetime import timedelta

from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

from inventario import views_usuario as legacy_usuario
from inventario.models import DetallePedido, Pedido


MAX_EXTENSIONES = 3
DIAS_EXTENSION = 3


def mapear_estado_ui_a_estado_real(estado_ui: str) -> str | None:
    estado_limpio = (estado_ui or "").strip().lower()
    return {
        "pendiente": "pendiente",
        "esperando-entrega": "esperando entrega",
        "entregado": "entregado",
        "vencido": "vencido",
        "devuelto": "devuelto",
        "rechazado": "rechazado",
        "cancelado": "cancelado",
    }.get(estado_limpio)


def _estado_ui_normalizado(estado_real: str) -> str:
    if estado_real in {"cancelado", "rechazado"}:
        return "cancelado"
    return estado_real


def _estado_pedido_canonico(estado: str) -> str:
    estado_limpio = (estado or "").strip().lower().replace("_", " ")
    aliases = {
        "deuelto": "devuelto",
        "debuelto": "devuelto",
        "devolvido": "devuelto",
        "esperandoentrega": "esperando entrega",
    }
    return aliases.get(estado_limpio, estado_limpio)


def obtener_contexto_pedidos_usuario(request) -> dict:
    legacy_usuario._auto_cancelar_pedidos_pendientes_vencidos()

    pedidos = list(
        Pedido.objects
        .filter(id_usuario_fk=request.user)
        .prefetch_related("detalles__id_prod_fk", "evidencias")
        .order_by("-fch_registro", "-id_pedido")
    )

    ahora = timezone.now()
    ventana_cancelacion = timedelta(minutes=10)

    for pedido in pedidos:
        estado_canonico = _estado_pedido_canonico(pedido.estado)
        if estado_canonico and estado_canonico != pedido.estado:
            pedido.estado = estado_canonico
            pedido.fch_ult_act = ahora
            pedido.save(update_fields=["estado", "fch_ult_act"])

        if pedido.estado == "devuelto" and (pedido.codigo_entrega or pedido.codigo_expira_en):
            pedido.codigo_entrega = None
            pedido.codigo_expira_en = None
            pedido.fch_ult_act = ahora
            pedido.save(update_fields=["codigo_entrega", "codigo_expira_en", "fch_ult_act"])

        detalles_pedido = list(pedido.detalles.all())
        if pedido.estado in ("entregado", "vencido"):
            pedido.detalles_usuario = [
                detalle for detalle in detalles_pedido
                if not (detalle.id_prod_fk and detalle.id_prod_fk.tipo_bien == "consumo")
            ]
        else:
            pedido.detalles_usuario = detalles_pedido
        pedido.detalles_usuario_count = len(pedido.detalles_usuario)

        pedido.estado_ui = _estado_ui_normalizado(pedido.estado)
        pedido.estado_ui_label = "Cancelado" if pedido.estado_ui == "cancelado" else pedido.estado.title()

        pedido.puede_mostrar_codigo_devolucion = pedido.estado in ("entregado", "vencido")

        if pedido.estado == "esperando entrega":
            codigo_vigente = bool(
                pedido.codigo_entrega
                and pedido.codigo_expira_en
                and pedido.codigo_expira_en >= ahora
            )
            if not codigo_vigente:
                pedido.codigo_entrega = f"{legacy_usuario.secrets.randbelow(1000000):06d}"
                pedido.codigo_expira_en = ahora + timedelta(hours=2)
                pedido.fch_ult_act = ahora
                pedido.save(update_fields=["codigo_entrega", "codigo_expira_en", "fch_ult_act"])
            pedido.codigo_vigente = True
            pedido.devolucion_codigo = None
            pedido.devolucion_segundos = 0
            pedido.devolucion_expira_en = None
        elif pedido.estado in ("entregado", "vencido"):
            legacy_usuario._asegurar_codigo_devolucion(pedido, ahora)
            pedido.codigo_vigente = False
            pedido.devolucion_codigo = pedido.codigo_entrega
            pedido.devolucion_expira_en = pedido.codigo_expira_en
            if pedido.codigo_expira_en:
                pedido.devolucion_segundos = max(int((pedido.codigo_expira_en - ahora).total_seconds()), 0)
            else:
                pedido.devolucion_segundos = 0
        else:
            pedido.codigo_vigente = False
            pedido.devolucion_codigo = None
            pedido.devolucion_segundos = 0
            pedido.devolucion_expira_en = None

        if pedido.estado == "pendiente" and pedido.fch_registro:
            expira_cancelacion = pedido.fch_registro + ventana_cancelacion
            segundos = int((expira_cancelacion - ahora).total_seconds())
            pedido.puede_cancelar = segundos > 0
            pedido.segundos_cancelacion = max(segundos, 0)
        else:
            pedido.puede_cancelar = False
            pedido.segundos_cancelacion = 0

        pedido.esta_vencido = (
            pedido.estado in ("entregado", "vencido")
            and pedido.fecha_devolucion is not None
            and pedido.fecha_devolucion < ahora
        ) or pedido.estado == "vencido"

    request.session["pedidos_u_visto_ids"] = [
        p.id_pedido for p in pedidos if p.estado in ("pendiente", "esperando entrega")
    ]

    estado_activo = (request.GET.get("estado") or "todos").strip().lower()
    estados_validos = {
        "todos", "pendiente", "esperando-entrega", "entregado", "vencido", "devuelto", "rechazado", "cancelado"
    }
    if estado_activo not in estados_validos:
        estado_activo = "todos"
    if estado_activo == "rechazado":
        estado_activo = "cancelado"

    filtro_estado_real = mapear_estado_ui_a_estado_real(estado_activo)

    pedidos_filtrados = pedidos
    if estado_activo == "cancelado":
        pedidos_filtrados = [p for p in pedidos if p.estado in {"cancelado", "rechazado"}]
    elif filtro_estado_real:
        pedidos_filtrados = [p for p in pedidos if p.estado == filtro_estado_real]

    conteo_cancelado = sum(1 for p in pedidos if p.estado in {"cancelado", "rechazado"})
    conteos_estado = {
        "todos": len(pedidos),
        "pendiente": sum(1 for p in pedidos if p.estado == "pendiente"),
        "esperando_entrega": sum(1 for p in pedidos if p.estado == "esperando entrega"),
        "entregado": sum(1 for p in pedidos if p.estado == "entregado"),
        "vencido": sum(1 for p in pedidos if p.estado == "vencido"),
        "devuelto": sum(1 for p in pedidos if p.estado == "devuelto"),
        "rechazado": conteo_cancelado,
        "cancelado": conteo_cancelado,
    }

    return {
        "pedidos": pedidos_filtrados,
        "estado_activo": estado_activo,
        "conteos_estado": conteos_estado,
        "ahora": ahora,
    }


def cancelar_pedido_usuario(request, pedido_id):
    with transaction.atomic():
        pedido = get_object_or_404(
            Pedido.objects.select_for_update(),
            pk=pedido_id,
            id_usuario_fk=request.user,
        )

        if pedido.estado != "pendiente":
            messages.error(request, "Solo puedes cancelar pedidos en estado pendiente.")
            return redirect("pedidos_usuario")

        if not pedido.fch_registro:
            messages.error(request, "No se pudo verificar la ventana de cancelacion.")
            return redirect("pedidos_usuario")

        ahora = timezone.now()
        expira = pedido.fch_registro + timedelta(minutes=10)
        if ahora > expira:
            messages.error(request, "El plazo de 10 minutos para cancelar este pedido ha vencido.")
            return redirect("pedidos_usuario")

        now = timezone.now()
        pedido.estado = "cancelado"
        pedido.fch_ult_act = now
        pedido.save(update_fields=["estado", "fch_ult_act"])

        DetallePedido.objects.filter(id_pedido_fk=pedido).update(
            estado_detalle="cancelado",
            fch_ult_act=now,
        )

    legacy_usuario._registrar_auditoria(
        request,
        accion="actualizar",
        entidad="pedido",
        entidad_id=pedido.id_pedido,
        descripcion=f"Pedido #{pedido.id_pedido} cancelado por el usuario en su panel.",
    )
    legacy_usuario._crear_notificacion(
        usuario=request.user,
        tipo="rechazado",
        titulo="Pedido cancelado por ti",
        mensaje=f"Cancelaste tu pedido #{pedido.id_pedido}. Si fue un error, deberas crear un nuevo pedido.",
        pedido_id=pedido.id_pedido,
    )
    legacy_usuario._notificar_staff(
        tipo="staff_pedido_cancelado",
        titulo=f"Pedido #{pedido.id_pedido} cancelado por el usuario",
        mensaje=(
            f"{request.user.nombre or ''} {request.user.apellido or ''}".strip() or request.user.correo
        ) + f" cancelo su pedido #{pedido.id_pedido}. Ya no es necesario prepararlo.",
        pedido_id=pedido.id_pedido,
    )
    messages.success(request, f"Pedido #{pedido.id_pedido} cancelado correctamente.")
    return redirect("pedidos_usuario")


def codigo_devolucion_usuario(request, pedido_id):
    if request.method != "GET":
        return JsonResponse({"ok": False, "error": "Metodo no permitido."}, status=405)

    with transaction.atomic():
        pedido = get_object_or_404(
            Pedido.objects.select_for_update(),
            pk=pedido_id,
            id_usuario_fk=request.user,
        )

        if pedido.estado not in ("entregado", "vencido"):
            return JsonResponse({"ok": False, "error": "Este pedido no esta en estado entregado."}, status=400)

        now = timezone.now()
        legacy_usuario._asegurar_codigo_devolucion(pedido, now)
        segundos = max(int((pedido.codigo_expira_en - now).total_seconds()), 0)

    return JsonResponse({
        "ok": True,
        "codigo": pedido.codigo_entrega,
        "segundos": segundos,
        "server_now": now.isoformat(),
        "expira_en": pedido.codigo_expira_en.isoformat() if pedido.codigo_expira_en else None,
    })


def extender_plazo_usuario(request, pedido_id):
    with transaction.atomic():
        pedido = get_object_or_404(
            Pedido.objects.select_for_update(),
            pk=pedido_id,
            id_usuario_fk=request.user,
        )

        if pedido.estado not in ("entregado", "vencido"):
            messages.error(request, "Solo puedes extender el plazo de pedidos actualmente entregados.")
            return redirect("pedidos_usuario")

        if pedido.extensiones_plazo >= MAX_EXTENSIONES:
            messages.error(
                request,
                f"Ya usaste los {MAX_EXTENSIONES} plazos disponibles. Debes devolver los productos a la brevedad posible.",
            )
            return redirect("pedidos_usuario")

        ahora = timezone.now()
        base = pedido.fecha_devolucion if pedido.fecha_devolucion and pedido.fecha_devolucion > ahora else ahora
        nueva_fecha = base + timedelta(days=DIAS_EXTENSION)

        pedido.fecha_devolucion = nueva_fecha
        pedido.extensiones_plazo += 1
        pedido.notif_vencimiento_enviada = False
        pedido.estado = "entregado"
        pedido.fch_ult_act = ahora
        pedido.save(update_fields=["fecha_devolucion", "extensiones_plazo", "notif_vencimiento_enviada", "estado", "fch_ult_act"])

    extensiones_restantes = MAX_EXTENSIONES - pedido.extensiones_plazo
    legacy_usuario._crear_notificacion(
        usuario=request.user,
        tipo="aviso_devolucion",
        titulo="Plazo de devolucion extendido",
        mensaje=(
            f"Extendiste el plazo del pedido #{pedido.id_pedido}. "
            f"Nueva fecha limite: {nueva_fecha.strftime('%d/%m/%Y %H:%M')}. "
            + (
                f"Te quedan {extensiones_restantes} extension{'es' if extensiones_restantes != 1 else ''} disponible{'s' if extensiones_restantes != 1 else ''}."
                if extensiones_restantes > 0
                else "No tienes mas extensiones disponibles. Debes devolver los productos."
            )
        ),
        pedido_id=pedido.id_pedido,
    )
    legacy_usuario._notificar_staff(
        tipo="aviso_devolucion",
        titulo=f"Pedido #{pedido.id_pedido} - plazo extendido",
        mensaje=(
            f"{request.user.nombre or ''} {request.user.apellido or ''}".strip() or request.user.correo
        ) + (
            f" extendio el plazo del pedido #{pedido.id_pedido} "
            f"(extension {pedido.extensiones_plazo}/{MAX_EXTENSIONES}). "
            f"Nueva fecha: {nueva_fecha.strftime('%d/%m/%Y %H:%M')}."
        ),
        pedido_id=pedido.id_pedido,
    )
    messages.success(
        request,
        f"Plazo extendido hasta el {nueva_fecha.strftime('%d/%m/%Y')}. "
        + (
            f"Te quedan {extensiones_restantes} extension{'es' if extensiones_restantes != 1 else ''} disponible{'s' if extensiones_restantes != 1 else ''}."
            if extensiones_restantes > 0
            else "Esta fue tu ultima extension. Debes devolver los productos en la nueva fecha."
        ),
    )
    return redirect("pedidos_usuario")
