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

