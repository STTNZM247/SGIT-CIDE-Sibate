import secrets
from datetime import timedelta

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(max_length=255, null=True, blank=True)
    fch_registro = models.DateTimeField(null=True, blank=True)
    fch_ult_act = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'rol'

    def __str__(self):
        return f'Rol {self.id_rol}'


class TipoDoc(models.Model):
    id_tipo_doc = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=60, unique=True)
    codigo = models.CharField(max_length=10, unique=True)
    fch_registro = models.DateTimeField(null=True, blank=True)
    fch_ult_act = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'tipo_doc'
        ordering = ['id_tipo_doc']

    def __str__(self):
        return self.codigo


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
    VERIFICACION_SENA_ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('solicitada', 'Solicitud enviada'),
        ('enlace_enviado', 'Enlace enviado'),
        ('documento_cargado', 'Documento cargado'),
        ('validado', 'Validado'),
        ('rechazada', 'Rechazada'),
    ]

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
    id_tipo_doc_fk = models.ForeignKey(
        TipoDoc,
        on_delete=models.SET_NULL,
        db_column='id_tipo_doc_fk',
        null=True,
        blank=True,
    )
    fot_usu = models.ImageField(upload_to='usuarios/', null=True, blank=True)
    banner_usu = models.ImageField(upload_to='usuarios/banners/', null=True, blank=True)
    telefono = models.CharField(max_length=30, null=True, blank=True)
    tema = models.CharField(
        max_length=10,
        choices=[('claro', 'Claro'), ('oscuro', 'Oscuro')],
        default='claro',
    )
    programa_formacion = models.CharField(max_length=255, null=True, blank=True)
    centro_desarrollo = models.CharField(max_length=255, null=True, blank=True)
    verificacion_sena_estado = models.CharField(
        max_length=25,
        choices=VERIFICACION_SENA_ESTADOS,
        default='pendiente',
    )
    verificacion_sena_imagen = models.ImageField(upload_to='usuarios/validacion_sena/', null=True, blank=True)
    verificacion_sena_documento = models.ImageField(upload_to='usuarios/validacion_manual/', null=True, blank=True)
    verificacion_sena_observacion = models.TextField(null=True, blank=True)
    verificacion_sena_solicitada_en = models.DateTimeField(null=True, blank=True)
    verificacion_sena_validada_en = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'correo'
    EMAIL_FIELD = 'correo'
    REQUIRED_FIELDS = ['nombre']

    class Meta:
        db_table = 'usuario'

    def __str__(self):
        return f'{self.nombre} {self.apellido}'

    @property
    def verificacion_sena_completa(self):
        return self.verificacion_sena_estado == 'validado'


class PasswordResetToken(models.Model):
    id_reset = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens',
    )
    token = models.CharField(max_length=128, unique=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    expira_en = models.DateTimeField()
    usado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'password_reset_token'
        ordering = ['-creado_en', '-id_reset']

    def __str__(self):
        return f'Reset token {self.usuario_id} ({self.token[:8]})'

    @property
    def esta_vigente(self):
        return self.usado_en is None and self.expira_en >= timezone.now()

    @classmethod
    def create_for_user(cls, usuario):
        ahora = timezone.now()
        cls.objects.filter(usuario=usuario, usado_en__isnull=True).update(usado_en=ahora)
        return cls.objects.create(
            usuario=usuario,
            token=secrets.token_urlsafe(32),
            expira_en=ahora + timedelta(minutes=30),
        )


class VerificacionSenaToken(models.Model):
    id_token = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='verificacion_sena_tokens',
    )
    token = models.CharField(max_length=128, unique=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    expira_en = models.DateTimeField()
    usado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'verificacion_sena_token'
        ordering = ['-creado_en', '-id_token']

    def __str__(self):
        return f'Verificación SENA {self.usuario_id} ({self.token[:8]})'

    @property
    def esta_vigente(self):
        return self.usado_en is None and self.expira_en >= timezone.now()

    @classmethod
    def create_for_user(cls, usuario):
        ahora = timezone.now()
        cls.objects.filter(usuario=usuario, usado_en__isnull=True).update(usado_en=ahora)
        return cls.objects.create(
            usuario=usuario,
            token=secrets.token_urlsafe(32),
            expira_en=ahora + timedelta(hours=48),
        )


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


class AuditoriaLog(models.Model):
    id_log = models.AutoField(primary_key=True)
    accion = models.CharField(max_length=30)
    entidad = models.CharField(max_length=80)
    entidad_id = models.CharField(max_length=80, null=True, blank=True)
    descripcion = models.TextField()
    id_usuario_fk = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        db_column='id_usuario_fk',
        null=True,
        blank=True,
        related_name='auditorias',
    )
    rol_usuario = models.CharField(max_length=80, null=True, blank=True)
    ip_origen = models.CharField(max_length=45, null=True, blank=True)
    fch_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'auditoria_log'
        ordering = ['-fch_registro', '-id_log']

    def __str__(self):
        return f'{self.accion} {self.entidad} ({self.entidad_id or "-"})'


class Pedido(models.Model):
    id_pedido = models.AutoField(primary_key=True)
    id_usuario_fk = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column='id_usuario_fk',
        related_name='pedidos',
    )
    estado = models.CharField(max_length=50, default='pendiente')
    total_productos = models.PositiveIntegerField(default=0)
    total_unidades = models.PositiveIntegerField(default=0)
    codigo_entrega = models.CharField(max_length=6, null=True, blank=True)
    codigo_expira_en = models.DateTimeField(null=True, blank=True)
    area_ubicacion = models.TextField(null=True, blank=True)
    foto_carnet = models.ImageField(upload_to='pedidos/carnets/', null=True, blank=True)
    tipo_devolucion = models.CharField(max_length=10, default='global', null=True, blank=True)
    fecha_devolucion = models.DateTimeField(null=True, blank=True)
    fch_registro = models.DateTimeField(null=True, blank=True)
    fch_ult_act = models.DateTimeField(null=True, blank=True)
    notif_vencimiento_enviada = models.BooleanField(default=False)
    extensiones_plazo = models.PositiveSmallIntegerField(default=0)  # máximo 3

    class Meta:
        db_table = 'pedido'
        ordering = ['-fch_registro', '-id_pedido']

    def __str__(self):
        return f'Pedido {self.id_pedido} - {self.id_usuario_fk}'


class DetallePedido(models.Model):
    id_det_pedido = models.AutoField(primary_key=True)
    id_pedido_fk = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        db_column='id_pedido_fk',
        related_name='detalles',
    )
    id_prod_fk = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,
        db_column='id_prod_fk',
        null=True,
        blank=True,
    )
    nombre_producto = models.CharField(max_length=255)
    nombre_catalogo = models.CharField(max_length=255, null=True, blank=True)
    cantidad_solicitada = models.PositiveIntegerField(default=1)
    stock_referencia = models.IntegerField(null=True, blank=True)
    estado_detalle = models.CharField(max_length=50, default='pendiente')
    fecha_devolucion = models.DateTimeField(null=True, blank=True)
    fch_registro = models.DateTimeField(null=True, blank=True)
    fch_ult_act = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'detalle_pedido'
        ordering = ['id_det_pedido']

    def __str__(self):
        return f'{self.nombre_producto} x {self.cantidad_solicitada}'


class PedidoEvidencia(models.Model):
    id_evidencia = models.AutoField(primary_key=True)
    id_pedido_fk = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        db_column='id_pedido_fk',
        related_name='evidencias',
    )
    foto_evidencia = models.ImageField(upload_to='pedidos/evidencias/')
    fch_registro = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'pedido_evidencia'
        ordering = ['id_evidencia']

    def __str__(self):
        return f'Evidencia {self.id_evidencia} pedido {self.id_pedido_fk_id}'


class CarritoItem(models.Model):
    id_carrito_item = models.AutoField(primary_key=True)
    id_usuario_fk = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column='id_usuario_fk',
        related_name='carrito_items',
    )
    id_prod_fk = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        db_column='id_prod_fk',
        related_name='carrito_items',
    )
    cantidad = models.PositiveIntegerField(default=1)
    fch_registro = models.DateTimeField(null=True, blank=True)
    fch_ult_act = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'carrito_item'
        constraints = [
            models.UniqueConstraint(fields=['id_usuario_fk', 'id_prod_fk'], name='uq_carrito_usuario_producto'),
        ]

    def __str__(self):
        return f'Carrito {self.id_usuario_fk_id} - Prod {self.id_prod_fk_id} x {self.cantidad}'


class Notificacion(models.Model):
    TIPOS = [
        ('pedido_creado', 'Pedido creado'),
        ('esperando_entrega', 'Esperando entrega'),
        ('entregado', 'Entregado'),
        ('rechazado', 'Rechazado'),
        ('no_disponible', 'Producto no disponible'),
        ('aviso_devolucion', 'Aviso de devolución'),
        ('prestamo_vencido', 'Préstamo vencido'),
        ('solicitud_validacion_sena', 'Solicitud de validación SENA'),
        ('enlace_validacion_sena', 'Enlace de validación SENA'),
        ('documento_validacion_sena', 'Documento cargado para validación SENA'),
        ('verificacion_sena_aprobada', 'Verificación SENA aprobada'),
        ('verificacion_sena_rechazada', 'Verificación SENA rechazada'),
        # Staff (admin / almacenista)
        ('staff_nuevo_pedido', 'Nuevo pedido recibido'),
        ('staff_pedido_cancelado', 'Pedido cancelado por usuario'),
        ('staff_pedido_entregado', 'Pedido entregado'),
        ('staff_solicitud_validacion_sena', 'Solicitud manual de validación SENA'),
        ('staff_documento_validacion_sena', 'Documento recibido para validación SENA'),
    ]

    id_noti = models.AutoField(primary_key=True)
    id_usuario_fk = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column='id_usuario_fk',
        related_name='notificaciones',
    )
    tipo = models.CharField(max_length=40, choices=TIPOS)
    titulo = models.CharField(max_length=120)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    id_pedido_ref = models.PositiveIntegerField(null=True, blank=True)
    fch_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notificacion'
        ordering = ['-fch_registro']

    def __str__(self):
        return f'Notif {self.id_noti} → usuario {self.id_usuario_fk_id}'
