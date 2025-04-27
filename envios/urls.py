from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('agencias', views.AgenciaDeliveryViewSet)
router.register('envios', views.EnvioViewSet)

urlpatterns = [
    path('', include(router.urls)),
]