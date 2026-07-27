"""ventana_ordenes_compra.py - Gestión de pedidos/órdenes de compra a proveedores."""
import tkinter as tk
from tkinter import ttk, messagebox
from modelos import DetalleOrdenCompra

COLOR_PRIMARIO = "#2F5496"
COLOR_FONDO = "#F4F6F7"


class VentanaOrdenesCompra(tk.Toplevel):
    def __init__(self, master, inventario, usuario="dueño", on_cambio=None):
        super().__init__(master)
        self.inventario = inventario
        self.usuario = usuario
        self.on_cambio = on_cambio
        self.carrito_pedido = []  # lista de DetalleOrdenCompra para armar pedido nuevo
        self.title("Pedidos a Proveedores — Ferretería Gian")
        self.geometry("1000x640")
        self.configure(bg=COLOR_FONDO)
        self.transient(master)
        self.grab_set()
        self._construir()
        self._refrescar_ordenes()

    def _construir(self):
        tk.Label(self, text="🚚 Pedidos a Proveedores", font=("Segoe UI", 14, "bold"),
                 bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(pady=(12, 4))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=6)

        self.tab_nuevo = tk.Frame(self.notebook, bg=COLOR_FONDO)
        self.notebook.add(self.tab_nuevo, text="  Armar pedido nuevo  ")

        self.tab_lista = tk.Frame(self.notebook, bg=COLOR_FONDO)
        self.notebook.add(self.tab_lista, text="  Pedidos realizados  ")

        self._construir_tab_nuevo()
        self._construir_tab_lista()

    # ───────────────── PESTAÑA: ARMAR PEDIDO NUEVO ─────────────────
    def _construir_tab_nuevo(self):
        # Botón de generación automática
        fr_auto = tk.Frame(self.tab_nuevo, bg="#FFF3CD")
        fr_auto.pack(fill="x", padx=10, pady=8)
        tk.Label(fr_auto, text="⚡ Generación automática: crea un pedido con todos los productos en stock bajo.",
                 bg="#FFF3CD", fg="#856404", font=("Segoe UI", 9)).pack(side="left", padx=8, pady=6)
        tk.Button(fr_auto, text="Generar pedido automático", bg="#D68910", fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  command=self._generar_automatico).pack(side="right", padx=8, pady=4)

        # Selección de proveedor
        fr_prov = tk.Frame(self.tab_nuevo, bg=COLOR_FONDO)
        fr_prov.pack(fill="x", padx=10, pady=6)
        tk.Label(fr_prov, text="Proveedor:", bg=COLOR_FONDO, font=("Segoe UI", 10, "bold")).pack(side="left")
        self.combo_proveedor = ttk.Combobox(fr_prov, state="readonly", font=("Segoe UI", 10), width=30)
        self.combo_proveedor.pack(side="left", padx=8)
        self.combo_proveedor.bind("<<ComboboxSelected>>", lambda e: self._buscar_productos())

        # Búsqueda de productos del proveedor
        fr_bus = tk.Frame(self.tab_nuevo, bg=COLOR_FONDO)
        fr_bus.pack(fill="both", expand=True, padx=10, pady=4)

        izq = tk.LabelFrame(fr_bus, text="Productos del proveedor", bg=COLOR_FONDO,
                             font=("Segoe UI", 9, "bold"), fg=COLOR_PRIMARIO)
        izq.pack(side="left", fill="both", expand=True, padx=(0, 6))

        cols = ("codigo", "nombre", "stock", "minimo")
        self.tabla_prod = ttk.Treeview(izq, columns=cols, show="headings", height=12)
        for col, txt, w in [("codigo", "Código", 70), ("nombre", "Nombre", 220),
                              ("stock", "Stock", 60), ("minimo", "Mínimo", 60)]:
            self.tabla_prod.heading(col, text=txt)
            self.tabla_prod.column(col, width=w, anchor="w" if col == "nombre" else "center")
        self.tabla_prod.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        self.tabla_prod.tag_configure("bajo", background="#FFC7CE")

        fr_cant = tk.Frame(izq, bg=COLOR_FONDO)
        fr_cant.pack(fill="x", padx=6, pady=(0, 6))
        tk.Label(fr_cant, text="Cantidad a pedir:", bg=COLOR_FONDO, font=("Segoe UI", 9)).pack(side="left")
        self.var_cant_pedido = tk.StringVar(value="10")
        tk.Entry(fr_cant, textvariable=self.var_cant_pedido, font=("Segoe UI", 9), width=6).pack(side="left", padx=4)
        tk.Button(fr_cant, text="➕ Agregar al pedido", bg="#27AE60", fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  command=self._agregar_al_pedido).pack(side="left", padx=6)

        der = tk.LabelFrame(fr_bus, text="Pedido a armar", bg=COLOR_FONDO,
                             font=("Segoe UI", 9, "bold"), fg=COLOR_PRIMARIO, width=320)
        der.pack(side="left", fill="both", padx=(6, 0))
        der.pack_propagate(False)

        cols2 = ("producto", "cantidad")
        self.tabla_pedido = ttk.Treeview(der, columns=cols2, show="headings", height=10)
        self.tabla_pedido.heading("producto", text="Producto")
        self.tabla_pedido.heading("cantidad", text="Cantidad")
        self.tabla_pedido.column("producto", width=220)
        self.tabla_pedido.column("cantidad", width=80, anchor="center")
        self.tabla_pedido.pack(fill="both", expand=True, padx=6, pady=6)

        tk.Button(der, text="🗑 Quitar", bg="#C0392B", fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  command=self._quitar_del_pedido).pack(pady=2)

        tk.Label(der, text="Notas (opcional):", bg=COLOR_FONDO, font=("Segoe UI", 9)).pack(anchor="w", padx=6, pady=(6, 0))
        self.var_notas = tk.StringVar()
        tk.Entry(der, textvariable=self.var_notas, font=("Segoe UI", 9), width=36).pack(padx=6, pady=2)

        tk.Button(der, text="✅ Confirmar pedido", bg=COLOR_PRIMARIO, fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                  command=self._confirmar_pedido).pack(fill="x", padx=6, pady=8)

        self._cargar_proveedores()

    def _cargar_proveedores(self):
        self.proveedores = self.inventario.obtener_proveedores()
        self.combo_proveedor["values"] = [p.nombre for p in self.proveedores]
        if self.proveedores:
            self.combo_proveedor.current(0)
            self._buscar_productos()

    def _buscar_productos(self):
        idx = self.combo_proveedor.current()
        if idx < 0 or not self.proveedores:
            return
        id_prov = self.proveedores[idx].id_proveedor
        for row in self.tabla_prod.get_children():
            self.tabla_prod.delete(row)
        productos = self.inventario.obtener_productos(id_proveedor=id_prov)
        self._productos_proveedor = productos
        for p in productos:
            tags = ("bajo",) if p.stock_bajo() else ()
            self.tabla_prod.insert("", "end", iid=p.id_producto,
                                    values=(p.codigo, p.nombre, p.cantidad, p.stock_minimo), tags=tags)

    def _agregar_al_pedido(self):
        sel = self.tabla_prod.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccioná un producto.", parent=self)
            return
        try:
            cant = int(self.var_cant_pedido.get())
            if cant <= 0: raise ValueError
        except:
            messagebox.showerror("Error", "Ingresá una cantidad válida.", parent=self)
            return
        id_p = int(sel[0])
        producto = self.inventario.obtener_producto_por_id(id_p)
        for d in self.carrito_pedido:
            if d.id_producto == id_p:
                d.cantidad_pedida += cant
                self._refrescar_carrito_pedido()
                return
        self.carrito_pedido.append(DetalleOrdenCompra(
            id_producto=id_p, nombre_producto=producto.nombre, cantidad_pedida=cant))
        self._refrescar_carrito_pedido()

    def _refrescar_carrito_pedido(self):
        for row in self.tabla_pedido.get_children():
            self.tabla_pedido.delete(row)
        for d in self.carrito_pedido:
            self.tabla_pedido.insert("", "end", values=(d.nombre_producto, d.cantidad_pedida))

    def _quitar_del_pedido(self):
        sel = self.tabla_pedido.selection()
        if not sel:
            return
        idx = self.tabla_pedido.index(sel[0])
        self.carrito_pedido.pop(idx)
        self._refrescar_carrito_pedido()

    def _confirmar_pedido(self):
        if not self.carrito_pedido:
            messagebox.showwarning("Pedido vacío", "Agregá al menos un producto.", parent=self)
            return
        idx = self.combo_proveedor.current()
        id_prov = self.proveedores[idx].id_proveedor if idx >= 0 else None
        nombre_prov = self.combo_proveedor.get()
        if not messagebox.askyesno("Confirmar pedido",
                                    f"¿Confirmar pedido a {nombre_prov} con {len(self.carrito_pedido)} producto(s)?",
                                    parent=self):
            return
        id_orden = self.inventario.crear_orden_compra(
            id_prov, self.carrito_pedido, self.usuario, self.var_notas.get())
        messagebox.showinfo("Pedido creado", f"Pedido #{id_orden:04d} registrado correctamente.\n\n"
                                              "Podés verlo en la pestaña \"Pedidos realizados\".", parent=self)
        self.carrito_pedido = []
        self._refrescar_carrito_pedido()
        self.var_notas.set("")
        self._refrescar_ordenes()
        if self.on_cambio:
            self.on_cambio()

    def _generar_automatico(self):
        idx = self.combo_proveedor.current()
        id_prov = self.proveedores[idx].id_proveedor if idx >= 0 else None
        if not messagebox.askyesno("Generar pedido automático",
                                    "Se va a generar un pedido con todos los productos en stock bajo"
                                    f"{' del proveedor seleccionado' if id_prov else ' (de todos los proveedores)'}.\n\n"
                                    "Las cantidades se calculan automáticamente para reponer el stock.\n\n¿Continuar?",
                                    parent=self):
            return
        try:
            id_orden = self.inventario.generar_orden_automatica(id_prov, self.usuario)
            messagebox.showinfo("Pedido generado", f"Pedido automático #{id_orden:04d} generado correctamente.",
                                 parent=self)
            self._refrescar_ordenes()
            if self.on_cambio:
                self.on_cambio()
        except ValueError as e:
            messagebox.showinfo("Sin productos", str(e), parent=self)

    # ───────────────── PESTAÑA: PEDIDOS REALIZADOS ─────────────────
    def _construir_tab_lista(self):
        fr_filtro = tk.Frame(self.tab_lista, bg=COLOR_FONDO)
        fr_filtro.pack(fill="x", padx=10, pady=8)
        tk.Label(fr_filtro, text="Estado:", bg=COLOR_FONDO, font=("Segoe UI", 10)).pack(side="left")
        self.combo_estado = ttk.Combobox(fr_filtro, state="readonly", font=("Segoe UI", 10), width=18,
                                          values=["(Todos)", "pendiente", "recibida", "cancelada"])
        self.combo_estado.current(0)
        self.combo_estado.pack(side="left", padx=6)
        self.combo_estado.bind("<<ComboboxSelected>>", lambda e: self._refrescar_ordenes())
        tk.Button(fr_filtro, text="Actualizar", bg=COLOR_PRIMARIO, fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  command=self._refrescar_ordenes).pack(side="left", padx=6)

        fr_t = tk.Frame(self.tab_lista, bg=COLOR_FONDO)
        fr_t.pack(fill="both", expand=True, padx=10)
        cols = ("id", "proveedor", "fecha", "estado", "notas")
        self.tabla_ordenes = ttk.Treeview(fr_t, columns=cols, show="headings", height=8)
        for col, txt, w in [("id", "N° Pedido", 80), ("proveedor", "Proveedor", 200),
                              ("fecha", "Fecha", 150), ("estado", "Estado", 90), ("notas", "Notas", 220)]:
            self.tabla_ordenes.heading(col, text=txt)
            self.tabla_ordenes.column(col, width=w, anchor="center" if col in ("id", "estado") else "w")
        sc = ttk.Scrollbar(fr_t, orient="vertical", command=self.tabla_ordenes.yview)
        self.tabla_ordenes.configure(yscrollcommand=sc.set)
        self.tabla_ordenes.pack(side="left", fill="both", expand=True)
        sc.pack(side="right", fill="y")
        self.tabla_ordenes.tag_configure("recibida", foreground="#27AE60")
        self.tabla_ordenes.tag_configure("cancelada", foreground="#AAAAAA")
        self.tabla_ordenes.tag_configure("pendiente", foreground="#D68910")
        self.tabla_ordenes.bind("<<TreeviewSelect>>", self._mostrar_detalle_orden)

        tk.Label(self.tab_lista, text="Detalle del pedido:", bg=COLOR_FONDO,
                 font=("Segoe UI", 10, "bold"), fg=COLOR_PRIMARIO).pack(anchor="w", padx=10, pady=(8, 2))
        fr_det = tk.Frame(self.tab_lista, bg=COLOR_FONDO)
        fr_det.pack(fill="x", padx=10)
        cols2 = ("producto", "pedida", "recibida")
        self.tabla_det_orden = ttk.Treeview(fr_det, columns=cols2, show="headings", height=5)
        for col, txt, w in [("producto", "Producto", 350), ("pedida", "Cant. pedida", 110), ("recibida", "Cant. recibida", 110)]:
            self.tabla_det_orden.heading(col, text=txt)
            self.tabla_det_orden.column(col, width=w, anchor="w" if col == "producto" else "center")
        self.tabla_det_orden.pack(fill="x")

        fr_bot = tk.Frame(self.tab_lista, bg=COLOR_FONDO)
        fr_bot.pack(pady=8)
        tk.Button(fr_bot, text="📦 Marcar como recibida (sumar stock)", bg="#27AE60", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                  command=self._marcar_recibida).pack(side="left", padx=4)
        tk.Button(fr_bot, text="❌ Cancelar pedido", bg="#C0392B", fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  command=self._cancelar_pedido).pack(side="left", padx=4)

    def _refrescar_ordenes(self):
        for row in self.tabla_ordenes.get_children():
            self.tabla_ordenes.delete(row)
        estado = self.combo_estado.get()
        estado_filtro = None if estado in ("(Todos)", "") else estado
        ordenes = self.inventario.obtener_ordenes_compra(estado_filtro)
        for o in ordenes:
            self.tabla_ordenes.insert("", "end", iid=o.id_orden,
                                       values=(f"{o.id_orden:04d}", o.proveedor_nombre, o.fecha,
                                               o.estado.upper(), o.notas or ""), tags=(o.estado,))
        for row in self.tabla_det_orden.get_children():
            self.tabla_det_orden.delete(row)

    def _mostrar_detalle_orden(self, event):
        sel = self.tabla_ordenes.selection()
        if not sel:
            return
        id_o = int(sel[0])
        for row in self.tabla_det_orden.get_children():
            self.tabla_det_orden.delete(row)
        for d in self.inventario.obtener_detalle_orden(id_o):
            self.tabla_det_orden.insert("", "end", values=(d.nombre_producto, d.cantidad_pedida, d.cantidad_recibida))

    def _marcar_recibida(self):
        sel = self.tabla_ordenes.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccioná un pedido.", parent=self)
            return
        id_o = int(sel[0])
        if not messagebox.askyesno("Confirmar recepción",
                                    "¿Marcar este pedido como recibido?\n\n"
                                    "El stock de los productos se actualizará automáticamente.", parent=self):
            return
        try:
            self.inventario.marcar_orden_recibida(id_o, usuario=self.usuario)
            messagebox.showinfo("Recibido", "Pedido marcado como recibido. Stock actualizado.", parent=self)
            self._refrescar_ordenes()
            if self.on_cambio:
                self.on_cambio()
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self)

    def _cancelar_pedido(self):
        sel = self.tabla_ordenes.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccioná un pedido.", parent=self)
            return
        id_o = int(sel[0])
        if not messagebox.askyesno("Cancelar pedido", "¿Cancelar este pedido?", parent=self):
            return
        self.inventario.cancelar_orden_compra(id_o)
        self._refrescar_ordenes()
