from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Notificacion
from .serializers import NotificacionSerializer

class NotificacionViewSet(viewsets.ModelViewSet):
    serializer_class = NotificacionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Notificacion.objects.filter(usuario=user).order_by('-fecha_creacion')

