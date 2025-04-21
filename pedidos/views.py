from django.shortcuts import render
from rest_framework import viewsets, status
from .models import Cart, ItemCart, Metodo_Pago, Pago, Detalle_Venta, Venta
from productos.models import Producto
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from productos.models import Stock_sucursal
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import CartSerializer, ItemCartSerializer, MetodoPagoSerializer, PagoSerializer, DetalleVentaSerializer, VentaSerializer
from productos.serializers import ProductoSerializer
from rest_framework import serializers
from rest_framework.decorators import action
from pedidos.ml.recomendador import recomendar


class CartViewSet(viewsets.ModelViewSet):
    """
    - Solo usuarios autenticados pueden acceder.
    - Staff ve todos los carritos; clientes solo el suyo.
    - Al crear un carrito, se asocia al usuario que hace la petición.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes     = [IsAuthenticated]
    serializer_class       = CartSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Cart.objects.all()
        return Cart.objects.filter(usuario=user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class ItemCartViewSet(viewsets.ModelViewSet):
    """
    - Solo usuarios autenticados pueden acceder.
    - Staff ve todos los ítems; clientes solo los de su carrito.
    - Al crear un ítem, se asocia al carrito activo del usuario.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes     = [IsAuthenticated]
    serializer_class       = ItemCartSerializer
    
    @action(detail=False, methods=['GET'], url_path='recomendaciones')
    def recomendaciones(self, request):
        user = request.user
        try:
            cart = Cart.objects.get(usuario=user, estado='activo')
        except Cart.DoesNotExist:
            return Response({"error: No se encontró un carrito activo"})
        
        productos_en_carrito = cart.items.values_list('producto_id', flat=True)
        recomendaciones_ids = recomendar(list(productos_en_carrito))

        productos_recomendados = Producto.objects.filter(id__in=recomendaciones_ids)
        serializer = ProductoSerializer(productos_recomendados, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return ItemCart.objects.all()
        # Solo los ítems cuyo cart pertenece al usuario
        return ItemCart.objects.filter(cart__usuario=user)

    def perform_create(self, serializer):
        user = self.request.user
        cart, _ = Cart.objects.get_or_create(usuario=user, estado='activo')
        
        producto = serializer.validated_data['producto']
        detalle = getattr(producto, 'detalle', None)
        if not detalle:
            raise serializers.ValidationError("el producto no tiene detalle asignado")
        precio = detalle.precio_final
        serializer.save(cart=cart, precio_unitario=precio)
    
    def perform_update(self, serializer):
        producto = serializer.validated_data.get('producto')
        if producto:
            detalle = getattr(producto, 'detalle', None)
            if not detalle:
                raise serializers.ValidationError("El producto no tiene detalle asignado.")
            precio = detalle.precio_final
            serializer.save(precio_unitario=precio)
        else:
            serializer.save()



class MetodoPagoViewSet(viewsets.ModelViewSet):
    queryset = Metodo_Pago.objects.all()
    serializer_class = MetodoPagoSerializer


class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.all()
    serializer_class = PagoSerializer


class DetalleVentaViewSet(viewsets.ModelViewSet):
    queryset = Detalle_Venta.objects.all()
    serializer_class = DetalleVentaSerializer

class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer

    authentication_classes = [TokenAuthentication]
    permission_classes     = [IsAuthenticated] 

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Venta.objects.all()
        return Venta.objects.filter(usuario=user)

    def create(self, request, *args, **kwargs):
        usuario = request.user
        sucursal_id = request.data.get('sucursal_id')
        if not sucursal_id:
            return Response({'error': 'Debe indicar una sucursal para la venta.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            carrito = Cart.objects.get(usuario=usuario, estado='activo')
        except Cart.DoesNotExist:
            return Response({'error': 'No tienes un carrito activo'}, status=status.HTTP_404_NOT_FOUND)
        
        items = carrito.items.all()
        if not items.exists():
            return Response({'error':'El carrito está vacio'}, status=status.HTTP_400_BAD_REQUEST)
        
        for item in items:
            try:
                stock_sucursal = Stock_sucursal.objects.get(producto=item.producto, sucursal_id=sucursal_id)
            except ObjectDoesNotExist:
                return Response({'error': f'El producto {item.producto.nombre} no está disponible en la sucursal seleccionada.'}, status=status.HTTP_400_BAD_REQUEST)

            if item.cantidad > stock_sucursal.stock:
                return Response({'error': f"No hay suficiente stock para el producto {item.producto.nombre} en la sucursal seleccionada."}, status=status.HTTP_400_BAD_REQUEST)

        
        total = sum(item.precio_unitario * item.cantidad for item in items)

        pago = Pago.objects.create(
            metodo_id=request.data.get('metodo_pago_id'),
            monto=total,
            estado='pendiente',
            referencia=request.data.get('referencia','')
        )

        venta = Venta.objects.create(
            usuario=usuario,
            pago=pago,
            total=total,
            estado='pendiente'
        )

        for item in items:
            Detalle_Venta.objects.create(
                venta=venta,
                producto=item.producto,
                cantidad=item.cantidad,
                precio_unitario=item.precio_unitario
            )
            stock_sucursal = Stock_sucursal.objects.get(producto=item.producto, sucursal_id=sucursal_id)
            stock_sucursal.stock -= item.cantidad
            stock_sucursal.save()
        
        carrito.estado = 'confirmado'
        carrito.save()

        serializer = self.get_serializer(venta)
        return Response({'mensaje':'Venta registrada con éxito', 'venta': serializer.data}, status=status.HTTP_201_CREATED)

    def actualizar_estado_pago(pago, estado):
        if estado == 'completado':
            pago.estado = 'completado'
        elif estado == 'fallido':
            pago.estado = 'fallido'
        pago.save()
    
    def actualizar_estado_venta(venta, estado):
        if estado == 'completado':
            venta.estado = 'procesando'
        elif estado == 'enviado':
            venta.estado = 'enviado'
        elif estado == 'entregado':
            venta.estado = 'entregado'
        elif estado == 'cancelado':
            venta.estado = 'cancelado'
        venta.save()
