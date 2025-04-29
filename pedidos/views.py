from django.shortcuts import render
from rest_framework import viewsets, status
from .models import Cart, ItemCart, Metodo_Pago, Pago, Detalle_Venta, Venta
from productos.models import Producto
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from productos.models import Stock_sucursal
from direcciones.models import Direccion
from envios.models import Envio
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import CartSerializer, ItemCartSerializer, MetodoPagoSerializer, PagoSerializer, DetalleVentaSerializer, VentaSerializer
from productos.serializers import ProductoSerializer
from rest_framework import serializers
from rest_framework.decorators import action
from pedidos.ml.recomendador_knn import recomendar
from django.utils import timezone
import stripe
from django.conf import settings


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
        usuario_id = user.id

        if usuario_id and user.is_staff:
            return Cart.objects.filter(usuario_id=usuario_id)

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
        
        productos_en_carrito = list(cart.items.values_list('producto_id', flat=True))
        recomendaciones_ids = recomendar(productos_en_carrito)

        productos_recomendados = Producto.objects.filter(id__in=recomendaciones_ids)
        serializer = ProductoSerializer(productos_recomendados, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        user = self.request.user
        cart_id = self.request.query_params.get('cart_id', None)
        if cart_id:
            return ItemCart.objects.filter(cart_id=cart_id)
        if user.is_staff:
            return ItemCart.objects.all()
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

    @action(detail=True, methods=['POST'])
    def confirmar_pago(self, request, pk=None):
        try:
            pago = self.get_object()
            if pago.estado != 'pendiente':
                return Response({"error": "Este pago ya fue procesado"}, status=status.HTTP_400_BAD_REQUEST)
            metodo_id = request.data.get('metodo_id')
            referencia = request.data.get('referencia', 'PagoSimulado')
            if metodo_id:
                metodo = Metodo_Pago.objects.get(id=metodo_id)
                pago.metodo = metodo
            pago.referencia = referencia
            pago.estado = 'completado'
            pago.save()

            venta = Venta.objects.get(pago=pago)
            venta.estado = 'procesando'
            venta.save()

            try:
                envio = Envio.objects.get(venta=venta)
                envio.estado = 'enviado'
                envio.fecha_envio = timezone.now()
                envio.observaciones = 'En camino'
                envio.save()
            except Envio.DoesNotExist:
                pass
            return Response({"mensaje": "Pago confirmado y procesando venta"}, status=status.HTTP_200_OK)
        except Exception as e:
            Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(detail=False, methods=['POST'], url_path='crear-intencion-pago')
    def create_payment_intent(self, request):
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY

            amount = request.data.get('amount')  # Monto en centavos
            currency = request.data.get('currency', 'bs')  # Default USD

            if not amount:
                return Response({'error': 'Debe proporcionar un monto.'}, status=status.HTTP_400_BAD_REQUEST)

            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                payment_method_types=["card"],
            )

            return Response({'client_secret': intent['client_secret']}, status=status.HTTP_200_OK) 
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class DetalleVentaViewSet(viewsets.ModelViewSet):
    queryset = Detalle_Venta.objects.all()
    serializer_class = DetalleVentaSerializer

    def get_queryset(self):
        venta_id = self.request.query_params.get('venta_id')
        qs = Detalle_Venta.objects.select_related('producto')  # <-- esto optimiza
        if venta_id is not None:
         qs = qs.filter(venta_id=venta_id)
        return qs



class VentaViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer

    authentication_classes = [TokenAuthentication]
    permission_classes     = [IsAuthenticated] 

    def get_queryset(self):
        user = self.request.user
        queryset = Venta.objects.all()
        if not user.is_staff:
            return queryset.filter(usuario=user)
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(usuario__id=user_id)

        return queryset
    
    @action(detail=False, methods=['get'], url_path='venta-pendiente')
    def get_venta_pendiente(self, request):
        user = request.user

        # Filtrar las ventas pendientes y ordenar por fecha descendente (la más reciente primero)
        venta_pendiente = Venta.objects.filter(usuario=user, estado='pendiente').order_by('-fecha').first()

        if venta_pendiente:
            # Si se encuentra una venta pendiente, serializamos la información
            serializer = self.get_serializer(venta_pendiente)
            return Response(serializer.data)
        else:
            return Response({"detail": "No hay ventas pendientes."}, status=status.HTTP_404_NOT_FOUND)
        
    def create(self, request, *args, **kwargs):
        usuario = request.user
        sucursal_id = request.data.get('sucursal_id')
        es_delivery = request.data.get('es_delivery', False)
        direccion_id = request.data.get('direccion_id')
        if not sucursal_id:
            return Response({'error': 'Debe indicar una sucursal para la venta.'}, status=status.HTTP_400_BAD_REQUEST)

        if es_delivery:
            if not direccion_id:
                return Response({'error': 'Debe proporcionar una dirección para el envio.'}, status=status.HTTP_400_BAD_REQUEST)
            try: 
                direccion = Direccion.objects.get(id=direccion_id, usuario=usuario)
            except Direccion.DoesNotExist:
                return Response({'error': 'La dirección proporcionada no existe o no pertenece al usuario'})

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

        if es_delivery:
            direccion = Direccion.objects.get(id=direccion_id, usuario=usuario)
            Envio.objects.create(
                venta=venta,
                cliente=usuario,
                direccion_entrega=direccion,
                estado='pendiente',
                observaciones='Pedido en preparación'
            )

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
