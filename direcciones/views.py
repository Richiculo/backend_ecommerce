from django.shortcuts import render
from rest_framework import viewsets
from .models import Direccion
from .serializers import DireccionSerializer
# Create your views here.

class DireccionViewSet(viewsets.ModelViewSet):
    queryset = Direccion.objects.all()
    serializer_class = DireccionSerializer