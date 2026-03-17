from django import forms

from .models import Catalogo, Producto, Usuario


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
                'placeholder': 'Ej: Proyector Epson',
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
        fields = ['cc', 'nombre', 'apellido', 'correo', 'fot_usu']
        widgets = {
            'cc': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'fot_usu': forms.ClearableFileInput(attrs={'class': 'form-file', 'accept': 'image/*'}),
        }
        labels = {
            'cc': 'Cédula',
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'correo': 'Correo',
            'fot_usu': 'Foto de perfil',
        }
