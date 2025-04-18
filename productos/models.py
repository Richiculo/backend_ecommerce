from django.db import models

# Modelo: Proveedor
class Proveedor(models.Model):
    nombre=models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre


# Modelo: Categoria
    
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(max_length=200)
    

    def __str__(self):
        return self.nombre


#Modelo: Producto

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(max_length=200)
    categorias = models.ManyToManyField(Categoria, through='Categoria_Producto')


    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nombre


# Modelo: Detalle producto
    
class Detalle_Producto(models.Model):
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE, related_name='detalle',null=True, blank=True)
    marca = models.CharField(max_length=100, default='Generico')
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)


    def __str__(self):
        return f"{self.producto.nombre} - {self.marca}"
    

# Modelo: Categoria_Producto
    
class Categoria_Producto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.producto.nombre} - {self.categoria.nombre}"


# Modelo: Stock_sucursal
    
class Stock_sucursal(models.Model):
    stock = models.IntegerField(default=0)
    
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, null=True, blank=True)
    sucursal = models.ForeignKey('sucursales.Sucursal',on_delete=models.CASCADE, null=True, blank=True)

    

    def __str__(self):
        return f"{self.producto.nombre} - {self.sucursal.nombre} - {self.stock}"
 
