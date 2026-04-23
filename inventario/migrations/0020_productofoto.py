from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0019_usuario_verificacion_sena_documento_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductoFoto',
            fields=[
                ('id_foto', models.AutoField(primary_key=True, serialize=False)),
                ('foto', models.ImageField(upload_to='productos/fotos/')),
                ('orden', models.PositiveSmallIntegerField(default=0)),
                ('fch_registro', models.DateTimeField(auto_now_add=True)),
                ('id_prod_fk', models.ForeignKey(
                    db_column='id_prod_fk',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='fotos',
                    to='inventario.producto',
                )),
            ],
            options={
                'db_table': 'producto_foto',
                'ordering': ['orden', 'id_foto'],
            },
        ),
    ]
