from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Stock_sucursal
from notificaciones.models import Notificacion
from django.contrib.auth import get_user_model


def actualizar_stock_total(producto):
    total = sum([s.stock for s in producto.stock_sucursal_set.all()])
    producto.stock_total = total
    producto.save()

@receiver([post_save, post_delete], sender=Stock_sucursal)
def actualizar_stock(sender, instance, **kwargs):
    actualizar_stock_total(instance.producto)

Usuario = get_user_model()

def verificar_stock_bajo(sender, instance, **kwargs):
    producto = instance.producto
    STOCK_MINIMO_GLOBAL = 5
    if instance.cantidad < STOCK_MINIMO_GLOBAL:
        admins = Usuario.objects.filter(is_superuser=True)
        for admin in admins:
            Notificacion.objects.create(
                titulo=f"Stock bajo: {producto.nombre}",
                mensaje=f"El stock del producto '{producto.nombre}' en la sucursal '{instance.sucursal.nombre}' está por debajo del mínimo.",
                usuario = admin,
                tipo='stock_bajo'
            )