from rest_framework import serializers
from .models import Cart, ItemCart, Metodo_Pago, Pago, Detalle_Venta, Venta

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


class ItemCartSerializer(serializers.ModelSerializer):
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
    class Meta:
        model = Detalle_Venta
        fields = '__all__'


class VentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venta
        fields = '__all__'