from rest_framework import serializers
from .models import Sucursal, Departamento


class SucursalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sucursal
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
        }

class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
        }