"""ventana_precios.py - Actualización automática de precios por proveedor (remarcación)."""
import tkinter as tk
from tkinter import ttk, messagebox

COLOR_PRIMARIO = "#2F5496"
COLOR_FONDO = "#F4F6F7"

class VentanaActualizarPrecios(tk.Toplevel):
    def __init__(self, master, inventario, on_cambio=None):
        super().__init__(master)
        self.inventario = inventario
        self.on_cambio = on_cambio
        self.title("Actualizar Precios por Proveedor")
        self.geometry("700x480")
        self.configure(bg=COLOR_FONDO)
        self.transient(master)
        self.grab_set()
        self._construir()
        self._refrescar()

    def _construir(self):
        tk.Label(self, text="🏷 Actualización de Precios", font=("Segoe UI", 14, "bold"),
                 bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(pady=(15, 3))
        tk.Label(self, text="Seleccioná un proveedor y aplicá un porcentaje de aumento o reducción a todos sus productos.",
                 bg=COLOR_FONDO, font=("Segoe UI", 9, "italic"), fg="#666666", wraplength=600).pack(pady=(0, 10))

        # Tabla de proveedores
        fr_t = tk.Frame(self, bg=COLOR_FONDO)
        fr_t.pack(fill="both", expand=True, padx=20)
        cols = ("nombre","contacto","telefono","cant_productos")
        self.tabla = ttk.Treeview(fr_t, columns=cols, show="headings", height=10)
        for col, txt, w in [("nombre","Proveedor",200),("contacto","Contacto",140),
                              ("telefono","Teléfono",120),("cant_productos","Productos",80)]:
            self.tabla.heading(col, text=txt)
            self.tabla.column(col, width=w, anchor="center" if col=="cant_productos" else "w")
        sc = ttk.Scrollbar(fr_t, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=sc.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        sc.pack(side="right", fill="y")
        self.tabla.bind("<<TreeviewSelect>>", self._seleccionar_proveedor)

        # Panel de ajuste
        fr_ajuste = tk.LabelFrame(self, text="Aplicar ajuste de precio", bg=COLOR_FONDO,
                                   font=("Segoe UI", 10, "bold"), fg=COLOR_PRIMARIO, padx=15, pady=10)
        fr_ajuste.pack(fill="x", padx=20, pady=10)

        self.lbl_proveedor_sel = tk.Label(fr_ajuste, text="Proveedor seleccionado: (ninguno)",
                                           bg=COLOR_FONDO, font=("Segoe UI", 10, "bold"), fg=COLOR_PRIMARIO)
        self.lbl_proveedor_sel.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0,8))

        tk.Label(fr_ajuste, text="Porcentaje:", bg=COLOR_FONDO, font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w")
        self.var_porcentaje = tk.StringVar(value="10")
        tk.Entry(fr_ajuste, textvariable=self.var_porcentaje, font=("Segoe UI", 11), width=10).grid(row=1, column=1, padx=8)
        tk.Label(fr_ajuste, text="%  (positivo = aumento, negativo = reducción)",
                 bg=COLOR_FONDO, font=("Segoe UI", 9, "italic"), fg="#666666").grid(row=1, column=2, sticky="w")

        # Vista previa
        tk.Label(fr_ajuste, text="Vista previa de cambios (primeros 5 productos):",
                 bg=COLOR_FONDO, font=("Segoe UI", 9, "bold")).grid(row=2, column=0, columnspan=4, sticky="w", pady=(10,4))
        cols2 = ("producto","precio_actual","precio_nuevo")
        self.tabla_preview = ttk.Treeview(fr_ajuste, columns=cols2, show="headings", height=5)
        for col, txt, w in [("producto","Producto",280),("precio_actual","Precio actual",120),("precio_nuevo","Precio nuevo",120)]:
            self.tabla_preview.heading(col, text=txt)
            self.tabla_preview.column(col, width=w, anchor="w" if col=="producto" else "center")
        self.tabla_preview.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(0,8))
        self.var_porcentaje.trace_add("write", lambda *a: self._actualizar_preview())

        # Botones
        fr_bot = tk.Frame(fr_ajuste, bg=COLOR_FONDO)
        fr_bot.grid(row=4, column=0, columnspan=4)
        tk.Button(fr_bot, text="✅ Aplicar aumento a TODOS los productos del proveedor",
                  bg="#27AE60", fg="white", font=("Segoe UI", 10, "bold"), relief="flat",
                  cursor="hand2", command=self._aplicar).pack(side="left", padx=6)
        tk.Button(fr_bot, text="Cerrar", bg="#AAAAAA", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                  command=self.destroy).pack(side="left", padx=6)

        self.id_proveedor_sel = None
        self.productos_del_proveedor = []

    def _refrescar(self):
        from database import conectar
        for row in self.tabla.get_children(): self.tabla.delete(row)
        proveedores = self.inventario.obtener_proveedores()
        conn = conectar(); cur = conn.cursor()
        for p in proveedores:
            cur.execute("SELECT COUNT(*) FROM productos WHERE id_proveedor=?", (p.id_proveedor,))
            cant = cur.fetchone()[0]
            self.tabla.insert("", "end", iid=p.id_proveedor,
                               values=(p.nombre, p.contacto or "-", p.telefono or "-", cant))
        conn.close()

    def _seleccionar_proveedor(self, event):
        sel = self.tabla.selection()
        if not sel: return
        self.id_proveedor_sel = int(sel[0])
        nombre = self.tabla.item(sel[0])["values"][0]
        self.lbl_proveedor_sel.config(text=f"Proveedor seleccionado: {nombre}")
        self.productos_del_proveedor = self.inventario.obtener_productos(id_proveedor=self.id_proveedor_sel)
        self._actualizar_preview()

    def _actualizar_preview(self):
        for row in self.tabla_preview.get_children(): self.tabla_preview.delete(row)
        if not self.productos_del_proveedor: return
        try:
            pct = float(self.var_porcentaje.get())
        except:
            return
        factor = 1 + pct / 100
        for p in self.productos_del_proveedor[:5]:
            nuevo = round(p.precio * factor, 2)
            self.tabla_preview.insert("", "end",
                                       values=(p.nombre, f"${p.precio:,.2f}", f"${nuevo:,.2f}"))

    def _aplicar(self):
        if not self.id_proveedor_sel:
            messagebox.showwarning("Atención", "Seleccioná un proveedor de la tabla.", parent=self)
            return
        try:
            pct = float(self.var_porcentaje.get())
        except:
            messagebox.showerror("Error", "Ingresá un porcentaje válido (ej: 10, -5, 15.5).", parent=self)
            return
        nombre_prov = self.tabla.item(self.tabla.selection()[0])["values"][0]
        signo = "aumento" if pct > 0 else "reducción"
        if not messagebox.askyesno("Confirmar",
                                    f"¿Aplicar un {signo} de {abs(pct):.1f}% a TODOS los productos de:\n\n{nombre_prov}?\n\nEsta acción no se puede deshacer.",
                                    parent=self):
            return
        try:
            cant = self.inventario.actualizar_precios_proveedor(self.id_proveedor_sel, pct)
            messagebox.showinfo("Precios actualizados",
                                 f"Se actualizaron {cant} producto(s) de {nombre_prov}\ncon un {signo} del {abs(pct):.1f}%.", parent=self)
            self.productos_del_proveedor = self.inventario.obtener_productos(id_proveedor=self.id_proveedor_sel)
            self._actualizar_preview()
            if self.on_cambio: self.on_cambio()
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self)
