from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Usuario, ActivitylogUsuario
from direcciones.models import Direccion
from direcciones.serializers import DireccionSerializer

class ActivitylogUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivitylogUsuario
        fields = '__all__'
        extra_kwargs = {
            'usuario': {'read_only': True},  # Solo lectura, se asigna automáticamente
            'fecha': {'read_only': True},    # Solo lectura, se asigna automáticamente
        }



class UsuarioSerializer(serializers.ModelSerializer):
    direccion = DireccionSerializer(required=False)  # Serializador anidado para la dirección
    activitylog = ActivitylogUsuarioSerializer(many=True, read_only=True)  # Serializador anidado para el log de actividad
    class Meta:
        model = Usuario
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
        }



    def create(self, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def validate_correo(self, value):
        user = getattr(self, 'instance', None)
        if Usuario.objects.exclude(pk=getattr(user, 'pk', None)).filter(correo=value).exists():
            raise serializers.ValidationError("Ese correo ya está registrado.")
        return value
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        direccion_data = self.initial_data.get('direccion_id')
        if direccion_data:
            try:
                direccion = Direccion.objects.get(pk=direccion_data)
                instance.direccion = direccion
            except Direccion.DoesNotExist:
                raise serializers.ValidationError({"direccion_id": "La dirección especificada no existe."})
        if password:
            instance.password = make_password(password)
        return super().update(instance, validated_data)