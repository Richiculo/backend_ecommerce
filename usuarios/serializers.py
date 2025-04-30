from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Usuario, ActivitylogUsuario, Rol
from direcciones.serializers import DireccionSerializer


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
    direccion = DireccionSerializer(required=False)  # Serializador anidado para la dirección
    rol = serializers.CharField(source='rol.nombre', read_only=False)
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
        # Extraer el nombre del rol del validated_data
        rol_nombre = validated_data.pop('rol', {}).get('nombre', None)
        
        # Si se proporciona un rol, buscarlo y asignarlo al usuario
        if rol_nombre:
            try:
                rol = Rol.objects.get(nombre=rol_nombre)
                instance.rol = rol
            except Rol.DoesNotExist:
                raise serializers.ValidationError({"rol": "El rol especificado no existe."})
        
        # Manejar la actualización de la contraseña si está presente
        password = validated_data.pop('password', None)
        if password:
            instance.password = make_password(password)
        
        # Actualizar el resto de los campos
        return super().update(instance, validated_data)