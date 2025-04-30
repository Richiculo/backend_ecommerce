from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Usuario, ActivitylogUsuario, Rol
from direcciones.serializers import DireccionSerializer
from .models import Direccion

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'


class ActivitylogUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivitylogUsuario
        fields = '__all__'
        extra_kwargs = {
            'usuario': {'read_only': True},  # Solo lectura, se asigna automáticamente
            'fecha': {'read_only': True},    # Solo lectura, se asigna automáticamente
        }



class UsuarioSerializer(serializers.ModelSerializer):
    direccion = serializers.PrimaryKeyRelatedField(
    queryset=Direccion.objects.all(), required=False, allow_null=True
)


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
    # Rol (si se manda)
        rol = validated_data.pop('rol', None)
        if rol:
            instance.rol = rol

    # Contraseña (si se manda)
        password = validated_data.pop('password', None)
        if password:
            instance.password = make_password(password)

    # Dirección (obtenida desde initial_data porque es direccion_id, no un objeto anidado)
        direccion_id = self.initial_data.get('direccion_id')
        if direccion_id:
            try:
                direccion = Direccion.objects.get(pk=direccion_id)
                instance.direccion = direccion
            except Direccion.DoesNotExist:
                raise serializers.ValidationError({"direccion_id": "La dirección especificada no existe."})

    # El resto de los campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
