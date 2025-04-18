from django.db import models

#Modelo: Carrito

class Cart(models.Model):
    usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE)
    creado_en = models.DateTimeField(auto_now=True)
    ESTADOS = [
        ('activo', 'Activo'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS,default='activo')

    def __str__(self):
        return f"Carrito de {self.usuario}"
    

#Modelo: Productos para el carrito
    
class ItemCart(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey('productos.Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.producto}"


#Modelo: Metodos de pago

class Metodo_Pago(models.Model):
    nombre = models.CharField(max_length=50) #tarjeta,qr,transferencia
    proveedor = models.CharField(max_length=100, blank=True, null=True) #Stripe, banco bnb...
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


#Modelo: Pago venta

class Pago(models.Model):
    metodo = models.ForeignKey(Metodo_Pago, on_delete=models.SET_NULL, null = True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices = [
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
        ('fallido', 'Fallido'),
    ])
    fecha = models.DateTimeField(auto_now_add=True)
    referencia = models.CharField(max_length=255, blank=True, null=True) #codigo de qr, id de transferencia...

    def __str__(self):
        return f"{self.metodo.nombre} - {self.estado}"


#Modelo: Venta/Pedido

class Venta(models.Model):
    usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE)

    pago = models.OneToOneField(Pago, on_delete=models.SET_NULL, null=True, blank=True)
    fecha = models.DateTimeField(auto_now=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=50, choices=[
        ('pendiente', 'Pendiente'),
        ('procesando','Procesando'),
        ('enviado','Enviado'),
        ('entregado','Entregado'),
        ('cancelado','Cancelado')
    ])

    def __str__(self):
        return f"Venta #{self.id} - {self.usuario.correo}"


#Modelo: Detalle de la venta

class Detalle_Venta(models.Model):
    venta = models.ForeignKey(Venta, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey('productos.Producto', on_delete=models.CASCADE)
    cantidad = models. PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto} x {self.cantidad}"


#Modelo: Seguimiento de un pedido
"""    
class Seguimiento_Pedido(models.Model):
    venta = models.OneToOneField(Venta, on_delete=models.CASCADE, related_name = 'seguimiento')
    direccion_envio = models.CharField(max_length = 255)
    ciudad = models.CharField(max_length=100)
    fecha_creacion = models.DateTimeField(auto_now=True)
    fecha_estimada = models.DateTimeField()
"""
