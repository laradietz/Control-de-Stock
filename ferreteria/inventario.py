"""
inventario.py - Lógica de negocio completa: productos, ventas, clientes,
movimientos de stock, actualización de precios por proveedor, caja diaria.
"""
import hashlib
from database import conectar
from modelos import (Producto, Proveedor, Categoria, Cliente, Venta, DetalleVenta,
                     OrdenCompra, DetalleOrdenCompra, Comprobante,
                     Devolucion, MovimientoCuentaCorriente, Oferta)


class Inventario:

    # ── PRODUCTOS ──────────────────────────────────────────────
    def _row_to_producto(self, f):
        p = Producto(f[0],f[1],f[2],f[3],f[4],f[5],f[6],f[7],f[8],f[9])
        p.precio_costo = f[10] if len(f) > 10 else 0
        p.fecha_vencimiento = f[11] if len(f) > 11 else None
        p.ubicacion = f[12] if len(f) > 12 else ""
        return p

    def _query_productos(self, where="", params=()):
        sql = """
            SELECT p.id_producto,p.codigo,p.nombre,p.id_categoria,p.precio,
                   p.cantidad,p.stock_minimo,p.id_proveedor,
                   COALESCE(c.nombre,'Sin categoría'),COALESCE(pr.nombre,'Sin proveedor'),
                   COALESCE(p.precio_costo,0),p.fecha_vencimiento,COALESCE(p.ubicacion,'')
            FROM productos p
            LEFT JOIN categorias c ON p.id_categoria=c.id_categoria
            LEFT JOIN proveedores pr ON p.id_proveedor=pr.id_proveedor
        """ + where + " ORDER BY p.nombre ASC"
        conn = conectar(); cur = conn.cursor()
        cur.execute(sql, params); rows = cur.fetchall(); conn.close()
        return [self._row_to_producto(r) for r in rows]

    def obtener_productos(self, filtro_texto="", id_categoria=None, id_proveedor=None):
        where, params = "WHERE 1=1", []
        if filtro_texto:
            where += " AND (p.codigo LIKE ? OR p.nombre LIKE ?)"
            params += [f"%{filtro_texto}%"]*2
        if id_categoria: where += " AND p.id_categoria=?"; params.append(id_categoria)
        if id_proveedor: where += " AND p.id_proveedor=?"; params.append(id_proveedor)
        return self._query_productos(where, params)

    def obtener_producto_por_id(self, id_p):
        r = self._query_productos("WHERE p.id_producto=?", (id_p,))
        return r[0] if r else None

    def obtener_producto_por_codigo(self, codigo):
        r = self._query_productos("WHERE p.codigo=?", (codigo,))
        return r[0] if r else None

    def agregar_producto(self, p: Producto):
        ok, msg = p.validar()
        if not ok: raise ValueError(msg)
        conn = conectar(); cur = conn.cursor()
        cur.execute("SELECT 1 FROM productos WHERE codigo=?", (p.codigo,))
        if cur.fetchone(): conn.close(); raise ValueError(f"Código '{p.codigo}' ya existe.")
        cur.execute("""INSERT INTO productos
                       (codigo,nombre,id_categoria,precio,cantidad,stock_minimo,id_proveedor,
                        precio_costo,fecha_vencimiento,ubicacion)
                       VALUES (?,?,?,?,?,?,?,?,?,?)""",
                    (p.codigo,p.nombre,p.id_categoria,p.precio,p.cantidad,p.stock_minimo,
                     p.id_proveedor,getattr(p,'precio_costo',0),
                     getattr(p,'fecha_vencimiento',None),getattr(p,'ubicacion','')))
        conn.commit(); conn.close()

    def actualizar_producto(self, p: Producto):
        ok, msg = p.validar()
        if not ok: raise ValueError(msg)
        conn = conectar(); cur = conn.cursor()
        cur.execute("SELECT id_producto FROM productos WHERE codigo=?", (p.codigo,))
        f = cur.fetchone()
        if f and f[0] != p.id_producto: conn.close(); raise ValueError(f"Código '{p.codigo}' ya pertenece a otro producto.")
        cur.execute("""UPDATE productos SET codigo=?,nombre=?,id_categoria=?,precio=?,
                       cantidad=?,stock_minimo=?,id_proveedor=?,precio_costo=?,
                       fecha_vencimiento=?,ubicacion=? WHERE id_producto=?""",
                    (p.codigo,p.nombre,p.id_categoria,p.precio,p.cantidad,p.stock_minimo,
                     p.id_proveedor,getattr(p,'precio_costo',0),
                     getattr(p,'fecha_vencimiento',None),getattr(p,'ubicacion',''),p.id_producto))
        conn.commit(); conn.close()

    def eliminar_producto(self, id_p):
        conn = conectar(); cur = conn.cursor()
        cur.execute("DELETE FROM productos WHERE id_producto=?", (id_p,))
        conn.commit(); conn.close()

    def productos_stock_bajo(self):
        return [p for p in self.obtener_productos() if p.stock_bajo()]

    def actualizar_precios_proveedor(self, id_proveedor: int, porcentaje: float):
        """Aumenta/reduce el precio de todos los productos de un proveedor en el % dado."""
        if porcentaje <= -100: raise ValueError("El porcentaje no puede ser -100% o menor.")
        conn = conectar(); cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM productos WHERE id_proveedor=?", (id_proveedor,))
        cant = cur.fetchone()[0]
        if cant == 0: conn.close(); raise ValueError("El proveedor no tiene productos asociados.")
        factor = 1 + porcentaje / 100
        cur.execute("UPDATE productos SET precio = ROUND(precio * ?, 2) WHERE id_proveedor=?",
                    (factor, id_proveedor))
        conn.commit(); conn.close()
        return cant

    # ── CATEGORÍAS ─────────────────────────────────────────────
    def obtener_categorias(self):
        conn = conectar(); cur = conn.cursor()
        cur.execute("SELECT id_categoria,nombre FROM categorias ORDER BY nombre")
        rows = cur.fetchall(); conn.close()
        return [Categoria(r[0],r[1]) for r in rows]

    def agregar_categoria(self, nombre):
        nombre = nombre.strip()
        if not nombre: raise ValueError("El nombre no puede estar vacío.")
        conn = conectar(); cur = conn.cursor()
        cur.execute("SELECT 1 FROM categorias WHERE nombre=?", (nombre,))
        if cur.fetchone(): conn.close(); raise ValueError(f"La categoría '{nombre}' ya existe.")
        cur.execute("INSERT INTO categorias (nombre) VALUES (?)", (nombre,))
        conn.commit(); conn.close()

    # ── PROVEEDORES ────────────────────────────────────────────
    def obtener_proveedores(self):
        conn = conectar(); cur = conn.cursor()
        cur.execute("SELECT id_proveedor,nombre,contacto,telefono,email FROM proveedores ORDER BY nombre")
        rows = cur.fetchall(); conn.close()
        return [Proveedor(r[0],r[1],r[2],r[3],r[4]) for r in rows]

    def agregar_proveedor(self, p: Proveedor):
        ok, msg = p.validar()
        if not ok: raise ValueError(msg)
        conn = conectar(); cur = conn.cursor()
        cur.execute("SELECT 1 FROM proveedores WHERE nombre=?", (p.nombre,))
        if cur.fetchone(): conn.close(); raise ValueError(f"Proveedor '{p.nombre}' ya existe.")
        cur.execute("INSERT INTO proveedores (nombre,contacto,telefono,email) VALUES (?,?,?,?)",
                    (p.nombre,p.contacto,p.telefono,p.email))
        conn.commit(); conn.close()

    def actualizar_proveedor(self, p: Proveedor):
        ok, msg = p.validar()
        if not ok: raise ValueError(msg)
        conn = conectar(); cur = conn.cursor()
        cur.execute("UPDATE proveedores SET nombre=?,contacto=?,telefono=?,email=? WHERE id_proveedor=?",
                    (p.nombre,p.contacto,p.telefono,p.email,p.id_proveedor))
        conn.commit(); conn.close()

    def eliminar_proveedor(self, id_p):
        conn = conectar(); cur = conn.cursor()
        cur.execute("DELETE FROM proveedores WHERE id_proveedor=?", (id_p,))
        conn.commit(); conn.close()

    # ── CLIENTES ───────────────────────────────────────────────
    def obtener_clientes(self, filtro=""):
        conn = conectar(); cur = conn.cursor()
        if filtro:
            cur.execute("SELECT id_cliente,nombre,telefono,email,direccion,fecha_alta FROM clientes WHERE nombre LIKE ? ORDER BY nombre",
                        (f"%{filtro}%",))
        else:
            cur.execute("SELECT id_cliente,nombre,telefono,email,direccion,fecha_alta FROM clientes ORDER BY nombre")
        rows = cur.fetchall(); conn.close()
        return [Cliente(r[0],r[1],r[2],r[3],r[4],r[5]) for r in rows]

    def agregar_cliente(self, c: Cliente):
        ok, msg = c.validar()
        if not ok: raise ValueError(msg)
        conn = conectar(); cur = conn.cursor()
        cur.execute("INSERT INTO clientes (nombre,telefono,email,direccion) VALUES (?,?,?,?)",
                    (c.nombre,c.telefono,c.email,c.direccion))
        conn.commit(); conn.close()

    def actualizar_cliente(self, c: Cliente):
        ok, msg = c.validar()
        if not ok: raise ValueError(msg)
        conn = conectar(); cur = conn.cursor()
        cur.execute("UPDATE clientes SET nombre=?,telefono=?,email=?,direccion=? WHERE id_cliente=?",
                    (c.nombre,c.telefono,c.email,c.direccion,c.id_cliente))
        conn.commit(); conn.close()

    def eliminar_cliente(self, id_c):
        conn = conectar(); cur = conn.cursor()
        cur.execute("DELETE FROM clientes WHERE id_cliente=?", (id_c,))
        conn.commit(); conn.close()

    def historial_cliente(self, id_cliente):
        conn = conectar(); cur = conn.cursor()
        cur.execute("""SELECT v.id_venta, v.fecha, v.total, v.anulada
                       FROM ventas v WHERE v.id_cliente=? ORDER BY v.fecha DESC""", (id_cliente,))
        rows = cur.fetchall(); conn.close()
        return rows

    # ── VENTAS ─────────────────────────────────────────────────
    def registrar_venta(self, detalles: list, id_cliente=None, usuario="dueño"):
        if not detalles: raise ValueError("La venta no tiene productos.")
        total = sum(d.subtotal for d in detalles)
        conn = conectar(); cur = conn.cursor()
        cur.execute("INSERT INTO ventas (total,id_cliente,usuario) VALUES (?,?,?)",
                    (total, id_cliente, usuario))
        id_venta = cur.lastrowid
        for d in detalles:
            cur.execute("""INSERT INTO detalle_ventas (id_venta,id_producto,nombre_producto,
                           precio_unitario,cantidad,subtotal) VALUES (?,?,?,?,?,?)""",
                        (id_venta,d.id_producto,d.nombre_producto,d.precio_unitario,d.cantidad,d.subtotal))
            if d.id_producto:
                cur.execute("UPDATE productos SET cantidad = cantidad - ? WHERE id_producto=?",
                            (d.cantidad, d.id_producto))
                cur.execute("""INSERT INTO movimientos_stock (id_producto,nombre_producto,tipo,cantidad,motivo,usuario)
                               VALUES (?,?,'salida',?,?,?)""",
                            (d.id_producto,d.nombre_producto,d.cantidad,f"Venta #{id_venta}",usuario))
        conn.commit(); conn.close()
        return id_venta

    def anular_venta(self, id_venta: int, usuario="dueño"):
        conn = conectar(); cur = conn.cursor()
        cur.execute("SELECT anulada FROM ventas WHERE id_venta=?", (id_venta,))
        row = cur.fetchone()
        if not row: conn.close(); raise ValueError("Venta no encontrada.")
        if row[0]: conn.close(); raise ValueError("La venta ya fue anulada.")
        cur.execute("SELECT id_producto,nombre_producto,cantidad FROM detalle_ventas WHERE id_venta=?", (id_venta,))
        detalles = cur.fetchall()
        for d in detalles:
            if d[0]:
                cur.execute("UPDATE productos SET cantidad = cantidad + ? WHERE id_producto=?", (d[2],d[0]))
                cur.execute("""INSERT INTO movimientos_stock (id_producto,nombre_producto,tipo,cantidad,motivo,usuario)
                               VALUES (?,?,'entrada',?,?,?)""",
                            (d[0],d[1],d[2],f"Anulación venta #{id_venta}",usuario))
        cur.execute("UPDATE ventas SET anulada=1 WHERE id_venta=?", (id_venta,))
        conn.commit(); conn.close()

    def obtener_ventas(self, fecha_desde=None, fecha_hasta=None, solo_activas=False):
        conn = conectar(); cur = conn.cursor()
        sql = """SELECT v.id_venta,v.fecha,v.total,v.id_cliente,
                        COALESCE(c.nombre,'Sin cliente'),v.usuario,v.anulada
                 FROM ventas v LEFT JOIN clientes c ON v.id_cliente=c.id_cliente
                 WHERE 1=1"""
        params = []
        if fecha_desde: sql += " AND DATE(v.fecha) >= ?"; params.append(fecha_desde)
        if fecha_hasta: sql += " AND DATE(v.fecha) <= ?"; params.append(fecha_hasta)
        if solo_activas: sql += " AND v.anulada=0"
        sql += " ORDER BY v.fecha DESC"
        cur.execute(sql, params); rows = cur.fetchall(); conn.close()
        return [Venta(r[0],r[1],r[2],r[3],r[4],r[5],r[6]) for r in rows]

    def obtener_detalle_venta(self, id_venta):
        conn = conectar(); cur = conn.cursor()
        cur.execute("""SELECT id_producto,nombre_producto,precio_unitario,cantidad,subtotal
                       FROM detalle_ventas WHERE id_venta=?""", (id_venta,))
        rows = cur.fetchall(); conn.close()
        return [DetalleVenta(r[0],r[1],r[2],r[3]) for r in rows]

    def resumen_caja(self, fecha=None):
        conn = conectar(); cur = conn.cursor()
        if not fecha:
            from datetime import date
            fecha = str(date.today())
        cur.execute("""SELECT COUNT(*), COALESCE(SUM(total),0)
                       FROM ventas WHERE DATE(fecha)=? AND anulada=0""", (fecha,))
        r = cur.fetchone()
        cur.execute("""SELECT COUNT(*) FROM ventas WHERE DATE(fecha)=? AND anulada=1""", (fecha,))
        anuladas = cur.fetchone()[0]
        cur.execute("""SELECT p.nombre, SUM(d.cantidad) as cant
                       FROM detalle_ventas d
                       JOIN ventas v ON d.id_venta=v.id_venta
                       LEFT JOIN productos p ON d.id_producto=p.id_producto
                       WHERE DATE(v.fecha)=? AND v.anulada=0
                       GROUP BY d.id_producto ORDER BY cant DESC LIMIT 5""", (fecha,))
        top = cur.fetchall()
        conn.close()
        return {"fecha": fecha, "cantidad_ventas": r[0], "total": r[1],
                "anuladas": anuladas, "top_productos": top}

    def estadisticas_ventas(self, dias=30):
        conn = conectar(); cur = conn.cursor()
        cur.execute("""SELECT DATE(fecha) as dia, COALESCE(SUM(total),0)
                       FROM ventas WHERE anulada=0 AND fecha >= date('now',?)
                       GROUP BY dia ORDER BY dia""", (f"-{dias} days",))
        rows = cur.fetchall(); conn.close()
        return rows

    def productos_mas_vendidos(self, limite=10):
        conn = conectar(); cur = conn.cursor()
        cur.execute("""SELECT d.nombre_producto, SUM(d.cantidad) as total_vendido
                       FROM detalle_ventas d JOIN ventas v ON d.id_venta=v.id_venta
                       WHERE v.anulada=0 GROUP BY d.id_producto
                       ORDER BY total_vendido DESC LIMIT ?""", (limite,))
        rows = cur.fetchall(); conn.close()
        return rows

    # ── MOVIMIENTOS DE STOCK ───────────────────────────────────
    def registrar_movimiento(self, id_producto, nombre_producto, tipo, cantidad, motivo, usuario="dueño"):
        if cantidad <= 0: raise ValueError("La cantidad debe ser mayor a 0.")
        conn = conectar(); cur = conn.cursor()
        if tipo == "entrada":
            cur.execute("UPDATE productos SET cantidad=cantidad+? WHERE id_producto=?", (cantidad,id_producto))
        elif tipo == "salida":
            cur.execute("SELECT cantidad FROM productos WHERE id_producto=?", (id_producto,))
            actual = cur.fetchone()[0]
            if actual < cantidad: conn.close(); raise ValueError(f"Stock insuficiente. Disponible: {actual}")
            cur.execute("UPDATE productos SET cantidad=cantidad-? WHERE id_producto=?", (cantidad,id_producto))
        cur.execute("""INSERT INTO movimientos_stock (id_producto,nombre_producto,tipo,cantidad,motivo,usuario)
                       VALUES (?,?,?,?,?,?)""", (id_producto,nombre_producto,tipo,cantidad,motivo,usuario))
        conn.commit(); conn.close()

    def obtener_movimientos(self, id_producto=None, limite=100):
        conn = conectar(); cur = conn.cursor()
        if id_producto:
            cur.execute("""SELECT fecha,tipo,cantidad,motivo,usuario FROM movimientos_stock
                           WHERE id_producto=? ORDER BY fecha DESC LIMIT ?""", (id_producto,limite))
        else:
            cur.execute("""SELECT fecha,nombre_producto,tipo,cantidad,motivo,usuario
                           FROM movimientos_stock ORDER BY fecha DESC LIMIT ?""", (limite,))
        rows = cur.fetchall(); conn.close()
        return rows

    # ── USUARIOS ───────────────────────────────────────────────
    def verificar_usuario(self, nombre, password):
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        conn = conectar(); cur = conn.cursor()
        cur.execute("SELECT id_usuario,nombre,rol FROM usuarios WHERE nombre=? AND password_hash=?",
                    (nombre, pwd_hash))
        row = cur.fetchone(); conn.close()
        return row  # (id, nombre, rol) o None

    def obtener_usuarios(self):
        conn = conectar(); cur = conn.cursor()
        cur.execute("SELECT id_usuario,nombre,rol FROM usuarios ORDER BY nombre")
        rows = cur.fetchall(); conn.close()
        return rows

    def agregar_usuario(self, nombre, password, rol="empleado"):
        if not nombre.strip(): raise ValueError("El nombre de usuario es obligatorio.")
        if not password: raise ValueError("La contraseña es obligatoria.")
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        conn = conectar(); cur = conn.cursor()
        try:
            cur.execute("INSERT INTO usuarios (nombre,password_hash,rol) VALUES (?,?,?)",
                        (nombre.strip(), pwd_hash, rol))
            conn.commit()
        except Exception:
            conn.close(); raise ValueError(f"El usuario '{nombre}' ya existe.")
        conn.close()

    def cambiar_password(self, id_usuario, nueva_password):
        pwd_hash = hashlib.sha256(nueva_password.encode()).hexdigest()
        conn = conectar(); cur = conn.cursor()
        cur.execute("UPDATE usuarios SET password_hash=? WHERE id_usuario=?", (pwd_hash,id_usuario))
        conn.commit(); conn.close()

    def eliminar_usuario(self, id_usuario):
        conn = conectar(); cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM usuarios WHERE rol='dueño'")
        if cur.fetchone()[0] <= 1:
            cur.execute("SELECT rol FROM usuarios WHERE id_usuario=?", (id_usuario,))
            if cur.fetchone()[0] == 'dueño':
                conn.close(); raise ValueError("No se puede eliminar el único usuario dueño.")
        cur.execute("DELETE FROM usuarios WHERE id_usuario=?", (id_usuario,))
        conn.commit(); conn.close()

    # ── ESTADÍSTICAS GENERALES ─────────────────────────────────
    def estadisticas_generales(self):
        conn = conectar(); cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM productos"); tp = cur.fetchone()[0]
        cur.execute("SELECT COALESCE(SUM(cantidad),0) FROM productos"); tu = cur.fetchone()[0]
        cur.execute("SELECT COALESCE(SUM(precio*cantidad),0) FROM productos"); vt = cur.fetchone()[0]
        conn.close()
        return {"total_productos": tp, "total_unidades": tu, "valor_total": vt,
                "productos_stock_bajo": len(self.productos_stock_bajo())}

    # ── ÓRDENES DE COMPRA A PROVEEDORES ────────────────────────
    def generar_orden_automatica(self, id_proveedor=None, usuario="dueño"):
        """Genera una orden de compra con todos los productos en stock bajo
        (opcionalmente filtrados por proveedor)."""
        productos = self.productos_stock_bajo()
        if id_proveedor:
            productos = [p for p in productos if p.id_proveedor == id_proveedor]
        if not productos:
            raise ValueError("No hay productos con stock bajo para generar la orden.")
        detalles = []
        for p in productos:
            cantidad_sugerida = max(p.stock_minimo * 2 - p.cantidad, p.stock_minimo)
            detalles.append(DetalleOrdenCompra(
                id_producto=p.id_producto, nombre_producto=p.nombre,
                cantidad_pedida=cantidad_sugerida))
        # Si no se especificó proveedor, agrupar por proveedor más frecuente
        if not id_proveedor and productos:
            from collections import Counter
            cnt = Counter(p.id_proveedor for p in productos if p.id_proveedor)
            id_proveedor = cnt.most_common(1)[0][0] if cnt else None
        return self.crear_orden_compra(id_proveedor, detalles, usuario,
                                        notas="Generada automáticamente por stock bajo")

    def crear_orden_compra(self, id_proveedor, detalles: list, usuario="dueño", notas=""):
        if not detalles:
            raise ValueError("La orden de compra no tiene productos.")
        conn = conectar(); cur = conn.cursor()
        cur.execute("INSERT INTO ordenes_compra (id_proveedor,usuario,notas) VALUES (?,?,?)",
                    (id_proveedor, usuario, notas))
        id_orden = cur.lastrowid
        for d in detalles:
            cur.execute("""INSERT INTO detalle_orden_compra
                           (id_orden,id_producto,nombre_producto,cantidad_pedida)
                           VALUES (?,?,?,?)""",
                        (id_orden, d.id_producto, d.nombre_producto, d.cantidad_pedida))
        conn.commit(); conn.close()
        return id_orden

    def obtener_ordenes_compra(self, estado=None):
        conn = conectar(); cur = conn.cursor()
        sql = """SELECT o.id_orden,o.id_proveedor,COALESCE(p.nombre,'Sin proveedor'),
                        o.fecha,o.estado,o.usuario,o.notas
                 FROM ordenes_compra o LEFT JOIN proveedores p ON o.id_proveedor=p.id_proveedor
                 WHERE 1=1"""
        params = []
        if estado:
            sql += " AND o.estado=?"; params.append(estado)
        sql += " ORDER BY o.fecha DESC"
        cur.execute(sql, params); rows = cur.fetchall(); conn.close()
        return [OrdenCompra(r[0],r[1],r[2],r[3],r[4],r[5],r[6]) for r in rows]

    def obtener_detalle_orden(self, id_orden):
        conn = conectar(); cur = conn.cursor()
        cur.execute("""SELECT id_detalle,id_producto,nombre_producto,cantidad_pedida,cantidad_recibida
                       FROM detalle_orden_compra WHERE id_orden=?""", (id_orden,))
        rows = cur.fetchall(); conn.close()
        return [DetalleOrdenCompra(r[0],r[1],r[2],r[3],r[4]) for r in rows]

    def marcar_orden_recibida(self, id_orden, actualizar_stock=True, usuario="dueño"):
        """Marca la orden como recibida y, si corresponde, suma el stock recibido."""
        conn = conectar(); cur = conn.cursor()
        cur.execute("SELECT estado FROM ordenes_compra WHERE id_orden=?", (id_orden,))
        row = cur.fetchone()
        if not row: conn.close(); raise ValueError("Orden no encontrada.")
        if row[0] == "recibida": conn.close(); raise ValueError("La orden ya fue marcada como recibida.")

        detalles = self.obtener_detalle_orden(id_orden)
        for d in detalles:
            cantidad_a_sumar = d.cantidad_pedida - d.cantidad_recibida
            if cantidad_a_sumar > 0:
                cur.execute("UPDATE detalle_orden_compra SET cantidad_recibida=cantidad_pedida WHERE id_detalle=?",
                            (d.id_detalle,))
                if actualizar_stock and d.id_producto:
                    cur.execute("UPDATE productos SET cantidad=cantidad+? WHERE id_producto=?",
                                (cantidad_a_sumar, d.id_producto))
                    cur.execute("""INSERT INTO movimientos_stock
                                   (id_producto,nombre_producto,tipo,cantidad,motivo,usuario)
                                   VALUES (?,?,'entrada',?,?,?)""",
                                (d.id_producto, d.nombre_producto, cantidad_a_sumar,
                                 f"Recepción orden de compra #{id_orden}", usuario))
        cur.execute("UPDATE ordenes_compra SET estado='recibida' WHERE id_orden=?", (id_orden,))
        conn.commit(); conn.close()

    def cancelar_orden_compra(self, id_orden):
        conn = conectar(); cur = conn.cursor()
        cur.execute("UPDATE ordenes_compra SET estado='cancelada' WHERE id_orden=?", (id_orden,))
        conn.commit(); conn.close()

    # ── COMPROBANTES DE COMPRA (PDF/FOTO) ──────────────────────
    def agregar_comprobante(self, comprobante: Comprobante):
        if not comprobante.archivo_ruta:
            raise ValueError("Debe adjuntar un archivo de comprobante.")
        conn = conectar(); cur = conn.cursor()
        cur.execute("""INSERT INTO comprobantes_compra
                       (id_proveedor,id_orden,numero_comprobante,monto,archivo_nombre,archivo_ruta,notas,usuario)
                       VALUES (?,?,?,?,?,?,?,?)""",
                    (comprobante.id_proveedor, comprobante.id_orden, comprobante.numero_comprobante,
                     comprobante.monto, comprobante.archivo_nombre, comprobante.archivo_ruta,
                     comprobante.notas, comprobante.usuario))
        conn.commit(); conn.close()

    def obtener_comprobantes(self, id_proveedor=None):
        conn = conectar(); cur = conn.cursor()
        sql = """SELECT c.id_comprobante,c.id_proveedor,COALESCE(p.nombre,'Sin proveedor'),
                        c.id_orden,c.fecha,c.numero_comprobante,c.monto,
                        c.archivo_nombre,c.archivo_ruta,c.notas,c.usuario
                 FROM comprobantes_compra c LEFT JOIN proveedores p ON c.id_proveedor=p.id_proveedor
                 WHERE 1=1"""
        params = []
        if id_proveedor:
            sql += " AND c.id_proveedor=?"; params.append(id_proveedor)
        sql += " ORDER BY c.fecha DESC"
        cur.execute(sql, params); rows = cur.fetchall(); conn.close()
        return [Comprobante(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9],r[10]) for r in rows]

    def eliminar_comprobante(self, id_comprobante):
        conn = conectar(); cur = conn.cursor()
        cur.execute("SELECT archivo_ruta FROM comprobantes_compra WHERE id_comprobante=?", (id_comprobante,))
        row = cur.fetchone()
        cur.execute("DELETE FROM comprobantes_compra WHERE id_comprobante=?", (id_comprobante,))
        conn.commit(); conn.close()
        return row[0] if row else None

    # ── VENTAS CON FORMA DE PAGO Y DESCUENTO ──────────────────
    def registrar_venta(self, detalles: list, id_cliente=None, usuario="dueño",
                        forma_pago="efectivo", descuento=0.0):
        if not detalles: raise ValueError("La venta no tiene productos.")
        subtotal = sum(d.subtotal for d in detalles)
        total = round(subtotal * (1 - descuento / 100), 2)
        conn = conectar(); cur = conn.cursor()
        cur.execute("""INSERT INTO ventas (total,id_cliente,usuario,forma_pago,descuento)
                       VALUES (?,?,?,?,?)""",
                    (total, id_cliente, usuario, forma_pago, descuento))
        id_venta = cur.lastrowid
        for d in detalles:
            cur.execute("""INSERT INTO detalle_ventas (id_venta,id_producto,nombre_producto,
                           precio_unitario,cantidad,subtotal) VALUES (?,?,?,?,?,?)""",
                        (id_venta,d.id_producto,d.nombre_producto,d.precio_unitario,d.cantidad,d.subtotal))
            if d.id_producto:
                cur.execute("UPDATE productos SET cantidad=cantidad-? WHERE id_producto=?",
                            (d.cantidad, d.id_producto))
                cur.execute("""INSERT INTO movimientos_stock (id_producto,nombre_producto,tipo,cantidad,motivo,usuario)
                               VALUES (?,?,'salida',?,?,?)""",
                            (d.id_producto,d.nombre_producto,d.cantidad,f"Venta #{id_venta}",usuario))
        # Si es fiado, generar cargo en cuenta corriente
        if id_cliente and forma_pago == "cuenta_corriente":
            cur.execute("""INSERT INTO cuenta_corriente (id_cliente,tipo,monto,descripcion,id_venta,usuario)
                           VALUES (?,'cargo',?,?,?,?)""",
                        (id_cliente, total, f"Venta #{id_venta}", id_venta, usuario))
        conn.commit(); conn.close()
        return id_venta

    def resumen_caja(self, fecha=None):
        conn = conectar(); cur = conn.cursor()
        if not fecha:
            from datetime import date; fecha = str(date.today())
        cur.execute("""SELECT COUNT(*), COALESCE(SUM(total),0)
                       FROM ventas WHERE DATE(fecha)=? AND anulada=0""", (fecha,))
        r = cur.fetchone()
        cur.execute("SELECT COUNT(*) FROM ventas WHERE DATE(fecha)=? AND anulada=1", (fecha,))
        anuladas = cur.fetchone()[0]
        # Por forma de pago
        cur.execute("""SELECT forma_pago, COALESCE(SUM(total),0)
                       FROM ventas WHERE DATE(fecha)=? AND anulada=0
                       GROUP BY forma_pago""", (fecha,))
        por_forma = {row[0]: row[1] for row in cur.fetchall()}
        # Top productos
        cur.execute("""SELECT p.nombre, SUM(d.cantidad)
                       FROM detalle_ventas d JOIN ventas v ON d.id_venta=v.id_venta
                       LEFT JOIN productos p ON d.id_producto=p.id_producto
                       WHERE DATE(v.fecha)=? AND v.anulada=0
                       GROUP BY d.id_producto ORDER BY SUM(d.cantidad) DESC LIMIT 5""", (fecha,))
        top = cur.fetchall()
        conn.close()
        return {"fecha": fecha, "cantidad_ventas": r[0], "total": r[1],
                "anuladas": anuladas, "top_productos": top, "por_forma_pago": por_forma}

    # ── DEVOLUCIONES ───────────────────────────────────────────
    def registrar_devolucion(self, id_venta, id_producto, nombre_producto,
                              cantidad, precio_unitario, motivo="", usuario="dueño"):
        if cantidad <= 0: raise ValueError("La cantidad debe ser mayor a 0.")
        conn = conectar(); cur = conn.cursor()
        cur.execute("SELECT anulada FROM ventas WHERE id_venta=?", (id_venta,))
        row = cur.fetchone()
        if not row: conn.close(); raise ValueError("Venta no encontrada.")
        if row[0]: conn.close(); raise ValueError("No se puede devolver una venta anulada.")
        cur.execute("""INSERT INTO devoluciones
                       (id_venta,id_producto,nombre_producto,cantidad,precio_unitario,motivo,usuario)
                       VALUES (?,?,?,?,?,?,?)""",
                    (id_venta,id_producto,nombre_producto,cantidad,precio_unitario,motivo,usuario))
        if id_producto:
            cur.execute("UPDATE productos SET cantidad=cantidad+? WHERE id_producto=?",
                        (cantidad, id_producto))
            cur.execute("""INSERT INTO movimientos_stock (id_producto,nombre_producto,tipo,cantidad,motivo,usuario)
                           VALUES (?,?,'entrada',?,?,?)""",
                        (id_producto,nombre_producto,cantidad,f"Devolución venta #{id_venta}",usuario))
        conn.commit(); conn.close()

    def obtener_devoluciones(self, id_venta=None):
        conn = conectar(); cur = conn.cursor()
        if id_venta:
            cur.execute("""SELECT id_devolucion,id_venta,id_producto,nombre_producto,
                           cantidad,precio_unitario,motivo,fecha,usuario
                           FROM devoluciones WHERE id_venta=? ORDER BY fecha DESC""", (id_venta,))
        else:
            cur.execute("""SELECT id_devolucion,id_venta,id_producto,nombre_producto,
                           cantidad,precio_unitario,motivo,fecha,usuario
                           FROM devoluciones ORDER BY fecha DESC LIMIT 100""")
        rows = cur.fetchall(); conn.close()
        return [Devolucion(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8]) for r in rows]

    # ── CUENTA CORRIENTE DE CLIENTES ───────────────────────────
    def obtener_saldo_cliente(self, id_cliente):
        conn = conectar(); cur = conn.cursor()
        cur.execute("""SELECT COALESCE(SUM(CASE WHEN tipo='cargo' THEN monto ELSE -monto END),0)
                       FROM cuenta_corriente WHERE id_cliente=?""", (id_cliente,))
        saldo = cur.fetchone()[0]; conn.close()
        return saldo

    def obtener_cuenta_corriente(self, id_cliente):
        conn = conectar(); cur = conn.cursor()
        cur.execute("""SELECT id_movimiento,tipo,monto,descripcion,id_venta,fecha,usuario
                       FROM cuenta_corriente WHERE id_cliente=? ORDER BY fecha DESC""", (id_cliente,))
        rows = cur.fetchall(); conn.close()
        return [MovimientoCuentaCorriente(r[0],id_cliente,r[1],r[2],r[3],r[4],r[5],r[6]) for r in rows]

    def registrar_pago_cuenta(self, id_cliente, monto, descripcion="Pago en efectivo", usuario="dueño"):
        if monto <= 0: raise ValueError("El monto del pago debe ser mayor a 0.")
        saldo = self.obtener_saldo_cliente(id_cliente)
        if monto > saldo + 0.01:
            raise ValueError(f"El pago (${monto:,.2f}) supera la deuda actual (${saldo:,.2f}).")
        conn = conectar(); cur = conn.cursor()
        cur.execute("""INSERT INTO cuenta_corriente (id_cliente,tipo,monto,descripcion,usuario)
                       VALUES (?,'pago',?,?,?)""", (id_cliente, monto, descripcion, usuario))
        conn.commit(); conn.close()

    def clientes_con_deuda(self):
        conn = conectar(); cur = conn.cursor()
        cur.execute("""SELECT cc.id_cliente, c.nombre,
                       SUM(CASE WHEN cc.tipo='cargo' THEN cc.monto ELSE -cc.monto END) as saldo
                       FROM cuenta_corriente cc
                       JOIN clientes c ON cc.id_cliente=c.id_cliente
                       GROUP BY cc.id_cliente HAVING saldo > 0.01
                       ORDER BY saldo DESC""")
        rows = cur.fetchall(); conn.close()
        return rows  # (id_cliente, nombre, saldo)

    # ── OFERTAS Y DESCUENTOS ───────────────────────────────────
    def agregar_oferta(self, oferta: Oferta):
        conn = conectar(); cur = conn.cursor()
        cur.execute("""INSERT INTO ofertas (id_producto,nombre_oferta,tipo,valor,
                       cantidad_minima,fecha_desde,fecha_hasta,activa)
                       VALUES (?,?,?,?,?,?,?,?)""",
                    (oferta.id_producto,oferta.nombre_oferta,oferta.tipo,oferta.valor,
                     oferta.cantidad_minima,oferta.fecha_desde,oferta.fecha_hasta,1))
        conn.commit(); conn.close()

    def obtener_ofertas(self, solo_activas=True):
        from datetime import date; hoy = str(date.today())
        conn = conectar(); cur = conn.cursor()
        sql = """SELECT o.id_oferta,o.id_producto,p.nombre,o.nombre_oferta,o.tipo,
                        o.valor,o.cantidad_minima,o.fecha_desde,o.fecha_hasta,o.activa
                 FROM ofertas o JOIN productos p ON o.id_producto=p.id_producto
                 WHERE 1=1"""
        if solo_activas:
            sql += f" AND o.activa=1 AND (o.fecha_hasta IS NULL OR o.fecha_hasta >= '{hoy}')"
        sql += " ORDER BY p.nombre"
        cur.execute(sql); rows = cur.fetchall(); conn.close()
        return [Oferta(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9]) for r in rows]

    def obtener_oferta_producto(self, id_producto, cantidad=1):
        """Devuelve la mejor oferta activa para un producto y cantidad dada."""
        ofertas = self.obtener_ofertas(solo_activas=True)
        ofertas_prod = [o for o in ofertas if o.id_producto == id_producto and cantidad >= o.cantidad_minima]
        return max(ofertas_prod, key=lambda o: o.valor, default=None)

    def desactivar_oferta(self, id_oferta):
        conn = conectar(); cur = conn.cursor()
        cur.execute("UPDATE ofertas SET activa=0 WHERE id_oferta=?", (id_oferta,))
        conn.commit(); conn.close()

    def eliminar_oferta(self, id_oferta):
        conn = conectar(); cur = conn.cursor()
        cur.execute("DELETE FROM ofertas WHERE id_oferta=?", (id_oferta,))
        conn.commit(); conn.close()

    # ── GANANCIAS / RENTABILIDAD ───────────────────────────────
    def reporte_ganancias(self, fecha_desde=None, fecha_hasta=None):
        from datetime import date
        if not fecha_desde: fecha_desde = str(date.today().replace(day=1))
        if not fecha_hasta: fecha_hasta = str(date.today())
        conn = conectar(); cur = conn.cursor()
        cur.execute("""SELECT d.nombre_producto, SUM(d.cantidad) as unidades,
                       SUM(d.subtotal) as ingresos,
                       COALESCE(p.precio_costo,0) as costo_unitario,
                       SUM(d.cantidad) * COALESCE(p.precio_costo,0) as costo_total
                       FROM detalle_ventas d
                       JOIN ventas v ON d.id_venta=v.id_venta
                       LEFT JOIN productos p ON d.id_producto=p.id_producto
                       WHERE v.anulada=0 AND DATE(v.fecha) BETWEEN ? AND ?
                       GROUP BY d.id_producto ORDER BY ingresos DESC""",
                    (fecha_desde, fecha_hasta))
        rows = cur.fetchall()
        cur.execute("""SELECT COALESCE(SUM(total),0) FROM ventas
                       WHERE anulada=0 AND DATE(fecha) BETWEEN ? AND ?""",
                    (fecha_desde, fecha_hasta))
        total_ingresos = cur.fetchone()[0]
        conn.close()
        resultados = []
        total_costo = 0
        for r in rows:
            nombre, unidades, ingresos, costo_unit, costo_total = r
            ganancia = ingresos - costo_total
            margen = (ganancia / ingresos * 100) if ingresos > 0 else 0
            resultados.append({
                "nombre": nombre, "unidades": unidades, "ingresos": ingresos,
                "costo_total": costo_total, "ganancia": ganancia, "margen": margen
            })
            total_costo += costo_total
        return {
            "detalle": resultados,
            "total_ingresos": total_ingresos,
            "total_costo": total_costo,
            "ganancia_total": total_ingresos - total_costo,
            "fecha_desde": fecha_desde, "fecha_hasta": fecha_hasta
        }

    def estadisticas_ventas_comparativa(self, mes_actual=None, mes_anterior=None):
        from datetime import date
        hoy = date.today()
        if not mes_actual:
            desde = hoy.replace(day=1)
            hasta = hoy
        else:
            desde, hasta = mes_actual
        # Mes anterior
        primer_dia_actual = hoy.replace(day=1)
        if primer_dia_actual.month == 1:
            primer_dia_ant = primer_dia_actual.replace(year=primer_dia_actual.year-1, month=12)
        else:
            primer_dia_ant = primer_dia_actual.replace(month=primer_dia_actual.month-1)
        conn = conectar(); cur = conn.cursor()
        cur.execute("""SELECT COALESCE(SUM(total),0), COUNT(*) FROM ventas
                       WHERE anulada=0 AND DATE(fecha) BETWEEN ? AND ?""",
                    (str(desde), str(hasta)))
        r_actual = cur.fetchone()
        cur.execute("""SELECT COALESCE(SUM(total),0), COUNT(*) FROM ventas
                       WHERE anulada=0 AND DATE(fecha) BETWEEN ? AND ?""",
                    (str(primer_dia_ant), str(primer_dia_actual)))
        r_anterior = cur.fetchone()
        conn.close()
        return {
            "actual": {"total": r_actual[0], "ventas": r_actual[1], "periodo": f"{desde} a {hasta}"},
            "anterior": {"total": r_anterior[0], "ventas": r_anterior[1], "periodo": f"{primer_dia_ant} a {primer_dia_actual}"},
            "variacion_pct": ((r_actual[0] - r_anterior[0]) / r_anterior[0] * 100) if r_anterior[0] > 0 else 0
        }

    # ── VENCIMIENTOS ───────────────────────────────────────────
    def productos_proximos_vencer(self, dias=30):
        from datetime import date, timedelta
        hoy = date.today()
        limite = str(hoy + timedelta(days=dias))
        hoy_str = str(hoy)
        conn = conectar(); cur = conn.cursor()
        cur.execute("""SELECT p.id_producto,p.codigo,p.nombre,p.fecha_vencimiento,p.cantidad,
                       COALESCE(c.nombre,''),COALESCE(pr.nombre,'')
                       FROM productos p
                       LEFT JOIN categorias c ON p.id_categoria=c.id_categoria
                       LEFT JOIN proveedores pr ON p.id_proveedor=pr.id_proveedor
                       WHERE p.fecha_vencimiento IS NOT NULL AND p.fecha_vencimiento != ''
                       AND p.fecha_vencimiento <= ? ORDER BY p.fecha_vencimiento ASC""",
                    (limite,))
        rows = cur.fetchall(); conn.close()
        resultado = []
        for r in rows:
            from datetime import datetime
            try:
                fv = datetime.strptime(r[3], "%Y-%m-%d").date()
                dias_restantes = (fv - hoy).days
            except:
                dias_restantes = None
            resultado.append({
                "id_producto": r[0], "codigo": r[1], "nombre": r[2],
                "fecha_vencimiento": r[3], "cantidad": r[4],
                "categoria": r[5], "proveedor": r[6],
                "dias_restantes": dias_restantes,
                "vencido": dias_restantes is not None and dias_restantes < 0
            })
        return resultado
