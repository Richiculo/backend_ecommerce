from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

# Create your models here.
class UsuarioManager(BaseUserManager):
    def create_user(self, username, correo, password=None):
        if not username:
            raise ValueError("El usuario debe tener un nombre")
        if not correo:
            raise ValueError("El usuario debe tener un correo")

        user = self.model(
            username=username,
            correo=self.normalize_email(correo),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, correo, password):
        user = self.create_user(username,correo,password)
        #user.is_staff = True
        #user.is_superuser = True
        user.save(using=self._db)
        return user
    
    def get_by_natural_key(self, username):
        return self.get(username=username)


class Usuario(AbstractBaseUser):
    username = models.CharField(max_length=50, unique=True)
    correo = models.EmailField(unique=True)
    



    #objects = UsuarioManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['correo']

    def _str__(self):
        return self.username
    
