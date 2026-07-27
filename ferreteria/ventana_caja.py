"""ventana_caja.py - Resumen de caja diaria con estadísticas y cierre exportable."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from exportador import exportar_caja_pdf
import subprocess, sys, os

COLOR_PRIMARIO = "#2F5496"
COLOR_FONDO = "#F4F6F7"

class VentanaCaja(tk.Toplevel):
    def __init__(self, master, inventario):
        super().__init__(master)
        self.inventario = inventario
        self.title("Caja Diaria — Ferretería Gian")
        self.geometry("600x540")
        self.configure(bg=COLOR_FONDO)
        self.transient(master)
        self.grab_set()
        self._construir()
        self._refrescar()

    def _construir(self):
        tk.Label(self, text="💰 Caja Diaria", font=("Segoe UI", 14, "bold"),
                 bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(pady=(15, 5))

        fr_fecha = tk.Frame(self, bg=COLOR_FONDO)
        fr_fecha.pack(pady=5)
        tk.Label(fr_fecha, text="Fecha:", bg=COLOR_FONDO, font=("Segoe UI", 10)).pack(side="left")
        self.var_fecha = tk.StringVar(value=str(date.today()))
        tk.Entry(fr_fecha, textvariable=self.var_fecha, font=("Segoe UI", 10), width=14).pack(side="left", padx=6)
        tk.Button(fr_fecha, text="Ver", bg=COLOR_PRIMARIO, fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  command=self._refrescar).pack(side="left")
        tk.Button(fr_fecha, text="Hoy", bg="#27AE60", fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  command=self._ver_hoy).pack(side="left", padx=6)

        # Tarjetas de estadísticas
        self.frame_stats = tk.Frame(self, bg=COLOR_FONDO)
        self.frame_stats.pack(fill="x", padx=20, pady=10)
        self.labels_stats = {}
        for clave, texto, color in [
            ("cantidad_ventas", "Ventas del día", "#27AE60"),
            ("total", "Total recaudado", "#2F5496"),
            ("anuladas", "Ventas anuladas", "#C0392B"),
        ]:
            fr = tk.Frame(self.frame_stats, bg=color, relief="ridge", bd=0)
            fr.pack(side="left", expand=True, fill="both", padx=6, pady=4)
            tk.Label(fr, text=texto, bg=color, fg="white", font=("Segoe UI", 9)).pack(pady=(8,2))
            lbl = tk.Label(fr, text="0", bg=color, fg="white", font=("Segoe UI", 18, "bold"))
            lbl.pack(pady=(0,8))
            self.labels_stats[clave] = lbl

        # Top productos
        tk.Label(self, text="Productos más vendidos hoy:", bg=COLOR_FONDO,
                 font=("Segoe UI", 10, "bold"), fg=COLOR_PRIMARIO).pack(anchor="w", padx=20, pady=(5,2))
        fr_top = tk.Frame(self, bg=COLOR_FONDO)
        fr_top.pack(fill="both", expand=True, padx=20)
        cols = ("producto","unidades")
        self.tabla_top = ttk.Treeview(fr_top, columns=cols, show="headings", height=8)
        self.tabla_top.heading("producto", text="Producto")
        self.tabla_top.heading("unidades", text="Unidades vendidas")
        self.tabla_top.column("producto", width=340)
        self.tabla_top.column("unidades", width=140, anchor="center")
        self.tabla_top.pack(fill="both", expand=True)

        # Botones
        fr_bot = tk.Frame(self, bg=COLOR_FONDO)
        fr_bot.pack(pady=12)
        tk.Button(fr_bot, text="📄 Exportar cierre a PDF", bg="#C0392B", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                  command=self._exportar_pdf).pack(side="left", padx=6)
        tk.Button(fr_bot, text="Cerrar", bg="#AAAAAA", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                  command=self.destroy).pack(side="left", padx=6)

    def _ver_hoy(self):
        self.var_fecha.set(str(date.today()))
        self._refrescar()

    def _refrescar(self):
        resumen = self.inventario.resumen_caja(self.var_fecha.get())
        self.resumen = resumen
        self.labels_stats["cantidad_ventas"].config(text=str(resumen["cantidad_ventas"]))
        self.labels_stats["total"].config(text=f"${resumen['total']:,.2f}")
        self.labels_stats["anuladas"].config(text=str(resumen["anuladas"]))
        for row in self.tabla_top.get_children(): self.tabla_top.delete(row)
        for nombre, cant in resumen["top_productos"]:
            self.tabla_top.insert("", "end", values=(nombre, cant))

    def _exportar_pdf(self):
        try:
            ruta = exportar_caja_pdf(self.resumen)
            messagebox.showinfo("Exportado", f"Cierre guardado en:\n{ruta}", parent=self)
            if sys.platform == "win32": os.startfile(ruta)
            elif sys.platform == "darwin": subprocess.run(["open", ruta])
            else: subprocess.run(["xdg-open", ruta])
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)
