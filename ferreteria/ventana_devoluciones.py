"""ventana_devoluciones.py - Registro de devoluciones de productos por clientes."""
import tkinter as tk
from tkinter import ttk, messagebox

COLOR_PRIMARIO = "#2F5496"
COLOR_FONDO = "#F4F6F7"


class VentanaDevoluciones(tk.Toplevel):
    def __init__(self, master, inventario, usuario="dueño", on_cambio=None):
        super().__init__(master)
        self.inventario = inventario
        self.usuario = usuario
        self.on_cambio = on_cambio
        self.title("Devoluciones — Ferretería Gian")
        self.geometry("950x580")
        self.configure(bg=COLOR_FONDO)
        self.transient(master)
        self.grab_set()
        self._construir()

    def _construir(self):
        tk.Label(self, text="🔄 Devoluciones de Clientes", font=("Segoe UI", 14, "bold"),
                 bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(pady=(12, 4))
        tk.Label(self, text="Registrá la devolución de un producto. El stock vuelve automáticamente.",
                 bg=COLOR_FONDO, font=("Segoe UI", 9, "italic"), fg="#666666").pack(pady=(0, 8))

        # Buscar venta original
        fr_busca = tk.LabelFrame(self, text="1. Buscar la venta original", bg=COLOR_FONDO,
                                  font=("Segoe UI", 10, "bold"), fg=COLOR_PRIMARIO, padx=10, pady=8)
        fr_busca.pack(fill="x", padx=15, pady=6)

        tk.Label(fr_busca, text="N° de venta:", bg=COLOR_FONDO, font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", padx=4)
        self.var_id_venta = tk.StringVar()
        tk.Entry(fr_busca, textvariable=self.var_id_venta, font=("Segoe UI", 10), width=10).grid(row=0, column=1, padx=4)
        tk.Button(fr_busca, text="🔍 Buscar", bg=COLOR_PRIMARIO, fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  command=self._buscar_venta).grid(row=0, column=2, padx=8)
        self.lbl_venta_info = tk.Label(fr_busca, text="", bg=COLOR_FONDO, font=("Segoe UI", 10), fg="#27AE60")
        self.lbl_venta_info.grid(row=0, column=3, padx=8, sticky="w")

        # Detalle de la venta
        fr_det = tk.LabelFrame(self, text="2. Seleccioná el producto a devolver", bg=COLOR_FONDO,
                                font=("Segoe UI", 10, "bold"), fg=COLOR_PRIMARIO, padx=10, pady=8)
        fr_det.pack(fill="x", padx=15, pady=4)

        cols = ("producto", "precio", "cantidad")
        self.tabla_det = ttk.Treeview(fr_det, columns=cols, show="headings", height=5)
        for col, txt, w in [("producto","Producto",320),("precio","Precio unit.",110),("cantidad","Cantidad",80)]:
            self.tabla_det.heading(col, text=txt)
            self.tabla_det.column(col, width=w, anchor="w" if col=="producto" else "center")
        self.tabla_det.pack(fill="x")

        # Formulario de devolución
        fr_form = tk.LabelFrame(self, text="3. Datos de la devolución", bg=COLOR_FONDO,
                                 font=("Segoe UI", 10, "bold"), fg=COLOR_PRIMARIO, padx=10, pady=8)
        fr_form.pack(fill="x", padx=15, pady=4)

        tk.Label(fr_form, text="Cantidad a devolver:", bg=COLOR_FONDO, font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", padx=4)
        self.var_cant = tk.StringVar(value="1")
        tk.Entry(fr_form, textvariable=self.var_cant, font=("Segoe UI", 10), width=8).grid(row=0, column=1, padx=4)

        tk.Label(fr_form, text="Motivo:", bg=COLOR_FONDO, font=("Segoe UI", 10)).grid(row=0, column=2, sticky="w", padx=8)
        self.var_motivo = tk.StringVar()
        tk.Entry(fr_form, textvariable=self.var_motivo, font=("Segoe UI", 10), width=36).grid(row=0, column=3, padx=4)

        tk.Button(fr_form, text="✅ Registrar devolución", bg="#27AE60", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                  command=self._registrar).grid(row=1, column=0, columnspan=4, pady=8)

        # Historial
        tk.Label(self, text="Historial de devoluciones recientes:", bg=COLOR_FONDO,
                 font=("Segoe UI", 10, "bold"), fg=COLOR_PRIMARIO).pack(anchor="w", padx=15, pady=(6,2))
        fr_hist = tk.Frame(self, bg=COLOR_FONDO)
        fr_hist.pack(fill="both", expand=True, padx=15, pady=(0,10))
        cols2 = ("fecha","venta","producto","cantidad","motivo","usuario")
        self.tabla_hist = ttk.Treeview(fr_hist, columns=cols2, show="headings", height=7)
        for col, txt, w in [("fecha","Fecha",140),("venta","Venta",70),("producto","Producto",220),
                              ("cantidad","Cant.",60),("motivo","Motivo",210),("usuario","Usuario",80)]:
            self.tabla_hist.heading(col, text=txt)
            self.tabla_hist.column(col, width=w, anchor="center" if col in ("venta","cantidad") else "w")
        sc = ttk.Scrollbar(fr_hist, orient="vertical", command=self.tabla_hist.yview)
        self.tabla_hist.configure(yscrollcommand=sc.set)
        self.tabla_hist.pack(side="left", fill="both", expand=True)
        sc.pack(side="right", fill="y")
        self._refrescar_historial()
        self._venta_actual = None
        self._detalles_actuales = []

    def _buscar_venta(self):
        try:
            id_v = int(self.var_id_venta.get())
        except:
            messagebox.showerror("Error", "Ingresá un número de venta válido.", parent=self)
            return
        ventas = self.inventario.obtener_ventas()
        venta = next((v for v in ventas if v.id_venta == id_v), None)
        if not venta:
            messagebox.showerror("No encontrada", f"No existe la venta #{id_v}.", parent=self)
            return
        if venta.anulada:
            messagebox.showerror("Anulada", "No se puede devolver una venta anulada.", parent=self)
            return
        self._venta_actual = venta
        self.lbl_venta_info.config(text=f"✓ Venta del {venta.fecha} — Total: ${venta.total:,.2f}")
        detalles = self.inventario.obtener_detalle_venta(id_v)
        self._detalles_actuales = detalles
        for row in self.tabla_det.get_children():
            self.tabla_det.delete(row)
        for d in detalles:
            self.tabla_det.insert("", "end", iid=d.id_producto or d.nombre_producto,
                                   values=(d.nombre_producto, f"${d.precio_unitario:,.2f}", d.cantidad))

    def _registrar(self):
        if not self._venta_actual:
            messagebox.showwarning("Atención", "Primero buscá la venta original.", parent=self)
            return
        sel = self.tabla_det.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccioná el producto a devolver.", parent=self)
            return
        try:
            cant = int(self.var_cant.get())
            if cant <= 0: raise ValueError
        except:
            messagebox.showerror("Error", "Ingresá una cantidad válida.", parent=self)
            return
        sel_val = sel[0]
        detalle = next((d for d in self._detalles_actuales
                        if str(d.id_producto) == str(sel_val) or d.nombre_producto == str(sel_val)), None)
        if not detalle:
            messagebox.showerror("Error", "No se encontró el producto seleccionado.", parent=self)
            return
        if cant > detalle.cantidad:
            messagebox.showerror("Error", f"La cantidad a devolver ({cant}) no puede ser mayor a la vendida ({detalle.cantidad}).", parent=self)
            return
        motivo = self.var_motivo.get() or "Sin motivo especificado"
        try:
            self.inventario.registrar_devolucion(
                self._venta_actual.id_venta, detalle.id_producto, detalle.nombre_producto,
                cant, detalle.precio_unitario, motivo, self.usuario)
            messagebox.showinfo("Devolución registrada",
                                 f"Se registró la devolución de {cant} unidad(es) de:\n{detalle.nombre_producto}\n\nEl stock fue actualizado.", parent=self)
            self.var_cant.set("1"); self.var_motivo.set("")
            self._refrescar_historial()
            if self.on_cambio: self.on_cambio()
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self)

    def _refrescar_historial(self):
        for row in self.tabla_hist.get_children():
            self.tabla_hist.delete(row)
        for d in self.inventario.obtener_devoluciones():
            self.tabla_hist.insert("", "end", values=(d.fecha, f"#{d.id_venta:05d}",
                                                        d.nombre_producto, d.cantidad, d.motivo, d.usuario))
