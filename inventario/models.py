from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    fch_registro = models.DateTimeField(null=True, blank=True)
    fch_ult_act = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'rol'

    def __str__(self):
        return f'Rol {self.id_rol}'


class UsuarioManager(BaseUserManager):
    def create_user(self, correo, password=None, **extra_fields):
        if not correo:
            raise ValueError('El correo es obligatorio')
        correo = self.normalize_email(correo)
        user = self.model(correo=correo, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, correo, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(correo, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    id_usu = models.AutoField(primary_key=True)
    cc = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nombre = models.CharField(max_length=255, null=True, blank=True)
    apellido = models.CharField(max_length=255, null=True, blank=True)
    correo = models.CharField(max_length=255, unique=True)
    # 'password' de AbstractBaseUser se guarda en columna 'contrasena'
    password = models.CharField(max_length=255, db_column='contrasena')
    id_rol_fk = models.ForeignKey(
        Rol,
        on_delete=models.SET_NULL,
        db_column='id_rol_fk',
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['nombre']

    class Meta:
        db_table = 'usuario'

    def __str__(self):
        return f'{self.nombre} {self.apellido}'


class Catalogo(models.Model):
    id_cat = models.AutoField(primary_key=True)
    nombre_catalogo = models.CharField(max_length=255, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    fch_registro = models.DateTimeField(null=True, blank=True)
    fch_ult_act = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'catalogo'

    def __str__(self):
        return self.nombre_catalogo or f'Catalogo {self.id_cat}'


class UsuCat(models.Model):
    id_usu_cat = models.AutoField(primary_key=True)
    id_usuario_fk = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column='id_usuario_fk',
    )
    id_cat_fk = models.ForeignKey(
        Catalogo,
        on_delete=models.CASCADE,
        db_column='id_cat_fk',
    )
    fch_registro = models.DateTimeField(null=True, blank=True)
    fch_ult_act = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'usu_cat'

    def __str__(self):
        return f'{self.id_usuario_fk} - {self.id_cat_fk}'


class Producto(models.Model):
    id_prod = models.AutoField(primary_key=True)
    nombre_producto = models.CharField(max_length=255, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    fot_prod = models.ImageField(upload_to='productos/', null=True, blank=True)
    id_cat_fk = models.ForeignKey(
        Catalogo,
        on_delete=models.CASCADE,
        db_column='id_cat_fk',
    )
    fch_registro = models.DateTimeField(null=True, blank=True)
    fch_ult_act = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'producto'

    def __str__(self):
        return self.nombre_producto or f'Producto {self.id_prod}'


class Disponibilidad(models.Model):
    id_disp = models.AutoField(primary_key=True)
    id_prod_fk = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        db_column='id_prod_fk',
    )
    cantidad = models.IntegerField(null=True, blank=True)
    stock = models.IntegerField(null=True, blank=True)
    descr_dispo = models.TextField(null=True, blank=True)
    fch_registro = models.DateTimeField(null=True, blank=True)
    fch_ult_act = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'disponibilidad'

    def __str__(self):
        return f'Disp. {self.id_prod_fk} stock={self.stock}'


class Auditorio(models.Model):
    id_aud = models.AutoField(primary_key=True)
    nombre_auditorio = models.CharField(max_length=255, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    fch_registro = models.DateTimeField(null=True, blank=True)
    fch_ult_act = models.DateTimeField(null=True, blank=True)
    id_usu_cat_fk = models.ForeignKey(
        UsuCat,
        on_delete=models.CASCADE,
        db_column='id_usu_cat_fk',
    )

    class Meta:
        db_table = 'auditorio'

    def __str__(self):
        return self.nombre_auditorio or f'Auditorio {self.id_aud}'
