from django.db import models
from pedidos.models import Venta
from usuarios.models import Usuario
from direcciones.models import Direccion



class AgenciaDelivery(models.Model):
    nombre = models.CharField(max_length=100)
    contacto = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    esta_activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
    
class Envio(models.Model):
    ESTADOS_ENVIO = [
        ('pendiente', 'Pendiente'),
        ('en_camino', 'En camino'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]

    venta = models.OneToOneField(Venta, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    direccion_entrega = models.ForeignKey(Direccion, on_delete=models.SET_NULL, null=True, blank=True)
    agencia = models.ForeignKey(AgenciaDelivery, on_delete=models.SET_NULL, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS_ENVIO, default='pendiente')
    fecha_envio = models.DateTimeField(null=True, blank=True)
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    observaciones = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Envio #{self.id} - {self.venta.id}"

    
