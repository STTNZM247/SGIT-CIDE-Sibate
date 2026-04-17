from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventario', '0012_auditoria_log'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='telefono',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='usuario',
            name='programa_formacion',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='usuario',
            name='centro_desarrollo',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
