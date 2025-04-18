from rest_framework import serializers
from .models import Producto, Categoria, Proveedor, Detalle_Producto, Categoria_Producto, Stock_sucursal 

class ProveedorSerializer(serializers.ModelSerializer):
    categorias = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )
    class Meta:
        model = Proveedor
        fields = '__all__'


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class ProductoSerializer(serializers.ModelSerializer):
    categorias = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )
    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'descripcion', 'proveedor', 'categorias']
    def create(self, validated_data):
        categorias_data = validated_data.pop('categorias', [])
        producto = Producto.objects.create(**validated_data)

        for cat_id in categorias_data:
            Categoria_Producto.objects.create(producto=producto, categoria_id=cat_id)

        return producto

class DetalleProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detalle_Producto
        fields = '__all__'


class StockSucursalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock_sucursal
        fields = '__all__'