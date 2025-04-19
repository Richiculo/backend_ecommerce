from django.urls import path, include
from rest_framework.routers import DefaultRouter
from pedidos import views

router = DefaultRouter()
router.register(r'carts', views.CartViewSet, basename='cart')
router.register(r'itemcarts', views.ItemCartViewSet, basename='itemcart')
router.register(r'metodos-pago', views.MetodoPagoViewSet, basename='metodopago')
router.register(r'pago', views.PagoViewSet, basename='pago')
router.register(r'detalle-venta', views.DetalleVentaViewSet, basename='detalleventa')
router.register(r'venta', views.VentaViewSet, basename='venta')


urlpatterns = [
    path('', include(router.urls)),
]

