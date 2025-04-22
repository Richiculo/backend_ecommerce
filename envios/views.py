from rest_framework import viewsets, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from .models import AgenciaDelivery, Envio
from .serializers import AgenciaDeliverySerializer, EnvioSerializer
from pedidos.models import Venta

class AgenciaDeliveryViewSet(viewsets.ModelViewSet):
    queryset = AgenciaDelivery.objects.all()
    serializer_class = AgenciaDeliverySerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]

class IsStaffOrOwner(permissions.BasePermission):
    """
    SAFE_METHODS: cualquier usuario autenticado puede leer.
    Escritura solo staff
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_staff
    
class EnvioViewSet(viewsets.ModelViewSet):
    """
    Gestiona envíos:
    - Clientes pueden listar/visualizar sus envíos.
    - Staff puede crear, modificar o eliminar cualquiera.
    """
    queryset = Envio.objects.all()
    serializer_class = EnvioSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsStaffOrOwner]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Envio.objects.all()
        return Envio.objects.filter(cliente=user)
    
    def perform_create(self, serializer):
        venta = serializer.validated_data.get('venta')
        if not self.request.user.is_staff and venta.usuario != self.request.user:
            raise PermissionDenied("No puedes crear envios para ventas de otros usuarios")
        serializer.save(cliente=venta.usuario)
    
    def perform_update(self, serializer):
        envio = self.get_object()
        nuevo_estado = serializer.validated_data.get('estado')
        if nuevo_estado and nuevo_estado != envio.estado:
            if nuevo_estado == 'en camino':
                serializer.save(fecha_envio=timezone.now())
                return
            if nuevo_estado == 'entregado':
                serializer.save(fecha_entrega=timezone.now())
                return
        serializer.save()

