from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('sucursales', views.SucursalViewSet)

urlpatterns = [
    path('', include(router.urls)),
]