from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0024_alter_subcategoria_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='motivo_rechazo',
            field=models.TextField(blank=True, null=True),
        ),
    ]
