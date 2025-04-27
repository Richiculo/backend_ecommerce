from django.db import models
from direcciones.models import Direccion
#Modelo: Departamento
class Departamento(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


# Modelo: Sucursal
class Sucursal(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    direccion = models.OneToOneField(Direccion, on_delete=models.CASCADE, null=True, blank=True)



    def __str__(self):
        return self.nombre