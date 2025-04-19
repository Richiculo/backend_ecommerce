from rest_framework import serializers
from .models import Direccion

class DireccionSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Direccion
        fields = '__all__'  # Serializa todos los campos del modelo
        read_only_fields = ['id']  # Solo lectura para el campo 'id'

