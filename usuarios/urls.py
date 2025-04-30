from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('usuarios', views.UsuarioViewSet)


urlpatterns = [
    re_path('login', views.login),
    re_path('register', views.register),
    re_path('perfil', views.perfil),
    # path('actualizar', views.actualizar_usuario),
    path('', include(router.urls) ),   
]