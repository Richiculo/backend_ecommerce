from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from django.utils import timezone
from django.db import models


# Modelo: Rol

class Rol(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

# Modelo: Permiso

class Permiso(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre


# Modelo: PermisoRol

class PermisoRol(models.Model):
    permiso = models.ForeignKey(Permiso, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('permiso', 'rol')

    def __str__(self):
        return f"{self.permiso.nombre} - {self.rol.nombre}"


# modelo: Usuario

class UsuarioManager(BaseUserManager):
    def create_user(self, nombre, apellidos, correo, password=None):
        if not nombre:
            raise ValueError("El usuario debe tener un nombre")
        if not correo:
            raise ValueError("El usuario debe tener un correo")
        if not apellidos:
            raise ValueError("El usuario debe tener apellidos registrados")
        user = self.model(
            nombre=nombre,
            apellidos=apellidos,
            correo=self.normalize_email(correo),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, nombre, apellidos, correo, password):
        user = self.create_user(nombre, apellidos, correo, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
    
    def get_by_natural_key(self, correo):
        return self.get(correo=correo)


class Usuario(AbstractBaseUser, PermissionsMixin):
    nombre = models.CharField(max_length=50)
    correo = models.EmailField(unique=True)
    apellidos = models.CharField(null=True, blank=True, max_length=100)
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['nombre','apellidos']

    def __str__(self):
        return self.correo
    

# Modelo: ActivityLogUsuario

class ActivitylogUsuario(models.Model):
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    accion = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.id_usuario.correo} - {self.accion} - {self.timestamp}"
    
