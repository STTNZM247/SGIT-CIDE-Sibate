# Diagramas de Validación SENA

Este archivo contiene 3 diagramas Mermaid del sistema de validación SENA.

Puedes:
- Copiar el código y pegarlo en https://mermaid.live/ para exportar a PNG/SVG
- Usar la extensión Mermaid en VS Code para visualizar
- Incluirlo en documentación de GitHub

---

## 1. FLUJO COMPLETO DE VALIDACIÓN SENA

```mermaid
flowchart TD
    A["👤 Usuario Registrado<br/>(Estado: pendiente)"] --> B{¿Intenta hacer pedido?}
    
    B -->|SÍ| C["🔍 Sistema verifica<br/>verificacion_sena_estado"]
    B -->|NO| A
    
    C --> D{¿Estado<br/>== validado?}
    
    D -->|✓ SÍ| E["✅ Pedido autorizado<br/>Procede a crear pedido"]
    
    D -->|✗ NO| F["⚠️ BLOQUEO<br/>Redirige a validación"]
    
    F --> G["📱 Pantalla de Validación"]
    
    G --> H{¿Qué opción?}
    
    H -->|Cámara guiada| I["📸 Captura del carnet SENA"]
    H -->|Galería/archivo| J["📁 Selecciona foto existente"]
    
    I --> K["🧠 Validación Automática"]
    J --> K
    
    K --> L["1️⃣ OCR Tesseract<br/>Extrae texto del carnet"]
    L --> M["2️⃣ Detección de logo SENA<br/>Verifica área verde"]
    M --> N["3️⃣ Valida nombre<br/>Compara con cuenta"]
    N --> O["4️⃣ Valida documento<br/>Compara con CC"]
    
    O --> P{¿Todas<br/>validaciones<br/>OK?}
    
    P -->|✅ SÍ| Q["✅ ÉXITO<br/>Estado → validado<br/>Guarda imagen<br/>Timestamp: validada_en"]
    P -->|❌ NO| R["❌ FALLA<br/>Estado → pendiente<br/>Guarda razones"]
    
    Q --> S["🔔 Notificación de aprobación"]
    S --> T["🔄 Redirige al carrito"]
    T --> E
    
    R --> U["⚡ Muestra errores:<br/>- Logo no detectado<br/>- Nombre no coincide<br/>- Documento no coincide<br/>- OCR fallo"]
    
    U --> V{¿Usuario elige<br/>validación<br/>manual?}
    
    V -->|SÍ| W["📧 Solicita validación manual<br/>Estado → solicitada"]
    V -->|NO| G
    
    W --> X["👨‍💼 Admin recibe notificación"]
    X --> Y["🔗 Admin envía enlace<br/>con token (24h)<br/>Estado → enlace_enviado"]
    Y --> Z["📨 Usuario recibe email"]
    
    Z --> AA["🔐 Usuario abre enlace<br/>Pantalla de carga manual"]
    AA --> AB["📄 Sube carnet o<br/>certificado SENA<br/>Estado → documento_cargado"]
    
    AB --> AC["👨‍💼 Admin revisa documento"]
    AC --> AD{¿Documento<br/>válido?}
    
    AD -->|✅ SÍ| AE["✅ Admin aprueba<br/>Estado → validado<br/>Timestamp: validada_en"]
    AD -->|❌ NO| AF["❌ Admin rechaza<br/>Estado → rechazada"]
    
    AE --> AG["🔔 Notificación de aprobación"]
    AG --> AH["✅ Usuario puede hacer pedidos"]
    AH --> E
    
    AF --> AI["🔔 Notificación de rechazo"]
    AI --> A
    
    E --> AJ["✅ Pedido creado exitosamente"]
    
    style A fill:#e1f5e1
    style E fill:#c8e6c9
    style Q fill:#a5d6a7
    style AE fill:#a5d6a7
    style F fill:#ffcccc
    style R fill:#ffcccc
    style AF fill:#ffcccc
    style U fill:#fff3cd
    style V fill:#fff3cd
    style W fill:#fff3cd
```

---

## 2. ARQUITECTURA DE COMPONENTES

```mermaid
graph TB
    subgraph "🗄️ BASE DE DATOS"
        DB["Usuario Model<br/>─ verificacion_sena_estado<br/>─ verificacion_sena_imagen<br/>─ verificacion_sena_documento<br/>─ verificacion_sena_validada_en<br/>─ verificacion_sena_solicitada_en<br/>─ verificacion_sena_observacion"]
        TOKEN["VerificacionSenaToken<br/>─ token (urlsafe)<br/>─ usuario_fk<br/>─ expira_en<br/>─ usado_en"]
    end
    
    subgraph "🧠 LÓGICA DE VALIDACIÓN"
        VAL["validacion_sena.py<br/>─ cargar_imagen_validacion()<br/>─ intentar_validacion_automatica()<br/>─ _extraer_texto_ocr()<br/>─ _detectar_logo_sena()<br/>─ normalizar_texto()"]
        OCR["Tesseract OCR<br/>(Library)"]
        PIL["Pillow<br/>(Image Processing)"]
    end
    
    subgraph "👁️ FRONTEND"
        TMPL_AUTO["validacion_sena.html<br/>─ Cámara guiada<br/>─ Galería/archivo<br/>─ Vista previa"]
        TMPL_MANUAL["validacion_sena_manual.html<br/>─ Carga documento<br/>─ Validación token"]
        CSS["validacion_sena.css"]
        JS["validacion_sena.js<br/>(Captura cámara)"]
    end
    
    subgraph "⚙️ VISTAS (Views)"
        USER_VIEWS["views_usuario.py<br/>─ validacion_sena()<br/>─ solicitar_validacion_manual()<br/>─ validacion_sena_carga_manual()<br/>─ usuario_realizar_pedido()"]
        ADMIN_VIEWS["views.py<br/>─ enviar_enlace_validacion_sena()<br/>─ aprobar_validacion_sena()"]
        HELPER["Helper Functions<br/>─ _usuario_tiene_validacion_sena()<br/>─ _build_carrito_context()"]
    end
    
    subgraph "🔗 RUTAS"
        ROUTES["/usuario/validacion-sena/<br/>/usuario/solicitar-manual/<br/>/usuario/carga-manual/{token}/<br/>/usuario/realizar-pedido/<br/>/usuarios/{id}/enviar-enlace/<br/>/usuarios/{id}/aprobar/"]
    end
    
    subgraph "📧 NOTIFICACIONES"
        NOTIF["Notificacion Model<br/>─ verificacion_sena_aprobada<br/>─ solicitud_validacion_sena<br/>─ staff_solicitud_validacion_sena<br/>─ enlace_validacion_sena<br/>─ documento_validacion_sena"]
        EMAIL["Email Backend<br/>(Django)"]
    end
    
    subgraph "🔐 SEGURIDAD"
        AUTH["@login_required<br/>Rol validation<br/>Token expiry (24h)<br/>One-time use"]
    end
    
    VAL --> OCR
    VAL --> PIL
    
    USER_VIEWS --> VAL
    USER_VIEWS --> DB
    USER_VIEWS --> TOKEN
    ADMIN_VIEWS --> DB
    ADMIN_VIEWS --> TOKEN
    
    USER_VIEWS --> HELPER
    HELPER --> DB
    
    ROUTES --> USER_VIEWS
    ROUTES --> ADMIN_VIEWS
    
    TMPL_AUTO --> JS
    TMPL_AUTO --> CSS
    TMPL_AUTO --> USER_VIEWS
    
    TMPL_MANUAL --> USER_VIEWS
    
    USER_VIEWS --> NOTIF
    ADMIN_VIEWS --> NOTIF
    NOTIF --> EMAIL
    
    AUTH --> USER_VIEWS
    AUTH --> ADMIN_VIEWS
    TOKEN --> AUTH
    
    style DB fill:#e3f2fd
    style TOKEN fill:#e3f2fd
    style VAL fill:#f3e5f5
    style OCR fill:#ede7f6
    style PIL fill:#ede7f6
    style USER_VIEWS fill:#e8f5e9
    style ADMIN_VIEWS fill:#e8f5e9
    style HELPER fill:#e8f5e9
    style TMPL_AUTO fill:#fff3e0
    style TMPL_MANUAL fill:#fff3e0
    style NOTIF fill:#fce4ec
    style EMAIL fill:#fce4ec
    style AUTH fill:#ffebee
```

---

## 3. MÁQUINA DE ESTADOS

```mermaid
stateDiagram-v2
    [*] --> pendiente: Usuario registrado<br/>Sin validación
    
    pendiente --> pendiente: Intenta validar automática<br/>y falla
    
    pendiente --> validado: Validación automática<br/>exitosa (OCR OK)
    
    pendiente --> solicitada: Usuario solicita<br/>validación manual
    
    solicitada --> enlace_enviado: Admin envía<br/>enlace con token
    
    enlace_enviado --> documento_cargado: Usuario carga<br/>documento
    
    documento_cargado --> validado: Admin aprueba<br/>validación
    
    documento_cargado --> rechazada: Admin rechaza<br/>validación
    
    rechazada --> solicitada: Usuario puede<br/>solicitar de nuevo
    
    validado --> [*]: Usuario puede<br/>hacer pedidos ✅
    
    note right of pendiente
        BLOQUEA PEDIDOS ❌
        Estado inicial
        OCR falló
    end note
    
    note right of solicitada
        BLOQUEA PEDIDOS ❌
        Esperando enlace
        del admin
    end note
    
    note right of enlace_enviado
        BLOQUEA PEDIDOS ❌
        Esperando que usuario
        cargue documento
    end note
    
    note right of documento_cargado
        BLOQUEA PEDIDOS ❌
        Pendiente revisión
        del admin
    end note
    
    note right of rechazada
        BLOQUEA PEDIDOS ❌
        Admin rechazó
        la evidencia
    end note
    
    note right of validado
        PERMITE PEDIDOS ✅
        Usuario verificado
        Una sola vez por
        ciclo de vida
    end note
```

---

## Cómo usar estos diagramas

### En GitHub/GitLab
Copia el código Mermaid directamente en un `.md` - se renderiza automáticamente.

### En Notion, Confluencia, etc.
Usa https://mermaid.live/ → Pega el código → Exporta a PNG/SVG

### En PowerPoint/Presentaciones
1. Ve a https://mermaid.live/
2. Pega el código del diagrama
3. Click en "Download" → Selecciona PNG o SVG
4. Inserta la imagen en tu presentación

### En VS Code
Instala extensión **"Markdown Preview Mermaid Support"** y visualiza este archivo directamente.

---

**Creado:** 22 de abril de 2026
**Proyecto:** Sistema de Inventario SENA - Validación SENA
