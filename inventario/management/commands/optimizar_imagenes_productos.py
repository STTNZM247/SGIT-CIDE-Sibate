from django.core.management.base import BaseCommand

from inventario.image_optim import optimize_image_field_to_webp
from inventario.models import Producto


class Command(BaseCommand):
    help = 'Optimiza imágenes existentes de productos a WEBP (redimensiona y comprime).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo muestra cuántas imágenes se procesarían sin guardar cambios.',
        )

    def handle(self, *args, **options):
        dry_run = bool(options.get('dry_run'))
        productos = Producto.objects.exclude(fot_prod='').exclude(fot_prod__isnull=True).order_by('id_prod')

        total = 0
        optimized = 0
        skipped = 0

        for producto in productos:
            total += 1
            if dry_run:
                self.stdout.write(f'[DRY-RUN] Producto #{producto.id_prod}: {producto.fot_prod.name}')
                continue

            ok = optimize_image_field_to_webp(producto.fot_prod)
            if ok:
                producto.save(update_fields=['fot_prod'])
                optimized += 1
                self.stdout.write(self.style.SUCCESS(f'Optimizada: Producto #{producto.id_prod}'))
            else:
                skipped += 1
                self.stdout.write(self.style.WARNING(f'Sin cambios: Producto #{producto.id_prod}'))

        if dry_run:
            self.stdout.write(self.style.WARNING(f'DRY-RUN completado. Imágenes detectadas: {total}'))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'Proceso completado. Total: {total}, optimizadas: {optimized}, sin cambios: {skipped}'
            ))
