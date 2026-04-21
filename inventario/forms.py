from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

from .models import Catalogo, Producto, Rol, TipoDoc, Usuario


class CorreoAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label='Correo',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Correo institucional',
            'autocomplete': 'username',
            'spellcheck': 'false',
        }),
    )
    password = forms.CharField(
        label='Contraseña',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Contraseña',
            'autocomplete': 'current-password',
        }),
    )

    error_messages = {
        'invalid_login': 'Correo o contraseña incorrectos.',
        'inactive': 'Usuario inactivo. Por favor comunícate con un administrador.',
    }

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=request, *args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'login-control'})
        self.fields['password'].widget.attrs.update({'class': 'login-control', 'id': 'id_password'})

    def clean(self):
        username = (self.data.get('username') or '').strip()
        password = self.data.get('password') or ''

        if username and password:
            usuario = get_user_model().objects.filter(correo__iexact=username).first()
            if usuario and usuario.check_password(password) and not usuario.is_active:
                raise forms.ValidationError(self.error_messages['inactive'], code='inactive')

        return super().clean()


class RegistroPublicoForm(forms.ModelForm):
    id_tipo_doc_fk = forms.ModelChoiceField(
        label='Tipo de documento',
        queryset=TipoDoc.objects.none(),
        empty_label='Selecciona una opción',
        widget=forms.Select(attrs={
            'class': 'login-control login-control--select',
            'id': 'id_tipo_doc_fk',
        }),
    )
    password1 = forms.CharField(
        label='Contraseña',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'login-control',
            'placeholder': 'Crea una contraseña segura',
            'autocomplete': 'new-password',
        }),
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'login-control',
            'placeholder': 'Confirma la contraseña',
            'autocomplete': 'new-password',
        }),
    )

    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'id_tipo_doc_fk', 'cc', 'correo']
        widgets = {
            'cc': forms.TextInput(attrs={
                'class': 'login-control',
                'placeholder': 'Número de documento',
                'id': 'id_cc',
                'disabled': 'disabled',
                'inputmode': 'numeric',
            }),
            'nombre': forms.TextInput(attrs={'class': 'login-control', 'placeholder': 'Nombre(s)', 'id': 'id_nombre'}),
            'apellido': forms.TextInput(attrs={'class': 'login-control', 'placeholder': 'Apellido(s)', 'id': 'id_apellido'}),
            'correo': forms.EmailInput(attrs={'class': 'login-control', 'placeholder': 'Correo institucional', 'id': 'id_correo'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_tipo_doc_fk'].queryset = TipoDoc.objects.order_by('id_tipo_doc')
        for field_name in ['nombre', 'apellido', 'id_tipo_doc_fk', 'cc', 'correo', 'password1', 'password2']:
            self.fields[field_name].required = True

    def clean_correo(self):
        correo = (self.cleaned_data.get('correo') or '').strip().lower()
        if Usuario.objects.filter(correo__iexact=correo).exists():
            raise forms.ValidationError('Ya existe una cuenta con este correo.')
        return correo

    def clean_cc(self):
        cc = (self.cleaned_data.get('cc') or '').strip()
        if not cc:
            raise forms.ValidationError('Debes ingresar el número de documento.')
        if cc and Usuario.objects.filter(cc=cc).exists():
            raise forms.ValidationError('Ya existe una cuenta con este documento.')
        return cc

    def clean(self):
        cleaned_data = super().clean()
        tipo_doc = cleaned_data.get('id_tipo_doc_fk')
        cc = (cleaned_data.get('cc') or '').strip()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if not tipo_doc:
            self.add_error('id_tipo_doc_fk', 'Selecciona el tipo de documento.')
        if tipo_doc and not cc:
            self.add_error('cc', 'Ingresa el número de documento para continuar.')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned_data

    def save(self, commit=True):
        usuario = super().save(commit=False)
        rol_usuario, _ = Rol.objects.get_or_create(nombre_rol='usuario')
        usuario.id_rol_fk = rol_usuario
        usuario.is_active = True
        usuario.is_staff = False
        usuario.set_password(self.cleaned_data['password1'])
        if commit:
            usuario.save()
        return usuario


class RecuperarAccesoForm(forms.Form):
    correo = forms.EmailField(
        required=True,
        label='Correo',
        widget=forms.EmailInput(attrs={
            'class': 'login-control',
            'placeholder': 'Correo institucional registrado',
            'autocomplete': 'email',
        }),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = None

    def clean_correo(self):
        correo = (self.cleaned_data.get('correo') or '').strip().lower()
        self.usuario = Usuario.objects.filter(correo__iexact=correo, is_active=True).first()
        if not self.usuario:
            raise forms.ValidationError('No encontramos una cuenta activa con ese correo.')
        return correo


class RestablecerPasswordForm(forms.Form):
    password1 = forms.CharField(
        label='Nueva contraseña',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'login-control',
            'placeholder': 'Nueva contraseña',
            'autocomplete': 'new-password',
        }),
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'login-control',
            'placeholder': 'Confirma la contraseña',
            'autocomplete': 'new-password',
        }),
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned_data

    def save(self, usuario):
        usuario.set_password(self.cleaned_data['password1'])
        usuario.is_active = True
        usuario.save(update_fields=['password', 'is_active'])
        return usuario


class CatalogoForm(forms.ModelForm):
    def clean_nombre_catalogo(self):
        nombre = (self.cleaned_data.get('nombre_catalogo') or '').strip()
        return nombre.upper()

    class Meta:
        model = Catalogo
        fields = ['nombre_catalogo', 'descripcion']
        labels = {
            'nombre_catalogo': 'Nombre del catálogo',
            'descripcion': 'Descripción',
        }
        widgets = {
            'nombre_catalogo': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej: Equipos audiovisuales',
                'autocomplete': 'off',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-input form-textarea',
                'placeholder': 'Descripción breve del catálogo…',
                'rows': 3,
            }),
        }


class ProductoForm(forms.ModelForm):
    def clean_nombre_producto(self):
        nombre = (self.cleaned_data.get('nombre_producto') or '').strip()
        return nombre.upper()

    stock_inicial = forms.IntegerField(
        min_value=0,
        label='Stock inicial',
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': '0',
            'min': '0',
        }),
    )
    descr_dispo = forms.CharField(
        required=False,
        label='Descripción de disponibilidad',
        widget=forms.Textarea(attrs={
            'class': 'form-input form-textarea',
            'placeholder': 'Observaciones de disponibilidad…',
            'rows': 2,
        }),
    )

    class Meta:
        model = Producto
        fields = ['nombre_producto', 'descripcion', 'id_cat_fk', 'fot_prod']
        labels = {
            'nombre_producto': 'Nombre del producto',
            'descripcion': 'Descripción',
            'id_cat_fk': 'Catálogo',
            'fot_prod': 'Foto del producto',
        }
        widgets = {
            'nombre_producto': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Nombre del producto',
                'autocomplete': 'off',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-input form-textarea',
                'placeholder': 'Descripción breve del producto…',
                'rows': 3,
            }),
            'id_cat_fk': forms.Select(attrs={
                'class': 'form-input form-select',
            }),
            'fot_prod': forms.ClearableFileInput(attrs={
                'class': 'form-file',
                'accept': 'image/*',
            }),
        }


class UsuarioPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'cc', 'nombre', 'apellido', 'correo', 'telefono',
            'programa_formacion', 'centro_desarrollo', 'fot_usu', 'banner_usu'
        ]
        widgets = {
            'cc': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_cc', 'placeholder': 'Número de documento'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_nombre', 'placeholder': 'Nombre'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_apellido', 'placeholder': 'Apellido'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'id': 'id_correo', 'placeholder': 'Correo institucional'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_telefono', 'placeholder': '+57 300 000 0000'}),
            'programa_formacion': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_programa_formacion', 'placeholder': 'Ej: ADSO / Análisis y desarrollo de software'}),
            'centro_desarrollo': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_centro_desarrollo', 'placeholder': 'Ej: Centro de formación de ...'}),
            'fot_usu': forms.ClearableFileInput(attrs={'class': 'form-file', 'accept': 'image/*', 'id': 'id_fot_usu'}),
            'banner_usu': forms.ClearableFileInput(attrs={'class': 'form-file', 'accept': 'image/*', 'id': 'id_banner_usu'}),
        }
        labels = {
            'cc': 'Cédula',
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'correo': 'Correo',
            'telefono': 'Teléfono',
            'programa_formacion': 'Programa de formación',
            'centro_desarrollo': 'Centro de desarrollo',
            'fot_usu': 'Foto de perfil',
            'banner_usu': 'Foto de portada',
        }
