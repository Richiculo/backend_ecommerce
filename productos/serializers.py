from rest_framework import serializers
from .models import Producto, Categoria, Proveedor, Detalle_Producto, Categoria_Producto, Stock_sucursal, Imagen_Producto
from sucursales.serializers import SucursalSerializer


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
            'detalle', 'categorias', 'esta_disponible',
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


class CategoriaProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria_Producto
        fields = '__all__'

class DetalleProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detalle_Producto
        fields = '__all__'

class ImagenProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Imagen_Producto
        fields = '__all__'



class StockSucursalSerializer(serializers.ModelSerializer):
    sucursal = serializers.CharField(source='sucursal.nombre', required=True)
    producto = serializers.CharField(source='producto.nombre', required=True)
    departamento = serializers.SerializerMethodField()  # Usar SerializerMethodField para obtener el departamento

    class Meta:
        model = Stock_sucursal
        fields = '__all__'

    def get_departamento(self, obj):
        # Verifica si la sucursal tiene una dirección asociada y si esa dirección tiene un departamento
        if obj.sucursal and obj.sucursal.direccion and obj.sucursal.direccion.departamento:
            return obj.sucursal.direccion.departamento.nombre
        return None  # Devuelve None si no hay departamento asociado

    def update(self, instance, validated_data):
        # Actualizar la sucursal
        sucursal_nombre = validated_data.pop('sucursal', {}).get('nombre', None)
        if sucursal_nombre:
            try:
                from sucursales.models import Sucursal  # Importar el modelo Sucursal
                sucursal = Sucursal.objects.get(nombre=instance.sucursal.nombre)  # Buscar la sucursal actual
                sucursal.nombre = sucursal_nombre  # Actualizar el nombre de la sucursal
                sucursal.save()  # Guardar los cambios
                instance.sucursal = sucursal
            except Sucursal.DoesNotExist:
                raise serializers.ValidationError({"sucursal": "La sucursal especificada no existe."})

        # Actualizar el producto
        producto_nombre = validated_data.pop('producto', {}).get('nombre', None)
        if producto_nombre:
            try:
                from productos.models import Producto  # Importar el modelo Producto
                producto = Producto.objects.get(nombre=instance.producto.nombre)  # Buscar el producto actual
                producto.nombre = producto_nombre  # Actualizar el nombre del producto
                producto.save()  # Guardar los cambios
                instance.producto = producto
            except Producto.DoesNotExist:
                raise serializers.ValidationError({"producto": "El producto especificado no existe."})

        # Actualizar el resto de los campos
        return super().update(instance, validated_data)