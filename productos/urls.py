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

urlpatterns = [
    path('', include(router.urls))
]