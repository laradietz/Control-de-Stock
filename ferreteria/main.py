"""
main.py - Ventana principal del Sistema de Control de Stock - Ferretería Gian.
Incluye todas las funcionalidades: ventas, caja, clientes, estadísticas,
movimientos, usuarios, backup, actualización de precios y más.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import sys
import os

# Soporte para PyInstaller: cuando corre como .exe, los archivos
# están junto al ejecutable, no en el directorio temporal interno.
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Apuntar la base de datos y exports a la carpeta del ejecutable
os.environ["FERRETERIA_BASE_DIR"] = BASE_DIR

from database import inicializar_db
from inventario import Inventario
from backup import hacer_backup

from ventana_login import VentanaLogin
from ventana_producto import VentanaProducto
from ventana_proveedores import VentanaProveedores
from ventana_categorias import VentanaCategorias
from ventana_reportes import VentanaReportes
from ventana_ventas import VentanaVentas
from ventana_historial_ventas import VentanaHistorialVentas
from ventana_caja import VentanaCaja
from ventana_clientes import VentanaClientes
from ventana_estadisticas import VentanaEstadisticas
from ventana_movimientos import VentanaMovimientos
from ventana_usuarios import VentanaUsuarios
from ventana_backup import VentanaBackup
from ventana_precios import VentanaActualizarPrecios
from ventana_ordenes_compra import VentanaOrdenesCompra
from ventana_comprobantes import VentanaComprobantes
from ventana_cuenta_corriente import VentanaCuentaCorriente
from ventana_devoluciones import VentanaDevoluciones
from ventana_ofertas import VentanaOfertas
from ventana_ganancias import VentanaGanancias
from ventana_vencimientos import VentanaVencimientos
from ventana_comparativa import VentanaComparativa
from exportador import exportar_excel, exportar_pdf

COLOR_PRIMARIO = "#2F5496"
COLOR_FONDO = "#F4F6F7"
COLOR_ALERTA = "#FFC7CE"
COLOR_SECUNDARIO = "#1A3A6B"


class AplicacionFerreteria(tk.Tk):
    def __init__(self, usuario):
        super().__init__()
        self.inventario = Inventario()
        self.usuario = usuario  # dict: {id, nombre, rol}

        self.title(f"Ferretería Gian — Control de Stock  |  Usuario: {usuario['nombre']}")
        self.geometry("1150x680")
        self.configure(bg=COLOR_FONDO)
        self.minsize(1000, 580)

        # Backup automático al iniciar
        try:
            hacer_backup()
        except Exception:
            pass

        self._construir_interfaz()
        self._refrescar_tabla()
        self._mostrar_alertas_stock()
        self._mostrar_alertas_vencimiento()

    # ─────────────────────────────────────────────────────────────
    # CONSTRUCCIÓN DE INTERFAZ
    # ─────────────────────────────────────────────────────────────
    def _construir_interfaz(self):
        self._construir_encabezado()
        self._construir_menu_lateral()
        self._construir_area_principal()
        self._construir_barra_estado()

    def _construir_encabezado(self):
        frame = tk.Frame(self, bg=COLOR_PRIMARIO, height=56)
        frame.pack(fill="x")
        frame.pack_propagate(False)
        tk.Label(frame, text="🔧  Ferretería Gian — Sistema de Control de Stock",
                 bg=COLOR_PRIMARIO, fg="white",
                 font=("Segoe UI", 15, "bold")).pack(side="left", padx=20, pady=12)
        tk.Label(frame, text=f"👤 {self.usuario['nombre']}  ({self.usuario['rol']})",
                 bg=COLOR_PRIMARIO, fg="#BDD7EE",
                 font=("Segoe UI", 10)).pack(side="right", padx=20)

    def _construir_menu_lateral(self):
        self.sidebar = tk.Frame(self, bg=COLOR_SECUNDARIO, width=190)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="MENÚ PRINCIPAL", bg=COLOR_SECUNDARIO,
                 fg="#BDD7EE", font=("Segoe UI", 8, "bold")).pack(pady=(15, 5), padx=10, anchor="w")

        secciones = [
            ("─── VENTAS ───", None, None),
            ("🛒  Nueva Venta", "#27AE60", self._nueva_venta),
            ("📋  Historial de Ventas", COLOR_SECUNDARIO, self._historial_ventas),
            ("💰  Caja del Día", COLOR_SECUNDARIO, self._abrir_caja),
            ("🔄  Devoluciones", COLOR_SECUNDARIO, self._abrir_devoluciones),
            ("💳  Cuenta Corriente", COLOR_SECUNDARIO, self._abrir_cuenta_corriente),
            ("", None, None),
            ("─── INVENTARIO ───", None, None),
            ("➕  Nuevo Producto", COLOR_SECUNDARIO, self._nuevo_producto),
            ("📦  Movimientos Stock", COLOR_SECUNDARIO, self._abrir_movimientos),
            ("🏷  Actualizar Precios", COLOR_SECUNDARIO, self._actualizar_precios),
            ("🎁  Ofertas y Descuentos", COLOR_SECUNDARIO, self._abrir_ofertas),
            ("📅  Vencimientos", COLOR_SECUNDARIO, self._abrir_vencimientos),
            ("", None, None),
            ("─── COMPRAS ───", None, None),
            ("📝  Pedidos a Proveedores", COLOR_SECUNDARIO, self._abrir_ordenes_compra),
            ("🧾  Comprobantes de Compra", COLOR_SECUNDARIO, self._abrir_comprobantes),
            ("", None, None),
            ("─── MAESTROS ───", None, None),
            ("👥  Clientes", COLOR_SECUNDARIO, self._abrir_clientes),
            ("🚚  Proveedores", COLOR_SECUNDARIO, self._abrir_proveedores),
            ("🗂  Categorías", COLOR_SECUNDARIO, self._abrir_categorias),
            ("", None, None),
            ("─── REPORTES ───", None, None),
            ("📊  Estadísticas", COLOR_SECUNDARIO, self._abrir_estadisticas),
            ("📈  Ganancias", COLOR_SECUNDARIO, self._abrir_ganancias),
            ("🔁  Comparativa", COLOR_SECUNDARIO, self._abrir_comparativa),
            ("📋  Reporte de Stock", COLOR_SECUNDARIO, self._abrir_reportes),
            ("📥  Exportar Excel", COLOR_SECUNDARIO, self._exportar_excel),
            ("📄  Exportar PDF", COLOR_SECUNDARIO, self._exportar_pdf),
            ("", None, None),
            ("─── SISTEMA ───", None, None),
            ("🔐  Usuarios", COLOR_SECUNDARIO, self._abrir_usuarios),
            ("💾  Backup", COLOR_SECUNDARIO, self._abrir_backup),
        ]

        for texto, color, cmd in secciones:
            if not texto:
                tk.Frame(self.sidebar, bg=COLOR_SECUNDARIO, height=6).pack(fill="x")
                continue
            if cmd is None:
                tk.Label(self.sidebar, text=texto, bg=COLOR_SECUNDARIO,
                         fg="#7FB3D3", font=("Segoe UI", 8, "bold")).pack(
                    pady=(6, 2), padx=10, anchor="w")
                continue
            btn = tk.Button(self.sidebar, text=texto, bg=color, fg="white",
                            font=("Segoe UI", 9), relief="flat", anchor="w",
                            padx=12, cursor="hand2", command=cmd,
                            activebackground="#2F5496", activeforeground="white")
            btn.pack(fill="x", padx=6, pady=1, ipady=4)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#2F5496") if b["bg"] != "#27AE60" else None)
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c) if c != "#27AE60" else None)

    def _construir_area_principal(self):
        self.area = tk.Frame(self, bg=COLOR_FONDO)
        self.area.pack(side="left", fill="both", expand=True)

        self._construir_barra_busqueda()
        self._construir_barra_acciones()
        self._construir_tabla()

    def _construir_barra_busqueda(self):
        frame = tk.Frame(self.area, bg=COLOR_FONDO)
        frame.pack(fill="x", padx=15, pady=(10, 4))

        tk.Label(frame, text="🔍 Buscar:", bg=COLOR_FONDO,
                 font=("Segoe UI", 10)).pack(side="left")
        self.var_busqueda = tk.StringVar()
        self.var_busqueda.trace_add("write", lambda *a: self._refrescar_tabla())
        tk.Entry(frame, textvariable=self.var_busqueda,
                 font=("Segoe UI", 10), width=28).pack(side="left", padx=6)

        tk.Label(frame, text="Categoría:", bg=COLOR_FONDO,
                 font=("Segoe UI", 10)).pack(side="left", padx=(12, 0))
        self.combo_cat = ttk.Combobox(frame, state="readonly", font=("Segoe UI", 10), width=18)
        self.combo_cat.pack(side="left", padx=6)
        self.combo_cat.bind("<<ComboboxSelected>>", lambda e: self._refrescar_tabla())

        tk.Label(frame, text="Proveedor:", bg=COLOR_FONDO,
                 font=("Segoe UI", 10)).pack(side="left", padx=(12, 0))
        self.combo_prov = ttk.Combobox(frame, state="readonly", font=("Segoe UI", 10), width=20)
        self.combo_prov.pack(side="left", padx=6)
        self.combo_prov.bind("<<ComboboxSelected>>", lambda e: self._refrescar_tabla())

        tk.Button(frame, text="✖ Limpiar", bg="#AAAAAA", fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  command=self._limpiar_filtros).pack(side="left", padx=6)
        tk.Button(frame, text="⚠ Solo stock bajo", bg="#C0392B", fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  command=self._mostrar_stock_bajo).pack(side="left")

    def _construir_barra_acciones(self):
        frame = tk.Frame(self.area, bg="#E8EEF7")
        frame.pack(fill="x", padx=15, pady=2)

        acciones = [
            ("➕ Nuevo", "#27AE60", self._nuevo_producto),
            ("✏ Modificar", COLOR_PRIMARIO, self._modificar_producto),
            ("🗑 Eliminar", "#C0392B", self._eliminar_producto),
            ("📦 Movimiento", "#8E44AD", self._abrir_movimientos),
            ("🏷 Precios proveedor", "#D68910", self._actualizar_precios),
        ]
        for texto, color, cmd in acciones:
            tk.Button(frame, text=texto, bg=color, fg="white",
                      font=("Segoe UI", 9, "bold"), relief="flat",
                      padx=10, pady=4, cursor="hand2",
                      command=cmd).pack(side="left", padx=3, pady=4)

    def _construir_tabla(self):
        frame = tk.Frame(self.area, bg=COLOR_FONDO)
        frame.pack(fill="both", expand=True, padx=15, pady=4)

        cols = ("codigo", "nombre", "categoria", "precio", "cantidad", "minimo", "proveedor")
        self.tabla = ttk.Treeview(frame, columns=cols, show="headings")

        config = [
            ("codigo", "Código", 90, "center"),
            ("nombre", "Nombre del Producto", 270, "w"),
            ("categoria", "Categoría", 140, "w"),
            ("precio", "Precio ($)", 100, "center"),
            ("cantidad", "Cantidad", 80, "center"),
            ("minimo", "Stock Mín.", 80, "center"),
            ("proveedor", "Proveedor", 160, "w"),
        ]
        for col, txt, w, anchor in config:
            self.tabla.heading(col, text=txt,
                               command=lambda c=col: self._ordenar_por(c))
            self.tabla.column(col, width=w, anchor=anchor)

        sc_y = ttk.Scrollbar(frame, orient="vertical", command=self.tabla.yview)
        sc_x = ttk.Scrollbar(frame, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=sc_y.set, xscrollcommand=sc_x.set)
        self.tabla.grid(row=0, column=0, sticky="nsew")
        sc_y.grid(row=0, column=1, sticky="ns")
        sc_x.grid(row=1, column=0, sticky="ew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        self.tabla.tag_configure("stock_bajo", background=COLOR_ALERTA)
        self.tabla.bind("<Double-1>", lambda e: self._modificar_producto())

        self._orden_col = None
        self._orden_asc = True

    def _construir_barra_estado(self):
        frame = tk.Frame(self, bg="#DDE3EE", height=28)
        frame.pack(fill="x", side="bottom")
        self.lbl_estado = tk.Label(frame, text="", bg="#DDE3EE",
                                    font=("Segoe UI", 9), anchor="w")
        self.lbl_estado.pack(side="left", padx=15, pady=4)
        self.lbl_valor = tk.Label(frame, text="", bg="#DDE3EE",
                                   font=("Segoe UI", 9, "bold"), anchor="e")
        self.lbl_valor.pack(side="right", padx=15, pady=4)

    # ─────────────────────────────────────────────────────────────
    # TABLA Y FILTROS
    # ─────────────────────────────────────────────────────────────
    def _refrescar_combos(self):
        self._cats = self.inventario.obtener_categorias()
        self._provs = self.inventario.obtener_proveedores()

        cat_actual = self.combo_cat.get()
        prov_actual = self.combo_prov.get()

        self.combo_cat["values"] = ["(Todas)"] + [c.nombre for c in self._cats]
        self.combo_prov["values"] = ["(Todos)"] + [p.nombre for p in self._provs]

        if cat_actual in self.combo_cat["values"]:
            self.combo_cat.set(cat_actual)
        else:
            self.combo_cat.current(0)

        if prov_actual in self.combo_prov["values"]:
            self.combo_prov.set(prov_actual)
        else:
            self.combo_prov.current(0)

    def _refrescar_tabla(self):
        self._refrescar_combos()

        texto = self.var_busqueda.get().strip()

        id_cat = None
        idx = self.combo_cat.current()
        if idx > 0:
            id_cat = self._cats[idx - 1].id_categoria

        id_prov = None
        idx = self.combo_prov.current()
        if idx > 0:
            id_prov = self._provs[idx - 1].id_proveedor

        productos = self.inventario.obtener_productos(
            filtro_texto=texto, id_categoria=id_cat, id_proveedor=id_prov)

        for row in self.tabla.get_children():
            self.tabla.delete(row)

        self._productos_actuales = productos
        for p in productos:
            tags = ("stock_bajo",) if p.stock_bajo() else ()
            self.tabla.insert("", "end", iid=p.id_producto, values=(
                p.codigo, p.nombre, p.categoria_nombre,
                f"${p.precio:,.2f}", p.cantidad, p.stock_minimo,
                p.proveedor_nombre), tags=tags)

        stats = self.inventario.estadisticas_generales()
        self.lbl_estado.config(
            text=f"Mostrando {len(productos)} de {stats['total_productos']} productos  "
                 f"|  ⚠ {stats['productos_stock_bajo']} con stock bajo  "
                 f"|  Hoy: {date.today().strftime('%d/%m/%Y')}")
        self.lbl_valor.config(
            text=f"Valor total del inventario: ${stats['valor_total']:,.2f}")

    def _limpiar_filtros(self):
        self.var_busqueda.set("")
        self.combo_cat.current(0)
        self.combo_prov.current(0)
        self._refrescar_tabla()

    def _mostrar_stock_bajo(self):
        for row in self.tabla.get_children():
            self.tabla.delete(row)
        productos = self.inventario.productos_stock_bajo()
        self._productos_actuales = productos
        for p in productos:
            self.tabla.insert("", "end", iid=p.id_producto, values=(
                p.codigo, p.nombre, p.categoria_nombre,
                f"${p.precio:,.2f}", p.cantidad, p.stock_minimo,
                p.proveedor_nombre), tags=("stock_bajo",))
        self.lbl_estado.config(
            text=f"⚠ Mostrando {len(productos)} producto(s) con stock bajo o igual al mínimo")

    def _ordenar_por(self, col):
        productos = self._productos_actuales[:]
        reverse = False
        if self._orden_col == col:
            reverse = not self._orden_asc
        self._orden_col = col
        self._orden_asc = not reverse

        indices = {"codigo": 0, "nombre": 1, "categoria": 2,
                   "precio": 3, "cantidad": 4, "minimo": 5, "proveedor": 6}
        attr = ["codigo", "nombre", "categoria_nombre", "precio",
                "cantidad", "stock_minimo", "proveedor_nombre"][indices[col]]
        productos.sort(key=lambda p: getattr(p, attr), reverse=reverse)

        for row in self.tabla.get_children():
            self.tabla.delete(row)
        self._productos_actuales = productos
        for p in productos:
            tags = ("stock_bajo",) if p.stock_bajo() else ()
            self.tabla.insert("", "end", iid=p.id_producto, values=(
                p.codigo, p.nombre, p.categoria_nombre,
                f"${p.precio:,.2f}", p.cantidad, p.stock_minimo,
                p.proveedor_nombre), tags=tags)

    def _get_producto_seleccionado(self):
        sel = self.tabla.selection()
        if not sel:
            return None
        return self.inventario.obtener_producto_por_id(int(sel[0]))

    def _mostrar_alertas_vencimiento(self):
        proximos = self.inventario.productos_proximos_vencer(dias=30)
        vencidos = [p for p in proximos if p["vencido"]]
        urgentes = [p for p in proximos if not p["vencido"] and p["dias_restantes"] is not None and p["dias_restantes"] <= 7]
        if vencidos or urgentes:
            lineas = []
            if vencidos:
                lineas.append(f"⛔ {len(vencidos)} producto(s) VENCIDO(S):")
                for p in vencidos[:3]:
                    lineas.append(f"  • {p['nombre']} ({p['fecha_vencimiento']})")
            if urgentes:
                lineas.append(f"⚠ {len(urgentes)} producto(s) vencen en menos de 7 días:")
                for p in urgentes[:3]:
                    lineas.append(f"  • {p['nombre']} — vence en {p['dias_restantes']} día(s)")
            messagebox.showwarning("⚠ Alerta de vencimientos",
                                    "\n".join(lineas) + "\n\nAndá a Inventario → Vencimientos para ver el detalle.")

    def _mostrar_alertas_stock(self):
        bajos = self.inventario.productos_stock_bajo()
        if bajos:
            messagebox.showwarning(
                "⚠ Alerta de stock bajo",
                f"Hay {len(bajos)} producto(s) con stock igual o menor al mínimo:\n\n" +
                "\n".join(f"• {p.nombre} (stock: {p.cantidad}, mín: {p.stock_minimo})"
                          for p in bajos[:8]) +
                ("\n..." if len(bajos) > 8 else "") +
                "\n\nAndá a Reportes → Reporte de Stock para ver el detalle completo.")

    # ─────────────────────────────────────────────────────────────
    # ACCIONES CRUD PRODUCTOS
    # ─────────────────────────────────────────────────────────────
    def _nuevo_producto(self):
        VentanaProducto(self, self.inventario, on_guardar=self._refrescar_tabla)

    def _modificar_producto(self):
        p = self._get_producto_seleccionado()
        if not p:
            messagebox.showwarning("Atención", "Seleccioná un producto de la tabla.")
            return
        VentanaProducto(self, self.inventario, on_guardar=self._refrescar_tabla, producto=p)

    def _eliminar_producto(self):
        p = self._get_producto_seleccionado()
        if not p:
            messagebox.showwarning("Atención", "Seleccioná un producto de la tabla.")
            return
        if not messagebox.askyesno("Confirmar", f"¿Eliminar '{p.nombre}'?"):
            return
        self.inventario.eliminar_producto(p.id_producto)
        self._refrescar_tabla()

    # ─────────────────────────────────────────────────────────────
    # VENTAS
    # ─────────────────────────────────────────────────────────────
    def _nueva_venta(self):
        VentanaVentas(self, self.inventario,
                      usuario=self.usuario["nombre"],
                      on_venta=self._refrescar_tabla)

    def _historial_ventas(self):
        VentanaHistorialVentas(self, self.inventario,
                               usuario=self.usuario["nombre"],
                               on_cambio=self._refrescar_tabla)

    def _abrir_caja(self):
        VentanaCaja(self, self.inventario)

    def _abrir_devoluciones(self):
        VentanaDevoluciones(self, self.inventario,
                            usuario=self.usuario["nombre"],
                            on_cambio=self._refrescar_tabla)

    def _abrir_cuenta_corriente(self):
        VentanaCuentaCorriente(self, self.inventario, usuario=self.usuario["nombre"])

    # ─────────────────────────────────────────────────────────────
    # MAESTROS
    # ─────────────────────────────────────────────────────────────
    def _abrir_clientes(self):
        VentanaClientes(self, self.inventario, on_cambio=self._refrescar_tabla)

    def _abrir_proveedores(self):
        VentanaProveedores(self, self.inventario, on_cambio=self._refrescar_tabla)

    def _abrir_categorias(self):
        VentanaCategorias(self, self.inventario, on_cambio=self._refrescar_tabla)

    # ─────────────────────────────────────────────────────────────
    # INVENTARIO
    # ─────────────────────────────────────────────────────────────
    def _abrir_movimientos(self):
        VentanaMovimientos(self, self.inventario,
                           usuario=self.usuario["nombre"],
                           on_cambio=self._refrescar_tabla)

    def _actualizar_precios(self):
        VentanaActualizarPrecios(self, self.inventario, on_cambio=self._refrescar_tabla)

    def _abrir_ofertas(self):
        VentanaOfertas(self, self.inventario, on_cambio=self._refrescar_tabla)

    def _abrir_vencimientos(self):
        VentanaVencimientos(self, self.inventario, on_cambio=self._refrescar_tabla)

    # ─────────────────────────────────────────────────────────────
    # COMPRAS
    # ─────────────────────────────────────────────────────────────
    def _abrir_ordenes_compra(self):
        VentanaOrdenesCompra(self, self.inventario,
                             usuario=self.usuario["nombre"],
                             on_cambio=self._refrescar_tabla)

    def _abrir_comprobantes(self):
        VentanaComprobantes(self, self.inventario, usuario=self.usuario["nombre"])

    # ─────────────────────────────────────────────────────────────
    # REPORTES Y EXPORTACIÓN
    # ─────────────────────────────────────────────────────────────
    def _abrir_estadisticas(self):
        VentanaEstadisticas(self, self.inventario)

    def _abrir_ganancias(self):
        VentanaGanancias(self, self.inventario)

    def _abrir_comparativa(self):
        VentanaComparativa(self, self.inventario)

    def _abrir_reportes(self):
        VentanaReportes(self, self.inventario)

    def _exportar_excel(self):
        productos = getattr(self, "_productos_actuales", self.inventario.obtener_productos())
        if not productos:
            messagebox.showinfo("Exportar", "No hay productos para exportar.")
            return
        try:
            ruta = exportar_excel(productos)
            messagebox.showinfo("Exportado", f"Archivo guardado en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _exportar_pdf(self):
        productos = getattr(self, "_productos_actuales", self.inventario.obtener_productos())
        if not productos:
            messagebox.showinfo("Exportar", "No hay productos para exportar.")
            return
        try:
            ruta = exportar_pdf(productos)
            messagebox.showinfo("Exportado", f"Archivo guardado en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ─────────────────────────────────────────────────────────────
    # SISTEMA
    # ─────────────────────────────────────────────────────────────
    def _abrir_usuarios(self):
        if self.usuario["rol"] != "dueño":
            messagebox.showerror("Sin permiso", "Solo el dueño puede gestionar usuarios.")
            return
        VentanaUsuarios(self, self.inventario, usuario_actual=self.usuario)

    def _abrir_backup(self):
        VentanaBackup(self)


def main():
    inicializar_db()

    # Pantalla de login
    inventario = Inventario()
    login = VentanaLogin(inventario)
    login.mainloop()

    if not login.usuario_logueado:
        return  # Cerró sin loguearse

    # Ventana principal
    app = AplicacionFerreteria(login.usuario_logueado)
    app.mainloop()


if __name__ == "__main__":
    main()
