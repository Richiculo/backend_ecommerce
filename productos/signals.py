from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Stock_sucursal

def actualizar_stock_total(producto):
    total = sum([s.stock for s in producto.stock_sucursal_set.all()])
    producto.stock_total = total
    producto.save()

@receiver([post_save, post_delete], sender=Stock_sucursal)
def actualizar_stock(sender, instance, **kwargs):
    actualizar_stock_total(instance.producto)