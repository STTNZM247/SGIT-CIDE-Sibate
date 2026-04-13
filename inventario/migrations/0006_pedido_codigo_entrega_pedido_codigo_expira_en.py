from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0005_pedido_detallepedido'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='codigo_entrega',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
        migrations.AddField(
            model_name='pedido',
            name='codigo_expira_en',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
