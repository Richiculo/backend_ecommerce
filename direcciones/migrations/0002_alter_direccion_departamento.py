# Generated by Django 5.2 on 2025-04-17 21:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('direcciones', '0001_initial'),
        ('sucursales', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='direccion',
            name='departamento',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sucursales.departamento'),
        ),
    ]
