# Generated by Django 5.2 on 2025-04-19 04:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('direcciones', '0002_alter_direccion_departamento'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='direccion',
            name='sucursal',
        ),
        migrations.RemoveField(
            model_name='direccion',
            name='usuario',
        ),
    ]
