# SGIT-CIDE-Sibate
Pagina web y app movil para gestionar los prestamos de inventario de las herramientas y insumos 

## Pipeline CSS (build/minificado)

Se agregó un pipeline para compilar y minificar los CSS usados por los templates.

### 1) Generar build CSS

```bash
python manage.py build_css_assets
```

Esto crea archivos en `inventario/static/inventario/css-build/` y genera el manifiesto:

- `inventario/static/inventario/css-build/manifest.json`

### 2) Activar CSS compilado en runtime

Configura la variable de entorno:

```bash
USE_BUILT_CSS=true
```

Con eso, los templates usarán automáticamente los `.min.css` del manifiesto.

### 3) Flujo recomendado

1. Editar CSS modular en `inventario/static/inventario/css/...`
2. Ejecutar `python manage.py build_css_assets`
3. Desplegar con `USE_BUILT_CSS=true`

## Tailwind CSS (uso gradual)

Se integró Tailwind para usar utilidades sin romper los estilos actuales.

- Prefijo de clases: `tw-` (ejemplo: `tw-flex tw-gap-2`)
- Preflight desactivado para evitar choques con CSS existente.
- Archivo de entrada: `inventario/static/inventario/tailwind/input.css`
- Archivo compilado: `inventario/static/inventario/css-build/tailwind.css`

### Instalar dependencias

```bash
npm install
```

### Compilar Tailwind una vez

```bash
npm run tw:build
```

### Modo watch (desarrollo)

```bash
npm run tw:watch
```

## Correo transaccional con Resend (Django)

El proyecto soporta proveedores SMTP por variable de entorno (`EMAIL_PROVIDER`).
Por defecto queda `resend`.

Variables recomendadas:

```bash
EMAIL_PROVIDER=resend
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.resend.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=resend
EMAIL_HOST_PASSWORD=re_xxxxxxxxxxxxxxxxx
DEFAULT_FROM_EMAIL=Inventario SENA <notificaciones@tu-dominio.com>
```

Notas:

- `EMAIL_HOST_PASSWORD` debe ser tu API Key SMTP de Resend.
- Configura SPF/DKIM/DMARC en tu dominio para mejor entregabilidad.
- En local puedes usar un `DEFAULT_FROM_EMAIL` temporal (por ejemplo `onboarding@resend.dev`) mientras verificas dominio.

