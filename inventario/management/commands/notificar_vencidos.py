"""
Management command: notificar_vencidos
Detecta pedidos entregados cuya fecha_devolucion ya pasó y que aún no fueron
marcados como devueltos. Envía una notificación interna y un correo al usuario.

Uso:
    python manage.py notificar_vencidos

Programar en PythonAnywhere (Tasks) para ejecutarse diariamente:
    cd ~/SGIT-CIDE-Sibate && workon entorno_sibate && python manage.py notificar_vencidos
"""

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.utils import timezone

from inventario.models import Notificacion, Pedido


class Command(BaseCommand):
    help = 'Envía notificaciones y correos a usuarios con préstamos vencidos'

    def handle(self, *args, **options):
        ahora = timezone.now()

        # Pedidos entregados, con fecha de devolución vencida,
        # que aún no han recibido notificación de vencimiento
        vencidos = Pedido.objects.filter(
            estado='entregado',
            fecha_devolucion__lt=ahora,
            notif_vencimiento_enviada=False,
        ).select_related('id_usuario_fk')

        total = vencidos.count()
        if total == 0:
            self.stdout.write('Sin préstamos vencidos nuevos.')
            return

        enviados = 0
        for pedido in vencidos:
            usuario = pedido.id_usuario_fk
            nombre  = getattr(usuario, 'nombre', '') or str(usuario)
            correo  = getattr(usuario, 'correo', None) or getattr(usuario, 'email', None)
            dias_vencido = (ahora - pedido.fecha_devolucion).days

            # ── Notificación interna ──────────────────────────────────────
            try:
                Notificacion.objects.create(
                    id_usuario_fk=usuario,
                    tipo='prestamo_vencido',
                    titulo='⚠️ Tu préstamo está vencido',
                    mensaje=(
                        f'El préstamo #{pedido.id_pedido} venció hace '
                        f'{dias_vencido} día{"s" if dias_vencido != 1 else ""}. '
                        'Por favor devuelve los productos o solicita más tiempo '
                        'a un almacenista.'
                    ),
                    id_pedido_ref=pedido.id_pedido,
                )
            except Exception as e:
                self.stderr.write(f'Error notificación pedido {pedido.id_pedido}: {e}')

            # ── Correo ────────────────────────────────────────────────────
            if correo:
                try:
                    _enviar_correo_vencimiento(pedido, usuario, nombre, correo, dias_vencido)
                except Exception as e:
                    self.stderr.write(f'Error correo pedido {pedido.id_pedido}: {e}')

            # ── Marcar como notificado ────────────────────────────────────
            pedido.notif_vencimiento_enviada = True
            pedido.save(update_fields=['notif_vencimiento_enviada'])
            enviados += 1

        self.stdout.write(self.style.SUCCESS(
            f'Notificaciones enviadas: {enviados}/{total}'
        ))


def _enviar_correo_vencimiento(pedido, usuario, nombre, correo, dias_vencido):
    fecha_str = pedido.fecha_devolucion.strftime('%d/%m/%Y')
    asunto = f'⚠️ Préstamo vencido – Pedido #{pedido.id_pedido} | Almacén SENA Sibaté'
    remitente = getattr(settings, 'DEFAULT_FROM_EMAIL', 'almacensedelacolonia@gmail.com')

    texto_plano = (
        f'Hola {nombre},\n\n'
        f'Tu préstamo #{pedido.id_pedido} venció el {fecha_str} '
        f'(hace {dias_vencido} día{"s" if dias_vencido != 1 else ""}).\n'
        'Por favor devuelve los productos o comunícate con un almacenista '
        'para solicitar más tiempo.\n\n'
        '— Almacén SENA Sibaté'
    )

    html = f"""
<!DOCTYPE html>
<html lang="es">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f4f4f4;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f4;padding:32px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0"
             style="background:#fff;border-radius:12px;overflow:hidden;
                    box-shadow:0 2px 12px rgba(0,0,0,0.08);max-width:600px;width:100%;">
        <!-- Cabecera -->
        <tr>
          <td style="background:#39A900;padding:28px 32px;text-align:center;">
            <p style="margin:0;color:#fff;font-size:13px;opacity:0.85;">SENA — Almacén Sibaté</p>
            <h1 style="margin:8px 0 0;color:#fff;font-size:24px;">⚠️ Préstamo vencido</h1>
          </td>
        </tr>
        <!-- Cuerpo -->
        <tr>
          <td style="padding:32px;">
            <p style="font-size:16px;color:#333;">Hola <strong>{nombre}</strong>,</p>
            <p style="font-size:15px;color:#444;line-height:1.6;">
              Tu préstamo <strong>#{pedido.id_pedido}</strong> tenía fecha de devolución el
              <strong>{fecha_str}</strong> y lleva
              <strong>{dias_vencido} día{"s" if dias_vencido != 1 else ""}</strong> vencido.
            </p>
            <!-- Aviso destacado -->
            <table width="100%" cellpadding="0" cellspacing="0" style="margin:24px 0;">
              <tr>
                <td style="background:#fff8e1;border-left:4px solid #ff8200;
                            border-radius:6px;padding:16px 20px;">
                  <p style="margin:0;font-size:15px;color:#333;">
                    Por favor <strong>devuelve los productos</strong> o comunícate con
                    un almacenista para <strong>solicitar más tiempo</strong>.
                  </p>
                </td>
              </tr>
            </table>
            <p style="font-size:13px;color:#888;margin-top:32px;">
              Si ya devolviste los productos, ignora este mensaje.<br>
              — Almacén SENA Sibaté
            </p>
          </td>
        </tr>
        <!-- Pie -->
        <tr>
          <td style="background:#f9f9f9;padding:16px 32px;text-align:center;
                      border-top:1px solid #eee;">
            <p style="margin:0;font-size:12px;color:#aaa;">
              Centro Industrial y de Desarrollo Empresarial – Sibaté, Cundinamarca
            </p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>
"""

    msg = EmailMultiAlternatives(asunto, texto_plano, remitente, [correo])
    msg.attach_alternative(html, 'text/html')
    msg.send()
