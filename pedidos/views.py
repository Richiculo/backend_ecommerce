from django.shortcuts import render
from rest_framework import viewsets, status
from .models import Cart, ItemCart, Metodo_Pago, Pago, Detalle_Venta, Venta
from rest_framework.permissions import IsAuthenticated
from productos.models import Stock_sucursal
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from .serializers import CartSerializer, ItemCartSerializer, MetodoPagoSerializer, PagoSerializer, DetalleVentaSerializer, VentaSerializer

#IMPORTS PARA REPORTES
from rest_framework.views import APIView
from django.http import FileResponse, HttpResponse
from reportlab.pdfgen import canvas
from io import BytesIO
from django.db.models import Q
from datetime import datetime, timezone
import pandas as pd
from rest_framework.response import Response

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

class GenerarReportePDF(APIView):
    def get(self, request):
        # 1. Obtener y validar parámetros
        fecha_inicio = request.query_params.get('fecha_inicio', '').strip('"')
        fecha_fin = request.query_params.get('fecha_fin', '').strip('"')
        monto_minimo = request.query_params.get('monto_minimo', 0)
        estado = request.query_params.get('estado', '').lower()
        
        # 2. Filtrar ventas
        ventas = Venta.objects.all()
        if fecha_inicio and fecha_fin:
            ventas = ventas.filter(fecha__date__range=[fecha_inicio, fecha_fin])
        if estado:
            ventas = ventas.filter(estado=estado)
        ventas = ventas.filter(total__gte=float(monto_minimo))
        
        # 3. Configuración del documento
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, 
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=72)
        
        styles = getSampleStyleSheet()
        
        # Modificar estilos existentes en lugar de añadir nuevos
        styles['Heading1'].fontSize = 16
        styles['Heading1'].leading = 20
        styles['Heading1'].alignment = 1  # Centrado
        styles['Heading1'].spaceAfter = 20
        styles['Heading1'].textColor = colors.HexColor('#2c3e50')
        
        styles['BodyText'].spaceBefore = 6
        styles['BodyText'].spaceAfter = 6
        styles['BodyText'].textColor = colors.HexColor('#34495e')
        
        # Contenido del PDF (resto del código permanece igual)
        elements = []
        
        # Encabezado
        elements.append(Paragraph("Reporte de Ventas", styles['Heading1']))
        elements.append(Paragraph(f"Total de ventas: {len(ventas)}", styles['Heading2']))
        
        # Filtros aplicados
        filtros_data = [
            ["Fecha inicio:", fecha_inicio or "Todos"],
            ["Fecha fin:", fecha_fin or "Todos"],
            ["Monto mínimo:", f"${float(monto_minimo):,.2f}"],
            ["Estado:", estado.capitalize() if estado else "Todos"]
        ]
        
        filtros_table = Table(filtros_data, colWidths=[1.5*inch, 3*inch])
        filtros_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
        ]))
        elements.append(filtros_table)
        elements.append(Paragraph(" ", styles['BodyText']))  # Espacio
        
        # Datos de ventas
        ventas_data = [["ID", "Fecha", "Cliente", "Total", "Estado"]]
        
        for venta in ventas:
            ventas_data.append([
                str(venta.id),
                venta.fecha.strftime('%Y-%m-%d'),
                venta.usuario.nombre,
                f"${float(venta.total):,.2f}",
                venta.estado.capitalize()
            ])
        
        ventas_table = Table(ventas_data, repeatRows=1)
        ventas_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#34495e')),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f9f9f9'), colors.white])
        ]))
        elements.append(ventas_table)
        
        
        
        # Generar PDF
        doc.build(elements)
        buffer.seek(0)
        
        return FileResponse(buffer, filename="reporte_ventas.pdf", content_type='application/pdf')



class GenerarReporteExcel(APIView):
    def get(self, request):
        # Obtener y limpiar parámetros (igual que en la vista PDF)
        fecha_inicio = request.query_params.get('fecha_inicio', '').strip('"')
        fecha_fin = request.query_params.get('fecha_fin', '').strip('"')
        estado = request.query_params.get('estado', '').lower()
        monto_minimo = float(request.query_params.get('monto_minimo', 0))

        # Filtrar ventas (usando la misma lógica que para PDF)
        ventas = Venta.objects.all()
        if fecha_inicio and fecha_fin:
            ventas = ventas.filter(fecha__date__range=[fecha_inicio, fecha_fin])
        if estado:
            ventas = ventas.filter(estado=estado)
        ventas = ventas.filter(total__gte=monto_minimo)

        # Convertir QuerySet a DataFrame de pandas
        data = []
        for venta in ventas:
            data.append({
                'ID': venta.id,
                'Fecha': venta.fecha.strftime('%Y-%m-%d'),
                'Cliente': venta.usuario.nombre,
                'Total': float(venta.total),
                'Estado': venta.estado,
                'Método Pago': venta.pago.metodo.nombre if venta.pago else ''
            })

        df = pd.DataFrame(data)

        # Crear archivo Excel en memoria
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Ventas', index=False)
        
        output.seek(0)

        # Preparar respuesta
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=reporte_ventas.xlsx'
        return response



class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer


class ItemCartViewSet(viewsets.ModelViewSet):
    queryset = ItemCart.objects.all()
    serializer_class = ItemCartSerializer

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

    def get_queryset(self):
        user = self.request.user
        """ if user.rol.nombre.lower() == 'cliente':
            return Venta.objets.filter(usuario=user) """
        return Venta.objects.all()

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
            referecia=request.data.get('referencia','')
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
