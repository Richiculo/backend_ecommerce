from django.db import models

# Modelo: Proveedor
class Proveedor(models.Model):
    nombre=models.CharField(max_length=100)


#Modelo: Producto

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(max_length=200)


    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nombre


# Modelo: Detalle producto
    
class Detalle_Producto(models.Model):
    marca = models.CharField(max_length=100)
    precio_venta = models.DecimalField
    precio_compra = models.DecimalField

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.marca
    

# Modelo: Categoria
    
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(max_length=200)
    

    def __str__(self):
        return self.nombre

# Modelo: Categoria_Producto
    
class Detalle_Producto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.producto


# Modelo: Stock_sucursal
    
class Stock_sucursal(models.Model):
    stock = models.IntegerField
    
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, null=True, blank=True)
    sucursal = models.ForeignKey('sucursales.Sucursal',on_delete=models.CASCADE, null=True, blank=True)

    

    def __str__(self):
        return self.nombre
 
