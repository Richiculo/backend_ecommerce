from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
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
        if password:
            instance.password = make_password(password)
        return super().update(instance, validated_data)