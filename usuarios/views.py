from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UsuarioSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import make_password
from rest_framework import status, viewsets
from django.shortcuts import get_object_or_404
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import Usuario, Rol
from django.utils import timezone


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer


# Create your views here.
@api_view(['POST'])
def register(request):
    serializer = UsuarioSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        rol_cliente = Rol.objects.get(pk=2)
        user = serializer.save(rol=rol_cliente)
        user = Usuario.objects.get(correo=serializer.data['correo'])
        user.save();
        
        token = Token.objects.create(user=user)
        return Response({"token": token.key, "usuario": serializer.data}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    user = get_object_or_404(Usuario, correo=request.data['correo'])

    if not user.check_password(request.data['password']):
        return Response({"error": "Contraseña invalida"}, status=status.HTTP_400_BAD_REQUEST)
    user.last_login = timezone.now()
    user.save()
    token, created = Token.objects.get_or_create(user=user)
    serializer = UsuarioSerializer(instance=user)

    return Response({"token": token.key, "user": serializer.data}, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def perfil(request):
    print(request.user)
    return Response("Estas logeado con {}".format(request.user.nombre),status=status.HTTP_200_OK)

@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def actualizar_usuario(request):
    user = request.user
    serializer = UsuarioSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Usuario actualizado", "usuario": serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

