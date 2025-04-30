from django.urls import path, include
from rest_framework.routers import DefaultRouter
from productos import views

router = DefaultRouter()
router.register(r'productos',views.ProductoViewSet)
router.register(r'proveedores',views.ProveedorViewSet)
router.register(r'categorias',views.CategoriaViewSet)
router.register(r'detalles',views.DetalleProductoViewSet)
router.register(r'stocks',views.StockSucursalViewSet)
router.register(r'imagenes-productos',views.ImagenProductoViewSet, basename = 'imagenes-productos')
router.register(r'descuentos', views.DescuentoViewSet, basename='descuentos')

urlpatterns = [
    path('reporte-stock-pdf/', views.GenerarStockPDF.as_view(), name='reporte-stock-pdf'),
    path('reporte-stock-excel/', views.GenerarStockExcel.as_view(), name='reporte-stock-excel'),
    path('', include(router.urls))
]