from django.urls import path, include
from rest_framework.routers import DefaultRouter
from direcciones import views

router = DefaultRouter()
router.register(r'direcciones', views.DireccionViewSet, basename='direccion')

urlpatterns = [
    path('', include(router.urls)),
]