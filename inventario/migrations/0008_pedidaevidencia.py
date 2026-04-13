from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0007_carritoitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='PedidoEvidencia',
            fields=[
                ('id_evidencia', models.AutoField(primary_key=True, serialize=False)),
                ('foto_evidencia', models.ImageField(upload_to='pedidos/evidencias/')),
                ('fch_registro', models.DateTimeField(blank=True, null=True)),
                ('id_pedido_fk', models.ForeignKey(db_column='id_pedido_fk', on_delete=django.db.models.deletion.CASCADE, related_name='evidencias', to='inventario.pedido')),
            ],
            options={
                'db_table': 'pedido_evidencia',
                'ordering': ['id_evidencia'],
            },
        ),
    ]
