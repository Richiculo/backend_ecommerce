from rest_framework import serializers
from .models import Cart, ItemCart, Metodo_Pago, Pago, Detalle_Venta, Venta
from productos.serializers import ProductoSerializer
from productos.models import Producto


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


class ItemCartSerializer(serializers.ModelSerializer):
    producto = serializers.PrimaryKeyRelatedField(
        queryset=Producto.objects.all(), write_only=True
    )
    producto_detalle = ProductoSerializer(source='producto', read_only=True)
    class Meta:
        model = ItemCart
        fields = '__all__'
        read_only_fields = ['cart', 'precio_unitario']


class MetodoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metodo_Pago
        fields = '__all__'


class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = '__all__'


class DetalleVentaSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer(read_only = True)

    class Meta:
        model = Detalle_Venta
        fields = '__all__'



class VentaSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)
    class Meta:
        model = Venta
        fields = ['id', 'fecha', 'total', 'estado', 'pago', 'nombre']  # Incluye 'nombre' y excluye 'usuario'
class VentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venta
        fields = '__all__'
