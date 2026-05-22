from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0022_producto_campos_subcategoria'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImportacionInventarioLog',
            fields=[
                ('id_log_import', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_archivo', models.CharField(max_length=255)),
                ('estado', models.CharField(default='ok', max_length=20)),
                ('total_productos', models.PositiveIntegerField(default=0)),
                ('total_creados', models.PositiveIntegerField(default=0)),
                ('total_actualizados', models.PositiveIntegerField(default=0)),
                ('total_imagenes_principales', models.PositiveIntegerField(default=0)),
                ('total_imagenes_secundarias', models.PositiveIntegerField(default=0)),
                ('total_errores', models.PositiveIntegerField(default=0)),
                ('resumen', models.TextField(blank=True, null=True)),
                ('fch_registro', models.DateTimeField(auto_now_add=True)),
                ('id_usuario_fk', models.ForeignKey(blank=True, db_column='id_usuario_fk', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='importaciones_inventario', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'importacion_inventario_log',
                'ordering': ['-fch_registro', '-id_log_import'],
            },
        ),
    ]
