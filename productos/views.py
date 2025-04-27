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


class GenerarStockPDF(APIView):
    def get(self, request):
        # Obtener todos los registros de stock
        stocks = Stock_sucursal.objects.all().select_related('producto', 'sucursal', 'sucursal__direccion')
        
        # Configuración del documento PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, 
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=72)
        
        styles = getSampleStyleSheet()
        
        # Modificar estilos existentes
        styles['Heading1'].fontSize = 16
        styles['Heading1'].leading = 20
        styles['Heading1'].alignment = 1  # Centrado
        styles['Heading1'].spaceAfter = 20
        styles['Heading1'].textColor = colors.HexColor('#2c3e50')
        
        styles['BodyText'].spaceBefore = 6
        styles['BodyText'].spaceAfter = 6
        styles['BodyText'].textColor = colors.HexColor('#34495e')
        
        # Contenido del PDF
        elements = []
        
        # Encabezado
        elements.append(Paragraph("Reporte de Stock por Sucursal", styles['Heading1']))
        elements.append(Paragraph(f"Total de registros: {stocks.count()}", styles['Heading2']))
        
        # Datos de stock
        stock_data = [["ID", "Producto", "Sucursal", "Departamento", "Stock"]]
        
        for stock in stocks:
            departamento = stock.sucursal.direccion.departamento.nombre if stock.sucursal.direccion and stock.sucursal.direccion.departamento else "N/A"
            stock_data.append([
                str(stock.id),
                stock.producto.nombre,
                stock.sucursal.nombre,
                departamento,
                str(stock.stock)
            ])
        
        stock_table = Table(stock_data, repeatRows=1)
        stock_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
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
        elements.append(stock_table)
        
        
        # Generar PDF
        doc.build(elements)
        buffer.seek(0)
        
        return FileResponse(buffer, filename="reporte_stock_sucursal.pdf", content_type='application/pdf')

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
