from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0021_alter_notificacion_tipo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subcategoria',
            fields=[
                ('id_subcat', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_subcategoria', models.CharField(max_length=255)),
                ('fch_registro', models.DateTimeField(blank=True, null=True)),
                ('fch_ult_act', models.DateTimeField(blank=True, null=True)),
                ('id_cat_fk', models.ForeignKey(db_column='id_cat_fk', on_delete=models.deletion.CASCADE, related_name='subcategorias', to='inventario.catalogo')),
            ],
            options={
                'db_table': 'subcategoria',
                'ordering': ['id_cat_fk_id', 'nombre_subcategoria'],
            },
        ),
        migrations.AddField(
            model_name='producto',
            name='cuentadante',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='producto',
            name='numero_placa',
            field=models.CharField(blank=True, max_length=80, null=True),
        ),
        migrations.AddField(
            model_name='producto',
            name='tipo_bien',
            field=models.CharField(choices=[('devolutivo', 'Devolutivo'), ('consumo', 'Consumo')], default='devolutivo', max_length=20),
        ),
        migrations.AddField(
            model_name='producto',
            name='ubicacion',
            field=models.CharField(default='Pendiente por asignar', max_length=255),
        ),
        migrations.AddField(
            model_name='producto',
            name='unidad_medida',
            field=models.CharField(choices=[('unidad', 'Unidad'), ('metro', 'Metro'), ('rollo', 'Rollo'), ('caja', 'Caja'), ('par', 'Par'), ('set', 'Set'), ('kg', 'Kilogramo'), ('litro', 'Litro')], default='unidad', max_length=20),
        ),
        migrations.AddField(
            model_name='producto',
            name='subcategorias',
            field=models.ManyToManyField(blank=True, related_name='productos', to='inventario.subcategoria'),
        ),
        migrations.AddConstraint(
            model_name='subcategoria',
            constraint=models.UniqueConstraint(fields=('id_cat_fk', 'nombre_subcategoria'), name='uq_subcat_catalogo_nombre'),
        ),
    ]
