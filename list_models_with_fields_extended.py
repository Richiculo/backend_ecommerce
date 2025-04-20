import os
import django
from django.apps import apps

# Configurá tu entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_ecommerce.settings')  # 🔁 Cambiá esto
django.setup()

# Obtener todos los modelos
all_models = apps.get_models()

# Recorrer modelos
for model in all_models:
    print(f'\n📦 Modelo: {model.__module__}.{model.__name__}')
    print('-' * 60)

    for field in model._meta.get_fields():
        # Saltamos relaciones inversas automáticas
        if field.auto_created and not field.concrete:
            continue

        print(f'🧩 Campo: {field.name}')
        print(f'   ├─ Tipo: {field.get_internal_type()}')

        # Si es relación, mostrar a qué modelo apunta
        if field.is_relation:
            rel_model = field.related_model
            print(f'   ├─ Relación con: {rel_model.__module__}.{rel_model.__name__}')
            print(f'   ├─ Tipo de relación: {"ManyToMany" if field.many_to_many else "OneToOne" if field.one_to_one else "ForeignKey" if field.many_to_one else "Desconocida"}')

        # Info general de cualquier campo
        print(f'   ├─ Nulo: {getattr(field, "null", "N/A")}')
        print(f'   ├─ Único: {getattr(field, "unique", "N/A")}')
        print(f'   └─ Clave primaria: {getattr(field, "primary_key", "N/A")}')
    print()
