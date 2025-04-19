from django.contrib import admin
from .models import Proveedor, Categoria, Producto, Categoria_Producto, Imagen_Producto, Detalle_Producto, Stock_sucursal
# Register your models here.
admin.site.register(Proveedor)
admin.site.register(Categoria)
admin.site.register(Producto)
admin.site.register(Categoria_Producto)
admin.site.register(Imagen_Producto)
admin.site.register(Detalle_Producto)
admin.site.register(Stock_sucursal)