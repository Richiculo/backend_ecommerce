from rest_framework import serializers
from .models import Direccion
from sucursales.serializers import DepartamentoSerializer


class DireccionSerializer(serializers.ModelSerializer):
    # Se puede incluir el serializador de sucursal si es necesario
    departamento = DepartamentoSerializer(read_only=True)  # Serializa el departamento relacionado
    class Meta: 
        model = Direccion
        fields = '__all__'  # Serializa todos los campos del modelo
        read_only_fields = ['id']  # Solo lectura para el campo 'id'

