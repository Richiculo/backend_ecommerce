from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# Modelo: Proveedor
class Proveedor(models.Model):
    nombre=models.CharField(max_length=100, unique = True)
    contacto = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null = True)
    correo = models.EmailField(blank=True, null=True)
    
    def __str__(self):
        return self.nombre


# Modelo: Categoria
    
class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(max_length=200, blank=True)
    

    def __str__(self):
        return self.nombre


#Modelo: Producto

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(max_length=200)
    categorias = models.ManyToManyField(Categoria, through='Categoria_Producto')
    esta_activo = models.BooleanField(default=True)
    esta_disponible = models.BooleanField(default=True)
    stock_total = models.IntegerField(default=0)
    
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, null=True, blank=True)
    
    def actualizar_stock_total(self):
        total = sum([s.stock for s in self.stock_sucursal_set.all()])
        self.stock_total = total
        self.save()

    def __str__(self):
        return self.nombre


#Modelo: Imagenes de un producto

class Imagen_Producto(models.Model):
    producto = models.ForeignKey(Producto, related_name='imagenes', on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='productos/')
    descripcion = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Imagen de {self.producto.nombre}"


# Modelo: Detalle producto
    
class Detalle_Producto(models.Model):
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE, related_name='detalle',null=True, blank=True)
    marca = models.CharField(max_length=100, default='Generico')
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tiene_descuento = models.BooleanField(default=False)
    porcentaje_descuento = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    @property
    def precio_final(self):
        if self.tiene_descuento and self.porcentaje_descuento >0:
            descuento = (self.precio_venta * self.porcentaje_descuento) / 100
            return round(self.precio_venta - descuento, 2)
        return self.precio_venta


    def __str__(self):
        if self.producto:
            return f"{self.producto.nombre} - {self.marca}"
        return f"Sin producto asignado - {self.marca}"
    

# Modelo: Categoria_Producto
    
class Categoria_Producto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('producto', 'categoria')
        verbose_name = 'Relación Producto-Categoría'
        verbose_name_plural = 'Relaciones Producto-Categoría'

    def __str__(self):
        return f"{self.producto.nombre} - {self.categoria.nombre}"


# Modelo: Stock_sucursal
    
class Stock_sucursal(models.Model):
    stock = models.PositiveIntegerField(default=0)
    
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    sucursal = models.ForeignKey('sucursales.Sucursal',on_delete=models.CASCADE)

    class Meta:
        unique_together = ('producto', 'sucursal')
        verbose_name = 'Stock en Sucursal'
        verbose_name_plural = 'Stock en Sucursales'

    def __str__(self):
        return f"{self.producto.nombre} - {self.sucursal.nombre} - {self.stock}"
 
