from django.db import models



# Modelo: Direccion

class Direccion(models.Model):
    pais = models.CharField(max_length=50)
    ciudad = models.CharField(max_length=50)
    zona = models.CharField(max_length=50, blank=True, null=True)
    calle = models.CharField(max_length=100)
    numero = models.CharField(max_length=10)
    referencia = models.TextField(blank=True, null=True)
    departamento = models.ForeignKey('sucursales.Departamento', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.calle} #{self.numero}, {self.zona or ''} - {self.ciudad}, {self.departamento}, {self.pais}"
