from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0009_usuario_banner_usu'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='area_ubicacion',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pedido',
            name='foto_carnet',
            field=models.ImageField(blank=True, null=True, upload_to='pedidos/carnets/'),
        ),
        migrations.AddField(
            model_name='pedido',
            name='tipo_devolucion',
            field=models.CharField(blank=True, default='global', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='pedido',
            name='fecha_devolucion',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='detallepedido',
            name='fecha_devolucion',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
