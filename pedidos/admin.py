from django.contrib import admin

from .models import Cart, ItemCart, Metodo_Pago, Pago, Detalle_Venta, Venta

admin.site.register(Cart)
admin.site.register(ItemCart)
admin.site.register(Metodo_Pago)
admin.site.register(Pago)
admin.site.register(Detalle_Venta)
admin.site.register(Venta)