from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from sucursales import views

router = DefaultRouter()
router.register(r'sucursales', views.SucursalViewSet, basename='sucursales')
router.register(r'departamentos', views.DepartamentoViewSet, basename='departamentos')

urlpatterns = [
    path('', include(router.urls)),
]