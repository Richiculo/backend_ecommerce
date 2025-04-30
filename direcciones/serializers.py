from rest_framework import serializers
from .models import Direccion
from sucursales.serializers import DepartamentoSerializer

class DireccionSerializer(serializers.ModelSerializer):
    departamento = serializers.CharField(source='departamento.nombre', read_only=True)
    class Meta: 
        model = Direccion
        fields = '__all__'  # Serializa todos los campos del modelo
        read_only_fields = ['id']  # Solo lectura para el campo 'id'

