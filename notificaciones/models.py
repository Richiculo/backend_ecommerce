from django.db import models
from usuarios.models import Usuario

class Notificacion(models.Model):
    titulo = models.CharField(max_length=255)
    mensaje = models.TextField()
    fecha_creada = models.DateField(auto_now_add=True)
    leida = models.BooleanField(default=False)

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE,related_name='notificaciones') 

    def __str__(self):
        return f"{self.usuario.correo} - {self.tipo} - {self.titulo}"

