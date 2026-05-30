## Resumen de hoy (29 de mayo)

- Se reorganizó la estructura del frontend y CSS del proyecto para dejar estilos más modulares por panel y funcionalidad.
- Se corrigieron rutas y referencias estáticas para mantener consistencia en la carga de assets.
- Se ajustó nomenclatura/organización general (alineación de nombres y módulos) para reducir confusión en mantenimiento.
- Se consolidó el flujo de compilación de CSS (build + manifest) para evitar diferencias entre estilos fuente y estilos servidos.

- Se corrigieron desajustes visuales en varios paneles (`pedidos`, `prestamos`, `auditorias`) por bloques CSS truncados o mal ubicados.
- Se mejoró el panel de `inventario` en búsqueda/select para que quedara consistente con el panel de usuario.
- Se rediseñaron las tarjetas de productos en inventario (mejor jerarquía visual, chips, espaciado y dark mode).
- Se mejoró la ventana/modal de detalle rápido de producto con mejor estructura visual y legibilidad.
- Se ensanchó y reorganizó el formulario de `Nuevo producto` en catálogo para mejor distribución.
- Se implementó lógica de subcategorías por catálogo: solo se muestran las subcategorías del catálogo seleccionado.
- Se cambió la selección de subcategorías a estilo visual tipo “carpetas” (en lugar de selector nativo).
- Se eliminó del flujo de `Nuevo producto` la función de crear “nuevas subcategorías” para simplificar la experiencia de usuarios nuevos.
- Se ajustó el layout del formulario para evitar espacios en blanco y selects sobredimensionados.
- Se implementó gestión de `Ubicaciones de productos`.
- Nuevo botón en catálogo para abrir mini formulario y registrar ubicaciones por nombre.
- Nuevo modelo `UbicacionProducto` y relación en `Catalogo` (`id_ubicacion_fk`).
- Nuevo selector tipo “carpetas” en `Nuevo catálogo` para asignar ubicación predeterminada.
- Autocompletado de ubicación en `Nuevo producto` según catálogo seleccionado.
- Se creó y aplicó migración `0026_ubicacionproducto_catalogo_id_ubicacion_fk`.
- Validaciones ejecutadas durante los cambios: `build_css_assets`, `check` y `migrate` completados correctamente.
