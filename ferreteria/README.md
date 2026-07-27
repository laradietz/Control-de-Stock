# Sistema de Control de Stock - Ferretería Gian

Sistema de gestión integral para ferretería: inventario, ventas, boletas,
caja diaria, clientes, estadísticas y más. Interfaz gráfica con Tkinter,
base de datos SQLite y exportación a Excel/PDF.

## Funcionalidades

### Ventas
- Punto de venta con carrito (búsqueda de productos, cantidad, total automático)
- El stock se descuenta solo al confirmar la venta
- Generación de boletas en PDF, listas para imprimir
- Historial de ventas con filtros por fecha (hoy / semana / mes)
- Anulación de ventas (devuelve el stock automáticamente)

### Caja
- Resumen diario: cantidad de ventas, total recaudado, ventas anuladas
- Top de productos más vendidos del día
- Cierre de caja exportable a PDF

### Inventario
- CRUD completo de productos (alta, baja, modificación, consulta)
- Control de stock mínimo con alertas visuales (filas en rojo)
- Aviso emergente al iniciar si hay productos con stock bajo
- Movimientos manuales de stock (entradas/salidas) con historial y motivo
- Actualización automática de precios por proveedor: aplicá un % de
  aumento o reducción a todos los productos de un proveedor de una sola vez

### Compras a proveedores
- Armado de pedidos manuales: elegís proveedor, productos y cantidades
- Generación automática de pedidos con todos los productos en stock bajo
- Marcado de pedidos como "recibidos", lo que suma el stock automáticamente
- Carga de comprobantes de compra (facturas, remitos) en PDF o foto,
  como respaldo asociado a cada proveedor o pedido

### Clientes
- Alta, modificación y baja de clientes
- Historial de compras por cliente

### Proveedores y categorías
- CRUD completo de proveedores (nombre, contacto, teléfono, email)
- Gestión de categorías de productos

### Estadísticas
- Gráfico de recaudación por día (7/30/90 días)
- Gráfico de productos más vendidos
- Alertas de stock bajo

### Reportes y exportación
- Exportación de inventario a Excel (.xlsx) y PDF
- Reporte específico de productos con stock bajo

### Usuarios
- Login con usuario y contraseña
- Roles: dueño (acceso total) y empleado
- Alta, baja y cambio de contraseña de usuarios

### Backup
- Backup automático de la base de datos al iniciar el programa
- Backup manual desde el menú
- Restauración de backups anteriores
- Limpieza automática de backups con más de 30 días

## Requisitos

- Python 3.10 o superior
- Tkinter (incluido en la mayoría de instalaciones de Python)

## Instalación

```bash
pip install openpyxl reportlab matplotlib pillow
```

## Ejecución

```bash
python main.py
```

O hacer doble clic en `INICIAR.bat` (Windows).

Usuario por defecto: `dueño` / contraseña `1234`

En la primera ejecución se crea automáticamente la base de datos
`db/ferreteria.db`, cargada con categorías, proveedores y productos
de ejemplo.

## Estructura del proyecto

```
ferreteria/
├── main.py                       # Ventana principal (punto de entrada)
├── database.py                   # Conexión y esquema de la base de datos
├── modelos.py                    # Producto, Proveedor, Categoria, Cliente, Venta
├── inventario.py                 # Lógica de negocio: CRUD, ventas, caja, precios
├── exportador.py                 # Exportación a Excel, PDF y boletas
├── backup.py                     # Backup automático de la base de datos
├── ventana_login.py              # Pantalla de inicio de sesión
├── ventana_producto.py           # Alta/edición de productos
├── ventana_ventas.py             # Punto de venta (carrito)
├── ventana_historial_ventas.py   # Historial y anulación de ventas
├── ventana_caja.py               # Caja diaria y cierre
├── ventana_clientes.py           # Gestión de clientes
├── ventana_proveedores.py        # Gestión de proveedores
├── ventana_categorias.py         # Gestión de categorías
├── ventana_precios.py            # Actualización de precios por proveedor (%)
├── ventana_movimientos.py        # Entradas/salidas manuales de stock
├── ventana_estadisticas.py       # Gráficos de ventas
├── ventana_reportes.py           # Reporte de stock bajo
├── ventana_usuarios.py           # Gestión de usuarios
├── ventana_backup.py             # Backup y restauración
├── db/
│   ├── ferreteria.db             # Base de datos SQLite (autogenerada)
│   └── backups/                  # Backups automáticos y manuales
├── exports/                      # Reportes y boletas exportadas
└── docs/
    ├── Documentacion_Tecnica_Ferreteria.docx
    └── diagrama_uml.png
```

## Cómo aumentar precios por proveedor

1. Menú lateral → Actualizar Precios
2. Seleccioná el proveedor en la tabla
3. Ingresá el porcentaje (ejemplo: 10 para +10%, -5 para -5%)
4. Revisá la vista previa de los nuevos precios
5. Hacé clic en "Aplicar aumento a TODOS los productos del proveedor"

Todos los productos asociados a ese proveedor se actualizan automáticamente.

Para más detalle, ver docs/Documentacion_Tecnica_Ferreteria.docx
