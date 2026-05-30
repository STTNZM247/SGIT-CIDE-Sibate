"""Adaptadores HTTP para pedidos de usuario."""

from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from inventario import views_usuario as legacy_views_usuario
from inventario.application.pedidos import use_cases


@login_required
def pedidos_usuario(request):
	if not legacy_views_usuario._usuario_cliente(request):
		return redirect("dashboard")
	context = use_cases.obtener_contexto_pedidos_usuario(request)
	return render(request, "inventario/usuario/pedidos_usuario.html", context)


@login_required
def pedido_codigo_devolucion(request, pedido_id):
	if not legacy_views_usuario._usuario_cliente(request):
		return JsonResponse({"ok": False, "error": "No autorizado."}, status=403)
	return use_cases.codigo_devolucion_usuario(request, pedido_id)


@login_required
@require_POST
def pedido_cancelar_usuario(request, pedido_id):
	if not legacy_views_usuario._usuario_cliente(request):
		return redirect("dashboard")
	return use_cases.cancelar_pedido_usuario(request, pedido_id)


@login_required
@require_POST
def pedido_extender_plazo(request, pedido_id):
	if not legacy_views_usuario._usuario_cliente(request):
		return redirect("dashboard")
	return use_cases.extender_plazo_usuario(request, pedido_id)
