from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0006_pedido_codigo_entrega_pedido_codigo_expira_en'),
    ]

    operations = [
        migrations.CreateModel(
            name='CarritoItem',
            fields=[
                ('id_carrito_item', models.AutoField(primary_key=True, serialize=False)),
                ('cantidad', models.PositiveIntegerField(default=1)),
                ('fch_registro', models.DateTimeField(blank=True, null=True)),
                ('fch_ult_act', models.DateTimeField(blank=True, null=True)),
                ('id_prod_fk', models.ForeignKey(db_column='id_prod_fk', on_delete=django.db.models.deletion.CASCADE, related_name='carrito_items', to='inventario.producto')),
                ('id_usuario_fk', models.ForeignKey(db_column='id_usuario_fk', on_delete=django.db.models.deletion.CASCADE, related_name='carrito_items', to='inventario.usuario')),
            ],
            options={
                'db_table': 'carrito_item',
            },
        ),
        migrations.AddConstraint(
            model_name='carritoitem',
            constraint=models.UniqueConstraint(fields=('id_usuario_fk', 'id_prod_fk'), name='uq_carrito_usuario_producto'),
        ),
    ]
