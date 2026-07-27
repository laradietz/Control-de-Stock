"""modelos.py - Clases del dominio: Producto, Proveedor, Categoria, Cliente, Venta, DetalleVenta."""

class Categoria:
    def __init__(self, id_categoria, nombre):
        self.id_categoria = id_categoria
        self.nombre = nombre
    def __str__(self): return self.nombre

class Proveedor:
    def __init__(self, id_proveedor=None, nombre="", contacto="", telefono="", email=""):
        self.id_proveedor = id_proveedor
        self.nombre = nombre; self.contacto = contacto
        self.telefono = telefono; self.email = email
    def validar(self):
        if not self.nombre.strip(): return False, "El nombre del proveedor es obligatorio."
        if self.email and "@" not in self.email: return False, "El email no es válido."
        return True, ""
    def __str__(self): return self.nombre

class Producto:
    def __init__(self, id_producto=None, codigo="", nombre="", id_categoria=None,
                 precio=0.0, cantidad=0, stock_minimo=5, id_proveedor=None,
                 categoria_nombre="", proveedor_nombre=""):
        self.id_producto = id_producto
        self.codigo = str(codigo).strip(); self.nombre = str(nombre).strip()
        self.id_categoria = id_categoria; self.precio = precio
        self.cantidad = cantidad; self.stock_minimo = stock_minimo
        self.id_proveedor = id_proveedor
        self.categoria_nombre = categoria_nombre; self.proveedor_nombre = proveedor_nombre
    def validar(self):
        if not self.codigo: return False, "El código es obligatorio."
        if not self.nombre: return False, "El nombre es obligatorio."
        try:
            v = float(self.precio)
            if v < 0: return False, "El precio no puede ser negativo."
            self.precio = v
        except: return False, "El precio debe ser un número válido."
        try:
            v = int(self.cantidad)
            if v < 0: return False, "La cantidad no puede ser negativa."
            self.cantidad = v
        except: return False, "La cantidad debe ser un entero válido."
        try:
            v = int(self.stock_minimo)
            if v < 0: return False, "El stock mínimo no puede ser negativo."
            self.stock_minimo = v
        except: return False, "El stock mínimo debe ser un entero válido."
        return True, ""
    def stock_bajo(self): return self.cantidad <= self.stock_minimo
    def __str__(self): return f"[{self.codigo}] {self.nombre}"

class Cliente:
    def __init__(self, id_cliente=None, nombre="", telefono="", email="", direccion="", fecha_alta=""):
        self.id_cliente = id_cliente; self.nombre = nombre
        self.telefono = telefono; self.email = email
        self.direccion = direccion; self.fecha_alta = fecha_alta
    def validar(self):
        if not self.nombre.strip(): return False, "El nombre del cliente es obligatorio."
        return True, ""
    def __str__(self): return self.nombre

class DetalleVenta:
    def __init__(self, id_producto, nombre_producto, precio_unitario, cantidad):
        self.id_producto = id_producto; self.nombre_producto = nombre_producto
        self.precio_unitario = float(precio_unitario); self.cantidad = int(cantidad)
        self.subtotal = self.precio_unitario * self.cantidad

class Venta:
    def __init__(self, id_venta=None, fecha="", total=0.0, id_cliente=None,
                 cliente_nombre="", usuario="dueño", anulada=0, detalles=None):
        self.id_venta = id_venta; self.fecha = fecha; self.total = total
        self.id_cliente = id_cliente; self.cliente_nombre = cliente_nombre
        self.usuario = usuario; self.anulada = anulada
        self.detalles = detalles or []

class DetalleOrdenCompra:
    def __init__(self, id_detalle=None, id_producto=None, nombre_producto="",
                 cantidad_pedida=0, cantidad_recibida=0):
        self.id_detalle = id_detalle; self.id_producto = id_producto
        self.nombre_producto = nombre_producto
        self.cantidad_pedida = int(cantidad_pedida)
        self.cantidad_recibida = int(cantidad_recibida)

class OrdenCompra:
    def __init__(self, id_orden=None, id_proveedor=None, proveedor_nombre="",
                 fecha="", estado="pendiente", usuario="dueño", notas="", detalles=None):
        self.id_orden = id_orden; self.id_proveedor = id_proveedor
        self.proveedor_nombre = proveedor_nombre
        self.fecha = fecha; self.estado = estado
        self.usuario = usuario; self.notas = notas
        self.detalles = detalles or []

class Comprobante:
    def __init__(self, id_comprobante=None, id_proveedor=None, proveedor_nombre="",
                 id_orden=None, fecha="", numero_comprobante="", monto=0.0,
                 archivo_nombre="", archivo_ruta="", notas="", usuario="dueño"):
        self.id_comprobante = id_comprobante
        self.id_proveedor = id_proveedor; self.proveedor_nombre = proveedor_nombre
        self.id_orden = id_orden; self.fecha = fecha
        self.numero_comprobante = numero_comprobante; self.monto = monto
        self.archivo_nombre = archivo_nombre; self.archivo_ruta = archivo_ruta
        self.notas = notas; self.usuario = usuario

class Devolucion:
    def __init__(self, id_devolucion=None, id_venta=None, id_producto=None,
                 nombre_producto="", cantidad=0, precio_unitario=0.0,
                 motivo="", fecha="", usuario="dueño"):
        self.id_devolucion = id_devolucion
        self.id_venta = id_venta
        self.id_producto = id_producto
        self.nombre_producto = nombre_producto
        self.cantidad = int(cantidad)
        self.precio_unitario = float(precio_unitario)
        self.subtotal = self.precio_unitario * self.cantidad
        self.motivo = motivo
        self.fecha = fecha
        self.usuario = usuario

class MovimientoCuentaCorriente:
    def __init__(self, id_movimiento=None, id_cliente=None, tipo="",
                 monto=0.0, descripcion="", id_venta=None, fecha="", usuario="dueño"):
        self.id_movimiento = id_movimiento
        self.id_cliente = id_cliente
        self.tipo = tipo  # "cargo" o "pago"
        self.monto = float(monto)
        self.descripcion = descripcion
        self.id_venta = id_venta
        self.fecha = fecha
        self.usuario = usuario

class Oferta:
    def __init__(self, id_oferta=None, id_producto=None, nombre_producto="",
                 nombre_oferta="", tipo="porcentaje", valor=0.0,
                 cantidad_minima=1, fecha_desde=None, fecha_hasta=None, activa=1):
        self.id_oferta = id_oferta
        self.id_producto = id_producto
        self.nombre_producto = nombre_producto
        self.nombre_oferta = nombre_oferta
        self.tipo = tipo  # "porcentaje" o "precio_fijo"
        self.valor = float(valor)
        self.cantidad_minima = int(cantidad_minima)
        self.fecha_desde = fecha_desde
        self.fecha_hasta = fecha_hasta
        self.activa = bool(activa)

    def calcular_precio(self, precio_original, cantidad):
        if not self.activa or cantidad < self.cantidad_minima:
            return precio_original
        if self.tipo == "porcentaje":
            return round(precio_original * (1 - self.valor / 100), 2)
        elif self.tipo == "precio_fijo":
            return self.valor
        return precio_original
