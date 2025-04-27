from django.forms import ValidationError
from django.shortcuts import render
from rest_framework import viewsets
from .models import Producto, Proveedor, Detalle_Producto, Categoria, Stock_sucursal, Imagen_Producto
from .serializers import ProductoSerializer, ProveedorSerializer, DetalleProductoSerializer, CategoriaSerializer, StockSucursalSerializer, ImagenProductoSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

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

""" class GenerarReportePDF(APIView):
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
 """


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    # ENDPOINT PARA FILTRAR POR PRODUCTO
    def get_queryset(self):
        categoria_id = self.request.query_params.get('categoria_id')
        
        if categoria_id:
            try:
                return Producto.objects.filter(
                    categoria_producto__categoria_id=int(categoria_id)
                )
            except ValueError:
                raise ValidationError("ID de categoría debe ser numérico")
        
        return super().get_queryset()


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
