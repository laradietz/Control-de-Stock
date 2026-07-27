"""
database.py - Base de datos relacional normalizada para Ferretería Gian.
Incluye tablas para: categorias, proveedores, productos, clientes,
ventas, detalle_ventas, movimientos_stock, usuarios, backups.
"""

import sqlite3
import os
import hashlib
import sys

# Cuando corre como .exe (PyInstaller), la DB debe estar junto al ejecutable
if os.environ.get("FERRETERIA_BASE_DIR"):
    _base = os.environ["FERRETERIA_BASE_DIR"]
elif getattr(sys, 'frozen', False):
    _base = os.path.dirname(sys.executable)
else:
    _base = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(_base, "db", "ferreteria.db")


def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def inicializar_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = conectar()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS categorias (
            id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS proveedores (
            id_proveedor INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            contacto TEXT,
            telefono TEXT,
            email TEXT
        );

        CREATE TABLE IF NOT EXISTS productos (
            id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL UNIQUE,
            nombre TEXT NOT NULL,
            id_categoria INTEGER,
            precio REAL NOT NULL CHECK (precio >= 0),
            cantidad INTEGER NOT NULL CHECK (cantidad >= 0),
            stock_minimo INTEGER NOT NULL DEFAULT 5 CHECK (stock_minimo >= 0),
            id_proveedor INTEGER,
            FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria) ON DELETE SET NULL,
            FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS clientes (
            id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT,
            email TEXT,
            direccion TEXT,
            fecha_alta TEXT DEFAULT (date('now'))
        );

        CREATE TABLE IF NOT EXISTS ventas (
            id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT DEFAULT (datetime('now','localtime')),
            total REAL NOT NULL,
            id_cliente INTEGER,
            usuario TEXT DEFAULT 'dueño',
            anulada INTEGER DEFAULT 0,
            FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS detalle_ventas (
            id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
            id_venta INTEGER NOT NULL,
            id_producto INTEGER,
            nombre_producto TEXT NOT NULL,
            precio_unitario REAL NOT NULL,
            cantidad INTEGER NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (id_venta) REFERENCES ventas(id_venta) ON DELETE CASCADE,
            FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS movimientos_stock (
            id_movimiento INTEGER PRIMARY KEY AUTOINCREMENT,
            id_producto INTEGER,
            nombre_producto TEXT NOT NULL,
            tipo TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            motivo TEXT,
            fecha TEXT DEFAULT (datetime('now','localtime')),
            usuario TEXT DEFAULT 'dueño',
            FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            rol TEXT NOT NULL DEFAULT 'empleado'
        );

        CREATE TABLE IF NOT EXISTS ordenes_compra (
            id_orden INTEGER PRIMARY KEY AUTOINCREMENT,
            id_proveedor INTEGER,
            fecha TEXT DEFAULT (datetime('now','localtime')),
            estado TEXT NOT NULL DEFAULT 'pendiente',
            usuario TEXT DEFAULT 'dueño',
            notas TEXT,
            FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS detalle_orden_compra (
            id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
            id_orden INTEGER NOT NULL,
            id_producto INTEGER,
            nombre_producto TEXT NOT NULL,
            cantidad_pedida INTEGER NOT NULL,
            cantidad_recibida INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (id_orden) REFERENCES ordenes_compra(id_orden) ON DELETE CASCADE,
            FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS comprobantes_compra (
            id_comprobante INTEGER PRIMARY KEY AUTOINCREMENT,
            id_proveedor INTEGER,
            id_orden INTEGER,
            fecha TEXT DEFAULT (datetime('now','localtime')),
            numero_comprobante TEXT,
            monto REAL,
            archivo_nombre TEXT NOT NULL,
            archivo_ruta TEXT NOT NULL,
            notas TEXT,
            usuario TEXT DEFAULT 'dueño',
            FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor) ON DELETE SET NULL,
            FOREIGN KEY (id_orden) REFERENCES ordenes_compra(id_orden) ON DELETE SET NULL
        );
    """)
    conn.commit()

    # Datos de ejemplo solo si están vacías
    cur.execute("SELECT COUNT(*) FROM categorias")
    if cur.fetchone()[0] == 0:
        _cargar_datos_ejemplo(conn)

    # Usuario dueño por defecto
    cur.execute("SELECT COUNT(*) FROM usuarios")
    if cur.fetchone()[0] == 0:
        pwd = hashlib.sha256("1234".encode()).hexdigest()
        cur.execute("INSERT INTO usuarios (nombre, password_hash, rol) VALUES (?, ?, ?)",
                    ("dueño", pwd, "dueño"))
        conn.commit()

    conn.close()
    migrar_db()


def _cargar_datos_ejemplo(conn):
    cur = conn.cursor()
    categorias = ["Herramientas Manuales","Tornillería","Electricidad",
                  "Pinturas","Plomería","Herramientas Eléctricas"]
    cur.executemany("INSERT INTO categorias (nombre) VALUES (?)", [(c,) for c in categorias])

    proveedores = [
        ("Truper Argentina","Juan Pérez","011-4555-1234","ventas@truper.com"),
        ("Stanley Black & Decker","María Gómez","011-4666-5678","contacto@stanley.com"),
        ("Distribuidora El Tornillo","Carlos Ruiz","011-4777-9012","info@eltornillo.com"),
        ("Pinturerías Sur","Ana López","011-4888-3456","ventas@pinturerias-sur.com"),
    ]
    cur.executemany("INSERT INTO proveedores (nombre,contacto,telefono,email) VALUES (?,?,?,?)", proveedores)

    productos = [
        ("HM-001","Martillo de carpintero 16oz",1,4500.00,25,5,1),
        ("HM-002","Destornillador Phillips PH2",1,1200.00,40,10,2),
        ("HM-003","Pinza universal 8 pulgadas",1,3200.00,15,5,1),
        ("TO-001","Tornillo autorroscante 1/4 x 1 (x100)",2,850.00,60,15,3),
        ("TO-002","Tuerca hexagonal M8 (x50)",2,600.00,8,10,3),
        ("EL-001","Cable unipolar 2.5mm (rollo x100m)",3,18500.00,5,2,4),
        ("EL-002","Llave de luz simple",3,950.00,30,8,4),
        ("PI-001","Pintura látex interior blanco 20L",4,32000.00,4,3,4),
        ("PI-002","Pincel 2 pulgadas",4,1100.00,18,5,4),
        ("PL-001","Caño PVC 1/2 pulgada (3m)",5,2300.00,12,4,3),
        ("HE-001","Taladro percutor 650W",6,45000.00,6,2,2),
        ("HE-002","Amoladora angular 4.5 pulgadas",6,38000.00,3,2,2),
    ]
    cur.executemany("""
        INSERT INTO productos (codigo,nombre,id_categoria,precio,cantidad,stock_minimo,id_proveedor)
        VALUES (?,?,?,?,?,?,?)
    """, productos)

    clientes = [
        ("Cliente General","","",""),
        ("Juan Rodríguez","011-1234-5678","juan@mail.com","Av. Rivadavia 1234"),
    ]
    cur.executemany("INSERT INTO clientes (nombre,telefono,email,direccion) VALUES (?,?,?,?)", clientes)
    conn.commit()


def migrar_db():
    """Agrega columnas y tablas nuevas sin perder datos existentes."""
    conn = conectar()
    cur = conn.cursor()

    # Columnas nuevas en productos
    for col, definition in [
        ("precio_costo", "REAL NOT NULL DEFAULT 0"),
        ("fecha_vencimiento", "TEXT"),
        ("ubicacion", "TEXT"),
    ]:
        try:
            cur.execute(f"ALTER TABLE productos ADD COLUMN {col} {definition}")
        except Exception:
            pass  # ya existe

    # Columna forma_pago en ventas
    try:
        cur.execute("ALTER TABLE ventas ADD COLUMN forma_pago TEXT NOT NULL DEFAULT 'efectivo'")
    except Exception:
        pass

    # Columna descuento en ventas
    try:
        cur.execute("ALTER TABLE ventas ADD COLUMN descuento REAL NOT NULL DEFAULT 0")
    except Exception:
        pass

    # Tabla cuenta corriente de clientes
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cuenta_corriente (
            id_movimiento INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            monto REAL NOT NULL,
            descripcion TEXT,
            id_venta INTEGER,
            fecha TEXT DEFAULT (datetime('now','localtime')),
            usuario TEXT DEFAULT 'dueño',
            FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE CASCADE,
            FOREIGN KEY (id_venta) REFERENCES ventas(id_venta) ON DELETE SET NULL
        )
    """)

    # Tabla devoluciones
    cur.execute("""
        CREATE TABLE IF NOT EXISTS devoluciones (
            id_devolucion INTEGER PRIMARY KEY AUTOINCREMENT,
            id_venta INTEGER NOT NULL,
            id_producto INTEGER,
            nombre_producto TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            motivo TEXT,
            fecha TEXT DEFAULT (datetime('now','localtime')),
            usuario TEXT DEFAULT 'dueño',
            FOREIGN KEY (id_venta) REFERENCES ventas(id_venta) ON DELETE CASCADE,
            FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE SET NULL
        )
    """)

    # Tabla ofertas
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ofertas (
            id_oferta INTEGER PRIMARY KEY AUTOINCREMENT,
            id_producto INTEGER NOT NULL,
            nombre_oferta TEXT NOT NULL,
            tipo TEXT NOT NULL,
            valor REAL NOT NULL,
            cantidad_minima INTEGER NOT NULL DEFAULT 1,
            fecha_desde TEXT,
            fecha_hasta TEXT,
            activa INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()
