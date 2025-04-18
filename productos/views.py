from django.shortcuts import render
from rest_framework import viewsets
from .models import Producto, Proveedor, Detalle_Producto, Categoria, Stock_sucursal, Imagen_Producto
from .serializers import ProductoSerializer, ProveedorSerializer, DetalleProductoSerializer, CategoriaSerializer, StockSucursalSerializer, ImagenProductoSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

class DetalleProductoViewSet(viewsets.ModelViewSet):
    queryset = Detalle_Producto.objects.all()
    serializer_class = DetalleProductoSerializer

class StockSucursalViewSet(viewsets.ModelViewSet):
    queryset = Stock_sucursal.objects.all()
    serializer_class = StockSucursalSerializer

class ImagenProductoViewSet(viewsets.ModelViewSet):
    queryset = Imagen_Producto.objects.all()
    serializer_class = ImagenProductoSerializer
