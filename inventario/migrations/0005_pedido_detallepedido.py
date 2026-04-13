from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0004_rol_nombre_rol'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id_pedido', models.AutoField(primary_key=True, serialize=False)),
                ('estado', models.CharField(default='pendiente', max_length=50)),
                ('total_productos', models.PositiveIntegerField(default=0)),
                ('total_unidades', models.PositiveIntegerField(default=0)),
                ('fch_registro', models.DateTimeField(blank=True, null=True)),
                ('fch_ult_act', models.DateTimeField(blank=True, null=True)),
                ('id_usuario_fk', models.ForeignKey(db_column='id_usuario_fk', on_delete=django.db.models.deletion.CASCADE, related_name='pedidos', to='inventario.usuario')),
            ],
            options={
                'db_table': 'pedido',
                'ordering': ['-fch_registro', '-id_pedido'],
            },
        ),
        migrations.CreateModel(
            name='DetallePedido',
            fields=[
                ('id_det_pedido', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_producto', models.CharField(max_length=255)),
                ('nombre_catalogo', models.CharField(blank=True, max_length=255, null=True)),
                ('cantidad_solicitada', models.PositiveIntegerField(default=1)),
                ('stock_referencia', models.IntegerField(blank=True, null=True)),
                ('estado_detalle', models.CharField(default='pendiente', max_length=50)),
                ('fch_registro', models.DateTimeField(blank=True, null=True)),
                ('fch_ult_act', models.DateTimeField(blank=True, null=True)),
                ('id_pedido_fk', models.ForeignKey(db_column='id_pedido_fk', on_delete=django.db.models.deletion.CASCADE, related_name='detalles', to='inventario.pedido')),
                ('id_prod_fk', models.ForeignKey(blank=True, db_column='id_prod_fk', null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventario.producto')),
            ],
            options={
                'db_table': 'detalle_pedido',
                'ordering': ['id_det_pedido'],
            },
        ),
    ]
