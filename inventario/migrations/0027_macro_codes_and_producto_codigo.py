from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0026_ubicacionproducto_catalogo_id_ubicacion_fk'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalogo',
            name='codigo_macro',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='producto',
            name='codigo_producto',
            field=models.CharField(blank=True, max_length=40, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='subcategoria',
            name='codigo_clasificacion',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
