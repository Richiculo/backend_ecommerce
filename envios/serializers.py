from rest_framework import serializers
from .models import AgenciaDelivery, Envio

class AgenciaDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = AgenciaDelivery
        fields = '__all__'

class EnvioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Envio
        fields = '__all__'
        read_only_fields = ['cliente', 'fecha_envio', 'fecha_entrega']