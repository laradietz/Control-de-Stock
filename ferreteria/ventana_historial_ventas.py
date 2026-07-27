"""ventana_historial_ventas.py - Historial de ventas con detalle y opción de anulación."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta
from exportador import generar_boleta_pdf
import subprocess, sys, os

COLOR_PRIMARIO = "#2F5496"
COLOR_FONDO = "#F4F6F7"

class VentanaHistorialVentas(tk.Toplevel):
    def __init__(self, master, inventario, usuario="dueño", on_cambio=None):
        super().__init__(master)
        self.inventario = inventario
        self.usuario = usuario
        self.on_cambio = on_cambio
        self.title("Historial de Ventas — Ferretería Gian")
        self.geometry("950x580")
        self.configure(bg=COLOR_FONDO)
        self.transient(master)
        self.grab_set()
        self._construir()
        self._refrescar()

    def _construir(self):
        tk.Label(self, text="Historial de Ventas", font=("Segoe UI", 14, "bold"),
                 bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(pady=(15, 5))

        # Filtros
        fr = tk.Frame(self, bg=COLOR_FONDO)
        fr.pack(fill="x", padx=15, pady=5)
        tk.Label(fr, text="Desde:", bg=COLOR_FONDO, font=("Segoe UI", 10)).pack(side="left")
        self.var_desde = tk.StringVar(value=str(date.today()))
        tk.Entry(fr, textvariable=self.var_desde, font=("Segoe UI", 10), width=12).pack(side="left", padx=4)
        tk.Label(fr, text="Hasta:", bg=COLOR_FONDO, font=("Segoe UI", 10)).pack(side="left", padx=(10,0))
        self.var_hasta = tk.StringVar(value=str(date.today()))
        tk.Entry(fr, textvariable=self.var_hasta, font=("Segoe UI", 10), width=12).pack(side="left", padx=4)
        tk.Button(fr, text="Buscar", bg=COLOR_PRIMARIO, fg="white", font=("Segoe UI", 9, "bold"),
                  relief="flat", cursor="hand2", command=self._refrescar).pack(side="left", padx=8)
        tk.Button(fr, text="Hoy", bg="#27AE60", fg="white", font=("Segoe UI", 9, "bold"),
                  relief="flat", cursor="hand2", command=self._filtrar_hoy).pack(side="left", padx=2)
        tk.Button(fr, text="Esta semana", bg="#8E44AD", fg="white", font=("Segoe UI", 9, "bold"),
                  relief="flat", cursor="hand2", command=self._filtrar_semana).pack(side="left", padx=2)
        tk.Button(fr, text="Este mes", bg="#D68910", fg="white", font=("Segoe UI", 9, "bold"),
                  relief="flat", cursor="hand2", command=self._filtrar_mes).pack(side="left", padx=2)

        # Tabla ventas
        fr_tabla = tk.Frame(self, bg=COLOR_FONDO)
        fr_tabla.pack(fill="both", expand=True, padx=15, pady=5)
        cols = ("id","fecha","cliente","total","estado")
        self.tabla = ttk.Treeview(fr_tabla, columns=cols, show="headings", height=12)
        for col, txt, w in [("id","N° Venta",80),("fecha","Fecha y Hora",160),
                              ("cliente","Cliente",160),("total","Total",100),("estado","Estado",90)]:
            self.tabla.heading(col, text=txt)
            self.tabla.column(col, width=w, anchor="center" if col in ("id","total","estado") else "w")
        sc = ttk.Scrollbar(fr_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=sc.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        sc.pack(side="right", fill="y")
        self.tabla.tag_configure("anulada", foreground="#AAAAAA")
        self.tabla.bind("<<TreeviewSelect>>", self._mostrar_detalle)

        # Detalle de venta
        tk.Label(self, text="Detalle de la venta seleccionada:", bg=COLOR_FONDO,
                 font=("Segoe UI", 10, "bold"), fg=COLOR_PRIMARIO).pack(anchor="w", padx=15)
        fr_det = tk.Frame(self, bg=COLOR_FONDO)
        fr_det.pack(fill="x", padx=15, pady=(2, 5))
        cols2 = ("producto","precio","cant","subtotal")
        self.tabla_det = ttk.Treeview(fr_det, columns=cols2, show="headings", height=4)
        for col, txt, w in [("producto","Producto",280),("precio","Precio unit.",110),("cant","Cant.",60),("subtotal","Subtotal",110)]:
            self.tabla_det.heading(col, text=txt)
            self.tabla_det.column(col, width=w, anchor="w" if col=="producto" else "center")
        sc2 = ttk.Scrollbar(fr_det, orient="vertical", command=self.tabla_det.yview)
        self.tabla_det.configure(yscrollcommand=sc2.set)
        self.tabla_det.pack(side="left", fill="x", expand=True)
        sc2.pack(side="right", fill="y")

        # Resumen y botones
        fr_bot = tk.Frame(self, bg=COLOR_FONDO)
        fr_bot.pack(fill="x", padx=15, pady=8)
        self.lbl_resumen = tk.Label(fr_bot, text="", bg=COLOR_FONDO, font=("Segoe UI", 10, "bold"), fg=COLOR_PRIMARIO)
        self.lbl_resumen.pack(side="left")
        tk.Button(fr_bot, text="🖨 Reimprimir boleta", bg=COLOR_PRIMARIO, fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  command=self._reimprimir).pack(side="right", padx=4)
        tk.Button(fr_bot, text="❌ Anular venta", bg="#C0392B", fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  command=self._anular).pack(side="right", padx=4)

    def _filtrar_hoy(self):
        hoy = str(date.today())
        self.var_desde.set(hoy); self.var_hasta.set(hoy); self._refrescar()

    def _filtrar_semana(self):
        hoy = date.today()
        self.var_desde.set(str(hoy - timedelta(days=hoy.weekday())))
        self.var_hasta.set(str(hoy)); self._refrescar()

    def _filtrar_mes(self):
        hoy = date.today()
        self.var_desde.set(str(hoy.replace(day=1)))
        self.var_hasta.set(str(hoy)); self._refrescar()

    def _refrescar(self):
        for row in self.tabla.get_children(): self.tabla.delete(row)
        ventas = self.inventario.obtener_ventas(self.var_desde.get(), self.var_hasta.get())
        total_periodo = sum(v.total for v in ventas if not v.anulada)
        for v in ventas:
            estado = "ANULADA" if v.anulada else "OK"
            tags = ("anulada",) if v.anulada else ()
            self.tabla.insert("", "end", iid=v.id_venta,
                               values=(f"{v.id_venta:05d}", v.fecha, v.cliente_nombre,
                                       f"${v.total:,.2f}", estado), tags=tags)
        self.lbl_resumen.config(text=f"Total del período: ${total_periodo:,.2f}  |  {len([v for v in ventas if not v.anulada])} ventas")
        for row in self.tabla_det.get_children(): self.tabla_det.delete(row)

    def _mostrar_detalle(self, event):
        sel = self.tabla.selection()
        if not sel: return
        id_v = int(sel[0])
        for row in self.tabla_det.get_children(): self.tabla_det.delete(row)
        for d in self.inventario.obtener_detalle_venta(id_v):
            self.tabla_det.insert("", "end", values=(d.nombre_producto, f"${d.precio_unitario:,.2f}", d.cantidad, f"${d.subtotal:,.2f}"))

    def _anular(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccioná una venta para anular.", parent=self)
            return
        id_v = int(sel[0])
        if not messagebox.askyesno("Anular venta", f"¿Anular la venta #{id_v:05d}?\nSe devolverá el stock automáticamente.", parent=self):
            return
        try:
            self.inventario.anular_venta(id_v, self.usuario)
            messagebox.showinfo("Anulada", f"Venta #{id_v:05d} anulada. Stock restaurado.", parent=self)
            self._refrescar()
            if self.on_cambio: self.on_cambio()
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self)

    def _reimprimir(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccioná una venta.", parent=self)
            return
        id_v = int(sel[0])
        detalles = self.inventario.obtener_detalle_venta(id_v)
        ventas = self.inventario.obtener_ventas()
        venta = next((v for v in ventas if v.id_venta == id_v), None)
        if not venta: return
        total = sum(d.subtotal for d in detalles)
        try:
            ruta = generar_boleta_pdf(id_v, detalles, total, venta.fecha, venta.cliente_nombre)
            messagebox.showinfo("Boleta generada", f"Guardada en:\n{ruta}", parent=self)
            if sys.platform == "win32": os.startfile(ruta)
            elif sys.platform == "darwin": subprocess.run(["open", ruta])
            else: subprocess.run(["xdg-open", ruta])
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)
