from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


def seed_tipos_doc(apps, schema_editor):
    TipoDoc = apps.get_model('inventario', 'TipoDoc')
    now = timezone.now()
    for codigo, nombre in [
        ('CC', 'Cedula de ciudadania'),
        ('TI', 'Tarjeta de identidad'),
    ]:
        TipoDoc.objects.update_or_create(
            codigo=codigo,
            defaults={
                'nombre': nombre,
                'fch_registro': now,
                'fch_ult_act': now,
            },
        )


def unseed_tipos_doc(apps, schema_editor):
    TipoDoc = apps.get_model('inventario', 'TipoDoc')
    TipoDoc.objects.filter(codigo__in=['CC', 'TI']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0017_tema_usuario'),
    ]

    operations = [
        migrations.CreateModel(
            name='TipoDoc',
            fields=[
                ('id_tipo_doc', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=60, unique=True)),
                ('codigo', models.CharField(max_length=10, unique=True)),
                ('fch_registro', models.DateTimeField(blank=True, null=True)),
                ('fch_ult_act', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'tipo_doc',
                'ordering': ['id_tipo_doc'],
            },
        ),
        migrations.AddField(
            model_name='usuario',
            name='id_tipo_doc_fk',
            field=models.ForeignKey(blank=True, db_column='id_tipo_doc_fk', null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventario.tipodoc'),
        ),
        migrations.RunPython(seed_tipos_doc, unseed_tipos_doc),
    ]
