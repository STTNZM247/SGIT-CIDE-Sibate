from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0027_macro_codes_and_producto_codigo'),
    ]

    operations = [
        migrations.AddField(
            model_name='subcategoria',
            name='descripcion',
            field=models.TextField(blank=True, null=True),
        ),
    ]
