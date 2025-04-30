from rest_framework import serializers
from .models import Sucursal, Departamento


class SucursalSerializer(serializers.ModelSerializer):
    departamento = serializers.SerializerMethodField()  # Campo personalizado para el nombre del departamento

    class Meta:
        model = Sucursal
        fields = ['id', 'nombre', 'telefono', 'departamento']  # Incluye el campo 'departamento'


    def get_departamento(self, obj):
        # Verifica si la sucursal tiene una dirección asociada y si esa dirección tiene un departamento
        if obj.direccion and obj.direccion.departamento:
            return obj.direccion.departamento.nombre
        return None  # Devuelve None si no hay departamento asociado


class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
        }