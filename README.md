# SGIT-CIDE-Sibaté

> **Sistema de Gestión de Inventario y Préstamos de Herramientas e Insumos**  
> Centro Industrial y de Desarrollo Empresarial (CIDE) — SENA Sede La Colonia / Sibaté.

---

## 📌 Tabla de Contenidos

1. [Descripción General](#-descripción-general)
2. [Características y Módulos Principales](#-características-y-módulos-principales)
3. [Roles del Sistema y Flujos de Trabajo](#-roles-del-sistema-y-flujos-de-trabajo)
4. [Stack Tecnológico](#-stack-tecnológico)
5. [Estructura del Proyecto](#-estructura-del-proyecto)
6. [Requisitos Previos](#-requisitos-previos)
7. [Instalación y Puesta en Marcha](#-instalación-y-puesta-en-marcha)
8. [Variables de Entorno](#-variables-de-entorno)
9. [Comandos de Gestión Personalizados](#-comandos-de-gestión-personalizados)
10. [Pipeline de CSS y Tailwind](#-pipeline-de-css-y-tailwind)
11. [Pruebas Automatizadas](#-pruebas-automatizadas)
12. [Licencia y Créditos](#-licencia-y-créditos)

---

## 📖 Descripción General

**SGIT-CIDE-Sibaté** es una plataforma web y adaptada a dispositivos móviles desarrollada en Django para automatizar el control de almacén, existencias, préstamos y devoluciones de herramientas, maquinaria, equipos e insumos del SENA.

El sistema resuelve la problemática del seguimiento manual de inventario en talleres y centros de formación mediante:
* Verificación biométrica/institucional de aprendices con lectura OCR de carnet SENA.
* Despacho y entrega segura de pedidos mediante códigos OTP de un solo uso (PIN de 6 dígitos).
* Código dinámico de devolución rápida con temporizador de 60 segundos.
* Diferenciación de bienes devolutivos frente a insumos de consumo no retornables.
* Trazabilidad total de auditoría y reportes gerenciales en PDF y Excel.

---

## 🚀 Características y Módulos Principales

### 1. Catálogo Jerárquico y Clasificación Multicriterio
* **Taxonomía en Árbol:** Organización por Macrocatálogos, Categorías y Subcategorías jerárquicas recursivas (con prevención de ciclos infinitos y validación de hasta 30 niveles de profundidad).
* **Generación Automática de Códigos:** Nomenclatura normalizada para herramientas y productos basada en clasificación institucional (`MACRO-CAT-SUBCAT-CONSECUTIVO`).
* **Wizard Paso a Paso:** Interfaz asistida para la creación y estructuración de nuevas líneas de catálogo y ubicaciones físicas de almacenamiento.

### 2. Gestión de Inventario y Stock
* **Tipos de Bienes:**
  * **Devolutivos:** Herramientas y equipos que requieren retorno físico al almacén.
  * **Consumo:** Insumos y materiales gastables (cables, tornillos, soldadura, etc.) que se descuentan permanentemente del stock sin exigir devolución.
* **Control de Existencias:** Gestión en tiempo real de cantidad total, stock disponible y alertas de nivel crítico.
* **Optimización Multimedia:** Conversión y compresión automática de imágenes a formato **WebP** mediante Pillow (remuestreo Lanczos) para minimizar consumo de ancho de banda y almacenamiento.
* **Galería Fotográfica:** Soporte para múltiples fotografías por producto con orden configurable.

### 3. Solicitud y Préstamo de Herramientas (Flujo de Aprendices)
* **Carrito Persistente:** Los ítems del carrito se almacenan en base de datos vinculados al usuario, permitiendo continuar pedidos desde diferentes dispositivos.
* **Despacho Seguro (Doble Factor con PIN de 6 Dígitos):** El pedido aprobado genera un código de entrega de 6 dígitos que el usuario presenta al almacenista para autorizar la salida de bodega.
* **Devolución Rápida:** Generación de un código efímero de devolución con ventana de validez de 60 segundos para agilizar la entrega en ventanilla.
* **Prórrogas:** Posibilidad de extender el plazo de devolución (hasta un máximo de 3 extensiones de 3 días cada una).
* **Evidencias de Entrega:** Registro fotográfico de soporte al momento de despachar o recibir herramientas.

### 4. Validación Institucional de Carnet SENA (Visión y OCR)
* **Captura en Vivo / Subida:** Permite fotografiar el carnet institucional usando la cámara del teléfono/computador o cargar una imagen existente.
* **Procesamiento de Imagen:** Auto-recorte inteligente sobre fondos oscuros y análisis cromático del verde institucional SENA.
* **OCR Tesseract:** Extracción de texto y cotejo automático de nombres, apellidos y número de documento (C.C. / T.I.) contra la cuenta del aprendiz.
* **Flujo Manual de Contingencia:** En caso de fallar el OCR, el aprendiz solicita revisión manual y el administrador puede despachar un enlace seguro con token de vigencia (4 horas) para carga de soporte documental.

### 5. Auditoría y Trazabilidad Completa
* Registro en bitácora (`AuditoriaLog`) de cada acción sensible: creación, modificación, eliminación de registros, aprobaciones y despachos.
* Captura automática de usuario responsable, rol, marca temporal y dirección IP de origen.

### 6. Reportes e Importación Masiva
* **Importación Masiva Excel:** Carga de productos mediante plantillas Excel con procesamiento por lotes vía `openpyxl` y registro detallado de incidencias en log.
* **Exportación Excel:** Descarga de listados completos de inventario y estado de préstamos.
* **Reportes PDF Nativos:** Generación vectorial de informes de préstamos y productos con stock bajo renderizados directamente mediante Pillow (sin dependencias complejas de librerías nativas del sistema operativo).

### 7. Centro de Notificaciones
* Notificaciones en tiempo real para usuarios (estados de pedidos, vencimientos, avisos de devolución).
* Alertas para el personal de almacén (nuevos pedidos, cancelaciones, solicitudes de validación).
* Contadores automáticos de alertas no leídas inyectados en la barra de navegación.

---

## 👥 Roles del Sistema y Flujos de Trabajo

```
[Usuario / Aprendiz]               [Almacenista]                    [Administrador]
         │                               │                                 │
         ├─ Explora catálogo             ├─ Revisa pedidos pendientes      ├─ Gestiona usuarios y roles
         ├─ Agrega al carrito            ├─ Valida código PIN (6 dígitos)  ├─ Aprueba validación SENA
         ├─ Valida carnet SENA (OCR)     ├─ Registra entrega y evidencia   ├─ Revisa bitácora de auditoría
         ├─ Solicita préstamo            ├─ Recibe devoluciones            ├─ Genera reportes PDF / Excel
         └─ Monitorea estado / prórrogas └─ Controla stock y almacenes     └─ Configuración global
```

* **Administrador (`admin`):** Acceso total al panel administrativo, gestión de usuarios, auditorías, estadísticas del dashboard, catálogos y aprobación de validaciones manuales.
* **Almacenista (`almacenista`):** Despacho y recepción de herramientas, validación de códigos de entrega, control de existencias e importación masiva.
* **Aprendiz / Instructor (`usuario`):** Consulta de productos, administración de su carrito, validación de carnet SENA, seguimiento de préstamos y generación de códigos de devolución.

---

## 🛠 Stack Tecnológico

| Capa | Tecnologías |
| :--- | :--- |
| **Backend** | Python 3.12, Django 6.0.6, PyMySQL |
| **Base de Datos** | MySQL / MariaDB (soporte dual para XAMPP local y PythonAnywhere) |
| **Frontend** | Django Templates, HTML5 Semántico, Vanilla CSS modular, JavaScript Vanilla |
| **Utilidades CSS** | Tailwind CSS 3.4.13 (prefijo `tw-`, preflight desactivado), PostCSS, Autoprefixer |
| **Visión / OCR** | Tesseract OCR, Pillow (PIL) 12.2.0 |
| **Hojas de Cálculo** | openpyxl 3.1.5 |
| **Correo Transaccional** | Django Core Mail / Resend SMTP |
| **Seguridad** | Throttling por IP y cuenta en login, Tokens criptográficos para reset y validación |

---

## 📂 Estructura del Proyecto

```
SGIT-CIDE-Sibate/
├── config/                          # Configuración raíz de Django
│   ├── __init__.py                  # Parche de compatibilidad PyMySQL para Django 6
│   ├── settings.py                  # Configuraciones (BD, Auth, Caché, Correo, Assets)
│   ├── urls.py                      # Enrutamiento principal del proyecto
│   ├── wsgi.py                      # Punto de entrada WSGI para producción
│   └── asgi.py                      # Punto de entrada ASGI
├── inventario/                      # Aplicación principal del sistema
│   ├── models.py                    # Definición de las 20 entidades de base de datos
│   ├── forms.py                     # Formularios de validación, registro y wizards
│   ├── db_compat.py                 # Introspección y compatibilidad con esquemas heredados
│   ├── validacion_sena.py           # Algoritmos de visión por computador y OCR para carnets
│   ├── image_optim.py               # Compresión y conversión automática a WebP
│   ├── middleware.py                # Control de usuarios activos y sesiones
│   ├── auth_backends.py             # Backend de autenticación compatible con MySQL
│   ├── context_processors.py        # Métricas de notificaciones y carrito en plantillas
│   ├── views.py                     # Vistas de administración, inventario, reportes y préstamos
│   ├── views_login.py               # Login, rate limiting, registro y restablecimiento de clave
│   ├── views_usuario.py             # Vistas del portal de aprendices y carrito
│   ├── views_catalogo_wizard.py     # Lógica del asistente interactivo de catálogos
│   ├── views_catalogo_panel.py      # Estructura de árbol y conteo de dependencias
│   ├── application/                 # Capa de casos de uso desacoplados (Clean Architecture)
│   ├── interfaces/                  # Adaptadores HTTP
│   ├── management/commands/         # Tareas CLI (CSS build, notificaciones, optimizador)
│   ├── templatetags/                # Tags de plantilla (ej. {% css_asset %})
│   ├── templates/inventario/        # Plantillas HTML modulares por área
│   └── static/inventario/           # Hojas de estilo CSS, scripts JS y Tailwind
├── media/                           # Archivos multimedia subidos (fotos, carnets, evidencias)
├── DIAGRAMAS_VALIDACION_SENA.md     # Diagramas Mermaid detallados de la validación SENA
├── package.json                     # Scripts y dependencias Node.js (Tailwind CSS)
├── requirements.txt                 # Dependencias Python
└── manage.py                        # CLI principal de Django
```

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado en tu equipo:

1. **Python 3.12+**: [python.org](https://www.python.org/)
2. **Node.js 18+ y npm**: [nodejs.org](https://nodejs.org/) (requerido para compilar Tailwind CSS)
3. **Servidor MySQL / MariaDB**:
   * En local puedes usar **XAMPP** o un servicio MySQL independiente (puerto por defecto: `3307` o `3306`).
4. **Tesseract OCR (Opcional en desarrollo, recomendado):**
   * En Windows: [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki) (agregado al `PATH`).

---

## ⚙️ Instalación y Puesta en Marcha

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/SGIT-CIDE-Sibate.git
cd SGIT-CIDE-Sibate
```

### 2. Configurar el Entorno Virtual de Python

```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# En Windows (PowerShell):
.venv\Scripts\Activate.ps1
# En Windows (CMD):
.venv\Scripts\activate.bat
# En Linux/macOS:
source .venv/bin/activate
```

### 3. Instalar Dependencias de Python

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar la Base de Datos MySQL

Crea la base de datos en tu gestor MySQL (por ejemplo `invsena` o `senainventario`):

```sql
CREATE DATABASE invsena CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

*(Opcional: Si dispones de un volcado inicial, puedes importarlo con `mysql -u root -p -P 3307 invsena < senainventario.sql`).*

### 5. Instalar y Compilar Assets de Frontend

```bash
# Instalar dependencias npm (Tailwind CSS)
npm install

# Compilar Tailwind CSS
npm run tw:build

# Compilar y minificar hojas de estilo modulares de Django
python manage.py build_css_assets
```

### 6. Ejecutar Migraciones de Django

```bash
python manage.py migrate
```

### 7. Crear el Superusuario Administrador

```bash
python manage.py createsuperuser
```
> **Nota:** El sistema utiliza el **correo electrónico** como nombre de usuario principal (`USERNAME_FIELD = 'correo'`).

### 8. Iniciar el Servidor de Desarrollo

```bash
python manage.py runserver
```

Abre tu navegador e ingresa a:  
👉 **`http://127.0.0.1:8000/`**

---

## 🔐 Variables de Entorno

Puedes configurar las siguientes variables de entorno en tu sistema o en un archivo de entorno según el servidor:

| Variable | Descripción | Valor por Defecto |
| :--- | :--- | :--- |
| `DJANGO_DEBUG` | Activa o desactiva el modo de depuración de Django | `True` en local, `False` en PythonAnywhere |
| `LOCAL_DB_NAME` | Nombre de la base de datos MySQL local | `invsena` |
| `LOCAL_DB_USER` | Usuario de la base de datos local | `root` |
| `LOCAL_DB_PASSWORD`| Contraseña de la base de datos local | `""` (vacío) |
| `LOCAL_DB_HOST` | Host del servidor MySQL | `127.0.0.1` |
| `LOCAL_DB_PORT` | Puerto de conexión MySQL | `3307` |
| `USE_BUILT_CSS` | Usa los archivos `.min.css` generados por el pipeline | `False` en desarrollo, `True` en producción |
| `EMAIL_HOST_PASSWORD`| API Key SMTP de Resend para envío de correos | `""` (usa consola si está vacío) |
| `DEFAULT_FROM_EMAIL`| Remitente de notificaciones por correo | `Inventario SENA <onboarding@resend.dev>` |

---

## ⌨️ Comandos de Gestión Personalizados

El proyecto incluye comandos de consola personalizados en `inventario/management/commands/`:

### Compilar y Minificar CSS del Proyecto
```bash
python manage.py build_css_assets
```
Genera los archivos `.min.css` en `inventario/static/inventario/css-build/` y actualiza el archivo de manifiesto `manifest.json`.

### Notificar Préstamos Vencidos y por Vencer
```bash
python manage.py notificar_vencidos
```
Revisa automáticamente en la base de datos aquellos préstamos que hayan alcanzado su fecha límite de retorno o estén próximos a vencer, enviando notificaciones y actualizando estados. *Recomendado para programar como Cron Job o Tarea programada en el servidor.*

### Optimizar Imágenes Existentes de Productos a WebP
```bash
python manage.py optimizar_imagenes_productos
```
Recorre el catálogo de productos existente y convierte las imágenes en formatos pesados (PNG, JPG) a formato optimizado WebP.

---

## 🎨 Pipeline de CSS y Tailwind

El sistema utiliza una arquitectura híbrida para estilos:
1. **CSS Modular Tradicional:** Ubicado en `inventario/static/inventario/css/` separado por módulos (`admin`, `dashboard`, `inventario`, `user`).
2. **Tailwind CSS Gradual:** Configurado con el prefijo obligatorio `tw-` para permitir el uso ágil de utilidades sin colisionar con los estilos preexistentes.

### Comandos de Tailwind:
```bash
# Compilar una sola vez minificado para producción:
npm run tw:build

# Modo vigilancia activa (Watch) durante desarrollo:
npm run tw:watch
```

---

## 🧪 Pruebas Automatizadas

El proyecto cuenta con una suite completa de pruebas unitarias y de integración en [inventario/tests.py](file:///c:/xampp/htdocs/invt_sena/inventario/tests.py) que verifican la gestión de usuarios, seguridad de contraseñas, validación SENA, middlewares y reglas de negocio.

Para ejecutar todas las pruebas:

```bash
python manage.py test inventario
```

Para ejecutar una prueba específica:

```bash
python manage.py test inventario.tests.GestionEstadoUsuarioTests
```

---

## 📄 Licencia y Créditos

* **Institución:** Servicio Nacional de Aprendizaje (SENA) — Centro Industrial y de Desarrollo Empresarial (CIDE), Sede La Colonia / Sibaté.
* **Propósito:** Software desarrollado con fines pedagógicos y de optimización operativa para el inventario de laboratorios, talleres y almacén general.
