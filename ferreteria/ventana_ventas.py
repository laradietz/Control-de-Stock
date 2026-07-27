"""ventana_ventas.py - Punto de venta con carrito, búsqueda de productos y boleta PDF."""
import tkinter as tk
from tkinter import ttk, messagebox
from modelos import DetalleVenta
from exportador import generar_boleta_pdf
import subprocess, sys, os

COLOR_PRIMARIO = "#2F5496"
COLOR_FONDO = "#F4F6F7"


class VentanaVentas(tk.Toplevel):
    def __init__(self, master, inventario, usuario="dueño", on_venta=None):
        super().__init__(master)
        self.inventario = inventario
        self.usuario = usuario
        self.on_venta = on_venta
        self.carrito = []
        self.title("Nueva Venta — Ferretería Gian")
        self.geometry("1150x700")
        self.minsize(1000, 640)
        self.configure(bg=COLOR_FONDO)
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._cancelar)
        self._construir()
        self._cargar_clientes()

    def _construir(self):
        # ENCABEZADO
        enc = tk.Frame(self, bg=COLOR_PRIMARIO, height=45)
        enc.pack(fill="x")
        enc.pack_propagate(False)
        tk.Label(enc, text="🛒  Nueva Venta", bg=COLOR_PRIMARIO, fg="white",
                 font=("Segoe UI", 14, "bold")).pack(side="left", padx=15, pady=8)

        contenedor = tk.Frame(self, bg=COLOR_FONDO)
        contenedor.pack(fill="both", expand=True, padx=12, pady=8)

        # ── PANEL IZQUIERDO: búsqueda ──
        izq = tk.LabelFrame(contenedor, text="Buscar y agregar productos",
                             bg=COLOR_FONDO, font=("Segoe UI", 10, "bold"), fg=COLOR_PRIMARIO)
        izq.pack(side="left", fill="both", expand=True, padx=(0, 8))

        fr_bus = tk.Frame(izq, bg=COLOR_FONDO)
        fr_bus.pack(fill="x", padx=8, pady=8)
        tk.Label(fr_bus, text="Código o nombre:", bg=COLOR_FONDO,
                 font=("Segoe UI", 10)).pack(side="left")
        self.var_busqueda = tk.StringVar()
        self.var_busqueda.trace_add("write", lambda *a: self._buscar())
        tk.Entry(fr_bus, textvariable=self.var_busqueda,
                 font=("Segoe UI", 10), width=28).pack(side="left", padx=6)

        cols = ("codigo", "nombre", "precio", "stock")
        self.tabla_prod = ttk.Treeview(izq, columns=cols, show="headings", height=18)
        for col, txt, w in [("codigo","Código",80),("nombre","Nombre",250),
                              ("precio","Precio",100),("stock","Stock",70)]:
            self.tabla_prod.heading(col, text=txt)
            self.tabla_prod.column(col, width=w, anchor="w" if col=="nombre" else "center")
        sc = ttk.Scrollbar(izq, orient="vertical", command=self.tabla_prod.yview)
        self.tabla_prod.configure(yscrollcommand=sc.set)
        self.tabla_prod.pack(side="left", fill="both", expand=True, padx=(8,0), pady=(0,8))
        sc.pack(side="left", fill="y", pady=(0,8))
        self.tabla_prod.bind("<Double-1>", lambda e: self._agregar_al_carrito())
        self._buscar()

        fr_cant = tk.Frame(izq, bg=COLOR_FONDO)
        fr_cant.pack(fill="x", padx=8, pady=(0,8))
        tk.Label(fr_cant, text="Cantidad:", bg=COLOR_FONDO,
                 font=("Segoe UI", 10)).pack(side="left")
        self.var_cantidad = tk.StringVar(value="1")
        tk.Entry(fr_cant, textvariable=self.var_cantidad,
                 font=("Segoe UI", 10), width=6).pack(side="left", padx=6)
        tk.Button(fr_cant, text="➕ Agregar al carrito", bg="#27AE60", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                  command=self._agregar_al_carrito).pack(side="left", padx=8)
        tk.Label(fr_cant, text="(o doble clic sobre el producto)",
                 bg=COLOR_FONDO, font=("Segoe UI", 8), fg="#888888").pack(side="left")

        # ── PANEL DERECHO: carrito + opciones + botones ──
        der = tk.Frame(contenedor, bg=COLOR_FONDO, width=400)
        der.pack(side="left", fill="y")
        der.pack_propagate(False)

        # Cliente
        fr_cli = tk.LabelFrame(der, text="Cliente", bg=COLOR_FONDO,
                                font=("Segoe UI", 9, "bold"), fg=COLOR_PRIMARIO, padx=6, pady=4)
        fr_cli.pack(fill="x", pady=(0,4))
        self.combo_cliente = ttk.Combobox(fr_cli, state="readonly",
                                           font=("Segoe UI", 10), width=36)
        self.combo_cliente.pack(fill="x")
        tk.Label(fr_cli, text="Obligatorio si la forma de pago es Fiado",
                 bg=COLOR_FONDO, font=("Segoe UI", 8), fg="#888888").pack(anchor="w")

        # Forma de pago
        fr_pago = tk.LabelFrame(der, text="Forma de pago", bg=COLOR_FONDO,
                                  font=("Segoe UI", 9, "bold"), fg=COLOR_PRIMARIO, padx=6, pady=4)
        fr_pago.pack(fill="x", pady=(0,4))
        self.var_forma_pago = tk.StringVar(value="efectivo")
        fr_radios = tk.Frame(fr_pago, bg=COLOR_FONDO)
        fr_radios.pack(fill="x")
        for texto, valor, color in [
            ("💵 Efectivo",   "efectivo",          "#27AE60"),
            ("💳 Tarjeta",    "tarjeta",            "#2F5496"),
            ("🔁 Transf.",    "transferencia",      "#8E44AD"),
            ("📒 Fiado",      "cuenta_corriente",   "#C0392B"),
        ]:
            tk.Radiobutton(fr_radios, text=texto, variable=self.var_forma_pago,
                           value=valor, bg=COLOR_FONDO, fg=color,
                           font=("Segoe UI", 9), activebackground=COLOR_FONDO,
                           command=self._actualizar_total).pack(side="left", padx=3)

        # Descuento
        fr_desc = tk.Frame(der, bg=COLOR_FONDO)
        fr_desc.pack(fill="x", pady=(0,4))
        tk.Label(fr_desc, text="Descuento %:", bg=COLOR_FONDO,
                 font=("Segoe UI", 10)).pack(side="left")
        self.var_descuento = tk.StringVar(value="0")
        self.var_descuento.trace_add("write", lambda *a: self._actualizar_total())
        tk.Entry(fr_desc, textvariable=self.var_descuento,
                 font=("Segoe UI", 10), width=6).pack(side="left", padx=6)
        tk.Label(fr_desc, text="(0 = sin descuento)", bg=COLOR_FONDO,
                 font=("Segoe UI", 8), fg="#888888").pack(side="left")

        # Carrito
        tk.Label(der, text="Carrito:", bg=COLOR_FONDO,
                 font=("Segoe UI", 10, "bold"), fg=COLOR_PRIMARIO).pack(anchor="w", pady=(2,0))
        fr_carrito = tk.Frame(der, bg=COLOR_FONDO)
        fr_carrito.pack(fill="both", expand=True)
        cols2 = ("nombre", "precio", "cant", "subtotal")
        self.tabla_carrito = ttk.Treeview(fr_carrito, columns=cols2,
                                           show="headings", height=10)
        for col, txt, w in [("nombre","Producto",160),("precio","Precio",80),
                              ("cant","Cant",45),("subtotal","Subtotal",80)]:
            self.tabla_carrito.heading(col, text=txt)
            self.tabla_carrito.column(col, width=w, anchor="w" if col=="nombre" else "center")
        sc2 = ttk.Scrollbar(fr_carrito, orient="vertical", command=self.tabla_carrito.yview)
        self.tabla_carrito.configure(yscrollcommand=sc2.set)
        self.tabla_carrito.pack(side="left", fill="both", expand=True)
        sc2.pack(side="right", fill="y")

        tk.Button(der, text="🗑 Quitar seleccionado", bg="#C0392B", fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  command=self._quitar_item).pack(fill="x", pady=2)

        # Total
        self.lbl_total = tk.Label(der, text="TOTAL: $0.00", bg=COLOR_PRIMARIO,
                                   fg="white", font=("Segoe UI", 16, "bold"))
        self.lbl_total.pack(fill="x", pady=4)

        # Aviso
        self.lbl_aviso = tk.Label(der, text="", bg="#FFF3CD", fg="#856404",
                                   font=("Segoe UI", 8, "bold"),
                                   wraplength=380, justify="left")
        self.lbl_aviso.pack(fill="x")

        # ── BOTONES PRINCIPALES ──
        tk.Button(der, text="✅  CONFIRMAR VENTA",
                  bg="#27AE60", fg="white",
                  font=("Segoe UI", 13, "bold"), relief="flat",
                  cursor="hand2", pady=8,
                  command=self._confirmar_venta).pack(fill="x", pady=(8,2))

        tk.Button(der, text="🖨  Confirmar e imprimir boleta",
                  bg=COLOR_PRIMARIO, fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat",
                  cursor="hand2", pady=6,
                  command=self._confirmar_e_imprimir).pack(fill="x", pady=2)

        tk.Button(der, text="❌  Cancelar venta",
                  bg="#AAAAAA", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat",
                  cursor="hand2", pady=5,
                  command=self._cancelar).pack(fill="x", pady=2)

    # ── LÓGICA ──────────────────────────────────────────────────

    def _cargar_clientes(self):
        self.clientes = self.inventario.obtener_clientes()
        self.combo_cliente["values"] = [c.nombre for c in self.clientes]
        if self.clientes:
            self.combo_cliente.current(0)

    def _buscar(self):
        texto = self.var_busqueda.get()
        for row in self.tabla_prod.get_children():
            self.tabla_prod.delete(row)
        for p in self.inventario.obtener_productos(filtro_texto=texto):
            self.tabla_prod.insert("", "end", iid=p.id_producto,
                                    values=(p.codigo, p.nombre,
                                            f"${p.precio:,.2f}", p.cantidad))

    def _agregar_al_carrito(self):
        sel = self.tabla_prod.selection()
        if not sel:
            messagebox.showwarning("Atención",
                                    "Seleccioná un producto de la lista.", parent=self)
            return
        id_p = int(sel[0])
        producto = self.inventario.obtener_producto_por_id(id_p)
        if not producto:
            return
        try:
            cant = int(self.var_cantidad.get())
            if cant <= 0: raise ValueError
        except:
            messagebox.showerror("Error",
                                  "Ingresá una cantidad válida (entero mayor a 0).", parent=self)
            return
        cant_en_carrito = sum(d.cantidad for d in self.carrito if d.id_producto == id_p)
        if cant_en_carrito + cant > producto.cantidad:
            messagebox.showerror("Stock insuficiente",
                                  f"Stock disponible: {producto.cantidad}. "
                                  f"Ya tenés {cant_en_carrito} en el carrito.", parent=self)
            return
        for d in self.carrito:
            if d.id_producto == id_p:
                d.cantidad += cant
                d.subtotal = d.precio_unitario * d.cantidad
                self._refrescar_carrito()
                return
        self.carrito.append(DetalleVenta(id_p, producto.nombre, producto.precio, cant))
        self._refrescar_carrito()

    def _refrescar_carrito(self):
        for row in self.tabla_carrito.get_children():
            self.tabla_carrito.delete(row)
        for d in self.carrito:
            self.tabla_carrito.insert("", "end", values=(
                d.nombre_producto, f"${d.precio_unitario:,.2f}",
                d.cantidad, f"${d.subtotal:,.2f}"))
        self._actualizar_total()

    def _actualizar_total(self):
        try:
            desc = float(self.var_descuento.get() or 0)
            desc = max(0, min(100, desc))
        except:
            desc = 0
        subtotal = sum(d.subtotal for d in self.carrito)
        total = subtotal * (1 - desc / 100)
        sufijo = f"  (-{desc:.0f}%)" if desc > 0 else ""
        self.lbl_total.config(text=f"TOTAL: ${total:,.2f}{sufijo}")
        if self.carrito:
            self.lbl_aviso.config(
                text='⚠ Tocá "CONFIRMAR VENTA" para que quede guardada.')
        else:
            self.lbl_aviso.config(text="")

    def _get_descuento(self):
        try:
            d = float(self.var_descuento.get() or 0)
            return max(0, min(100, d))
        except:
            return 0

    def _quitar_item(self):
        sel = self.tabla_carrito.selection()
        if not sel:
            return
        self.carrito.pop(self.tabla_carrito.index(sel[0]))
        self._refrescar_carrito()

    def _get_id_cliente(self):
        idx = self.combo_cliente.current()
        return self.clientes[idx].id_cliente if idx >= 0 and self.clientes else None

    def _cancelar(self):
        if self.carrito:
            if not messagebox.askyesno(
                "Salir sin guardar",
                "Tenés productos en el carrito que todavía NO se registraron.\n\n"
                "Si salís ahora la venta NO se va a guardar.\n\n"
                "¿Seguro que querés salir sin confirmar?",
                parent=self, icon="warning"):
                return
        self.destroy()

    def _validar_fiado(self, forma):
        if forma != "cuenta_corriente":
            return True
        idx = self.combo_cliente.current()
        if idx < 0 or not self.clientes:
            messagebox.showerror(
                "Cliente requerido",
                "Para ventas fiadas tenés que seleccionar un cliente.\n\n"
                "Si el cliente no está en la lista, cerrá esta ventana "
                "y agregalo desde Menú → Clientes.", parent=self)
            return False
        nombre = self.clientes[idx].nombre
        if nombre.lower() in ("cliente general", "sin cliente"):
            messagebox.showerror(
                "Cliente requerido",
                "No se puede registrar una venta fiada a 'Cliente General'.\n\n"
                "Seleccioná un cliente específico o agregalo primero "
                "desde Menú → Clientes.", parent=self)
            return False
        return True

    def _confirmar_venta(self):
        if not self.carrito:
            messagebox.showwarning("Carrito vacío",
                                    "Agregá al menos un producto antes de confirmar.",
                                    parent=self)
            return
        forma = self.var_forma_pago.get()
        if not self._validar_fiado(forma):
            return
        desc = self._get_descuento()
        subtotal = sum(d.subtotal for d in self.carrito)
        total = round(subtotal * (1 - desc / 100), 2)
        cant_items = sum(d.cantidad for d in self.carrito)
        formas_txt = {"efectivo": "Efectivo", "tarjeta": "Tarjeta",
                      "transferencia": "Transferencia",
                      "cuenta_corriente": "Fiado (cuenta corriente)"}
        cliente_txt = self.combo_cliente.get() or "Sin cliente"
        if not messagebox.askyesno(
            "Confirmar venta",
            f"Productos: {len(self.carrito)} ({cant_items} unidades)\n"
            f"Cliente: {cliente_txt}\n"
            f"Forma de pago: {formas_txt.get(forma, forma)}\n"
            f"Descuento: {desc:.0f}%\n"
            f"Total: ${total:,.2f}\n\n¿Confirmar la venta?", parent=self):
            return
        id_cliente = self._get_id_cliente()
        id_venta = self.inventario.registrar_venta(
            self.carrito, id_cliente, self.usuario, forma, desc)
        messagebox.showinfo(
            "✅ Venta registrada",
            f"Venta #{id_venta:05d} registrada correctamente.\n\n"
            f"Total: ${total:,.2f}  ({formas_txt.get(forma, forma)})\n"
            f"El stock ya fue actualizado.", parent=self)
        if self.on_venta:
            self.on_venta()
        self.destroy()

    def _confirmar_e_imprimir(self):
        if not self.carrito:
            messagebox.showwarning("Carrito vacío",
                                    "Agregá al menos un producto antes de confirmar.",
                                    parent=self)
            return
        forma = self.var_forma_pago.get()
        if not self._validar_fiado(forma):
            return
        desc = self._get_descuento()
        subtotal = sum(d.subtotal for d in self.carrito)
        total = round(subtotal * (1 - desc / 100), 2)
        formas_txt = {"efectivo": "Efectivo", "tarjeta": "Tarjeta",
                      "transferencia": "Transferencia",
                      "cuenta_corriente": "Fiado (cuenta corriente)"}
        cliente_txt = self.combo_cliente.get() or "Sin cliente"
        cant_items = sum(d.cantidad for d in self.carrito)
        if not messagebox.askyesno(
            "Confirmar venta",
            f"Productos: {len(self.carrito)} ({cant_items} unidades)\n"
            f"Cliente: {cliente_txt}\n"
            f"Forma de pago: {formas_txt.get(forma, forma)}\n"
            f"Descuento: {desc:.0f}%\n"
            f"Total: ${total:,.2f}\n\n¿Confirmar y generar boleta?", parent=self):
            return
        id_cliente = self._get_id_cliente()
        from datetime import datetime
        id_venta = self.inventario.registrar_venta(
            self.carrito, id_cliente, self.usuario, forma, desc)
        try:
            ruta = generar_boleta_pdf(
                id_venta, self.carrito, total,
                datetime.now().strftime("%d/%m/%Y %H:%M"),
                cliente_txt, forma_pago=forma, descuento=desc)
            messagebox.showinfo("Boleta generada",
                                 f"Boleta guardada en:\n{ruta}\n\nAbriendo...",
                                 parent=self)
            if sys.platform == "win32":
                os.startfile(ruta)
            elif sys.platform == "darwin":
                subprocess.run(["open", ruta])
            else:
                subprocess.run(["xdg-open", ruta])
        except Exception as e:
            messagebox.showerror("Error al generar boleta", str(e), parent=self)
        if self.on_venta:
            self.on_venta()
        self.destroy()
