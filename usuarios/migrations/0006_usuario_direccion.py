# Generated by Django 5.2 on 2025-04-19 04:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('direcciones', '0003_remove_direccion_sucursal_remove_direccion_usuario'),
        ('usuarios', '0005_usuario_groups_usuario_is_superuser_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='direccion',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='direcciones.direccion'),
        ),
    ]
