from django.shortcuts import render
from .serializers import SucursalSerializer
from rest_framework import viewsets
# Create your views here.

from .models import Sucursal

class SucursalViewSet(viewsets.ModelViewSet):
    queryset = Sucursal.objects.all()
    serializer_class = SucursalSerializer
