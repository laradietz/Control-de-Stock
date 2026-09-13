# Control de Stock — Ferretería Gian

Sistema de escritorio para la gestión integral de una ferretería: ventas,
inventario, caja, clientes, proveedores y reportes. Desarrollado en Python
con interfaz gráfica (Tkinter) y base de datos SQLite, para uso real de un
comercio.

## ¿Qué problema resuelve?

Un comercio chico necesita llevar el control de su stock, registrar ventas
con boleta, saber cuánto recaudó por día y no quedarse sin productos sin
darse cuenta — sin depender de una planilla de Excel manual ni de un
sistema en la nube con costo mensual. Esta aplicación cubre ese flujo
completo como programa de escritorio, con una base de datos local.

## Características

- **Ventas**: punto de venta con carrito, descuento automático de stock,
  boletas en PDF, historial filtrable por fecha, anulación de ventas
- **Caja**: resumen diario (ventas, recaudación, anulaciones), top de
  productos vendidos, cierre exportable a PDF
- **Inventario**: CRUD de productos, alertas de stock mínimo, movimientos
  manuales de stock con historial, actualización de precios por proveedor
  (aumento/reducción porcentual masivo)
- **Compras**: pedidos manuales o automáticos a partir del stock bajo,
  recepción de pedidos con suma automática de stock, carga de comprobantes
- **Clientes y proveedores**: alta/baja/modificación, historial de compras
- **Estadísticas**: gráficos de recaudación y productos más vendidos
- **Reportes**: exportación de inventario a Excel y PDF
- **Usuarios**: login con roles (dueño/empleado)
- **Backups**: automáticos al iniciar, manuales desde el menú, con
  limpieza de backups antiguos

## Tecnologías

- Python 3
- Tkinter (interfaz gráfica)
- SQLite (base de datos relacional local, con foreign keys)
- openpyxl (exportación a Excel), reportlab (PDF), matplotlib (gráficos)
- PyInstaller (empaquetado como ejecutable de Windows)

## Arquitectura

Separación por responsabilidad dentro de un mismo paquete: `database.py`
concentra el esquema y la conexión, `modelos.py` define las entidades del
dominio, `inventario.py` contiene la lógica de negocio (ventas, stock,
caja, precios), `exportador.py` y `backup.py` son utilidades transversales,
y cada `ventana_*.py` es una pantalla independiente de la interfaz que
consume esa lógica — sin queries SQL sueltas dentro de las ventanas.

```
Interfaz (ventana_*.py)
    ↓
Lógica de negocio (inventario.py)
    ↓
Acceso a datos (database.py)
    ↓
SQLite
```

## Instalación

Requiere Python 3.10+.

```bash
git clone https://github.com/laradietz/Control-de-Stock.git
cd Control-de-Stock/ferreteria
pip install openpyxl reportlab matplotlib pillow
```

## Ejecución

```bash
python main.py
```

En la primera ejecución se crea automáticamente la base de datos en
`db/ferreteria.db`, cargada con categorías, proveedores y productos de
ejemplo. Usuario por defecto: `dueño` / `1234`.

## Documentación técnica

El repositorio incluye documentación adicional en `ferreteria/docs/`:
un diagrama UML del modelo de datos y un documento técnico detallado.

## Qué aprendí

- Diseñar un esquema relacional normalizado a mano con SQLite (incluyendo
  claves foráneas) sin el andamiaje de un ORM.
- Manejar rutas de archivo de forma distinta según el programa corra desde
  código fuente o empaquetado como `.exe` con PyInstaller.
- Construir una aplicación de escritorio con varias pantallas que comparten
  estado (stock, caja) de forma consistente.

## Próximas mejoras

- Extraer la lógica de `inventario.py` en servicios más chicos y testeables
  (hoy concentra ventas, stock y caja en un mismo módulo).
- Agregar tests automatizados sobre las reglas de negocio (descuento de
  stock, anulación de ventas, cálculo de caja).
- Migrar el almacenamiento de comprobantes/backups a una carpeta configurable
  fuera del repositorio del proyecto.
