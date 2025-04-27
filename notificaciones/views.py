from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Notificacion
from .serializers import NotificacionSerializer
from rest_framework.authentication import TokenAuthentication

class NotificacionViewSet(viewsets.ModelViewSet):
    
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificacionSerializer
    def get_queryset(self):
        user = self.request.user
        return Notificacion.objects.filter(usuario=user).order_by('-fecha_creada')

