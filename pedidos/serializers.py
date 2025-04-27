from rest_framework import serializers
from .models import Cart, ItemCart, Metodo_Pago, Pago, Detalle_Venta, Venta
from usuarios.serializers import UsuarioSerializer

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


class ItemCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCart
        fields = '__all__'


class MetodoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metodo_Pago
        fields = '__all__'


class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = '__all__'


class DetalleVentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detalle_Venta
        fields = '__all__'



class VentaSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)
    class Meta:
        model = Venta
        fields = ['id', 'fecha', 'total', 'estado', 'pago', 'nombre']  # Incluye 'nombre' y excluye 'usuario'