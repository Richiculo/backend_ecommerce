from django.shortcuts import render
from rest_framework import viewsets
from .models import Producto, Proveedor, Detalle_Producto, Categoria, Stock_sucursal, Imagen_Producto
from .serializers import ProductoSerializer, ProveedorSerializer, DetalleProductoSerializer, CategoriaSerializer, StockSucursalSerializer, ImagenProductoSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


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


class DescuentoViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = Detalle_Producto.objects.all()
        serializer = DetalleProductoSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        serializer = DetalleProductoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk=None):
        descuento = self.get_object(pk)
        serializer = DetalleProductoSerializer(descuento, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['POST'])
    def activar(self, request, pk=None):
        descuento = self.get_object(pk)
        descuento.tiene_descuento = True
        descuento.save()
        return Response({"status": "descuento activado"})
    
    @action(detail=True, methods=['POST'])
    def desactivar(self, request, pk=None):
        descuento = self.get_object(pk)
        descuento.tiene_descuento = False
        descuento.save()
        return Response({"status": "descuento desactivado"})
    
    def get_object(self, pk):
        return Detalle_Producto.objects.get(pk=pk)