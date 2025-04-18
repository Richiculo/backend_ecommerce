from rest_framework import serializers
from .models import Producto, Categoria, Proveedor, Detalle_Producto, Categoria_Producto, Stock_sucursal, Imagen_Producto

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
    descuento =serializers.SerializerMethodField()
    imagenes =serializers.SerializerMethodField()
    detalle =serializers.SerializerMethodField()
    categorias =serializers.SerializerMethodField()
    stock_total =serializers.IntegerField(read_only=True)
    proveedor = serializers.StringRelatedField()

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'descripcion', 'proveedor',
            'descuento', 'imagenes', 'stock_total',
            'detalle', 'categorias'
        ]

    def get_descuento(self, obj):
        if hasattr(obj, 'detalle') and obj.detalle.tiene_descuento:
            return float(obj.detalle.porcentaje_descuento)
        return None

    def get_imagenes(self, obj):
        return [img.imagen.url for img in obj.imagenes.all()]

    def get_detalle(self, obj):
        if hasattr(obj, 'detalle'):
            return {
                'marca': obj.detalle.marca,
                'precio': float(obj.detalle.precio_final)
            }
        return None

    def get_categorias(self, obj):
        return [
            {
                'nombre': cat.nombre,
                'descripcion': cat.descripcion
            }
            for cat in obj.categorias.all()
        ]

class DetalleProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detalle_Producto
        fields = '__all__'

class ImagenProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imagen_Producto
        fields = '__all__'



class StockSucursalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock_sucursal
        fields = '__all__'