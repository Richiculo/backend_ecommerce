# Generated by Django 5.2 on 2025-04-17 23:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_permiso_rol_usuario_apellidos_usuario_is_active_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usuario',
            old_name='username',
            new_name='nombre',
        ),
    ]
