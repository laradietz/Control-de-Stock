"""ventana_ganancias.py - Reporte de ganancias y rentabilidad por período."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

COLOR_PRIMARIO = "#2F5496"
COLOR_FONDO = "#F4F6F7"


class VentanaGanancias(tk.Toplevel):
    def __init__(self, master, inventario):
        super().__init__(master)
        self.inventario = inventario
        self.title("Ganancias y Rentabilidad — Ferretería Gian")
        self.geometry("920x600")
        self.configure(bg=COLOR_FONDO)
        self.transient(master)
        self.grab_set()
        self._construir()
        self._consultar()

    def _construir(self):
        tk.Label(self, text="📈 Reporte de Ganancias", font=("Segoe UI", 14, "bold"),
                 bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(pady=(12, 4))
        tk.Label(self, text="Requiere tener cargado el 'precio de costo' en cada producto para calcular la ganancia real.",
                 bg=COLOR_FONDO, font=("Segoe UI", 9, "italic"), fg="#856404").pack(fill="x", padx=15, pady=(0, 6))

        # Filtros de fecha
        fr_filtro = tk.Frame(self, bg=COLOR_FONDO)
        fr_filtro.pack(fill="x", padx=15, pady=6)
        tk.Label(fr_filtro, text="Desde:", bg=COLOR_FONDO, font=("Segoe UI", 10)).pack(side="left")
        self.var_desde = tk.StringVar(value=str(date.today().replace(day=1)))
        tk.Entry(fr_filtro, textvariable=self.var_desde, font=("Segoe UI", 10), width=12).pack(side="left", padx=4)
        tk.Label(fr_filtro, text="Hasta:", bg=COLOR_FONDO, font=("Segoe UI", 10)).pack(side="left", padx=(8,0))
        self.var_hasta = tk.StringVar(value=str(date.today()))
        tk.Entry(fr_filtro, textvariable=self.var_hasta, font=("Segoe UI", 10), width=12).pack(side="left", padx=4)
        tk.Button(fr_filtro, text="Consultar", bg=COLOR_PRIMARIO, fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  command=self._consultar).pack(side="left", padx=8)
        tk.Button(fr_filtro, text="Este mes", bg="#27AE60", fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  command=self._filtrar_mes).pack(side="left", padx=2)

        # Tarjetas de resumen
        self.frame_resumen = tk.Frame(self, bg=COLOR_FONDO)
        self.frame_resumen.pack(fill="x", padx=15, pady=6)
        self.labels_resumen = {}
        for clave, texto, color in [
            ("total_ingresos", "Ingresos totales", "#2F5496"),
            ("total_costo", "Costo total", "#C0392B"),
            ("ganancia_total", "Ganancia neta", "#27AE60"),
        ]:
            fr = tk.Frame(self.frame_resumen, bg=color)
            fr.pack(side="left", expand=True, fill="both", padx=6, pady=4)
            tk.Label(fr, text=texto, bg=color, fg="white", font=("Segoe UI", 9)).pack(pady=(8,2))
            lbl = tk.Label(fr, text="$0", bg=color, fg="white", font=("Segoe UI", 16, "bold"))
            lbl.pack(pady=(0,8))
            self.labels_resumen[clave] = lbl

        # Tabla detalle
        tk.Label(self, text="Detalle por producto:", bg=COLOR_FONDO,
                 font=("Segoe UI", 10, "bold"), fg=COLOR_PRIMARIO).pack(anchor="w", padx=15, pady=(4,2))
        fr_t = tk.Frame(self, bg=COLOR_FONDO)
        fr_t.pack(fill="both", expand=True, padx=15, pady=(0,10))
        cols = ("producto","unidades","ingresos","costo","ganancia","margen")
        self.tabla = ttk.Treeview(fr_t, columns=cols, show="headings", height=12)
        for col, txt, w in [("producto","Producto",260),("unidades","Unidades",80),
                              ("ingresos","Ingresos",100),("costo","Costo",100),
                              ("ganancia","Ganancia",100),("margen","Margen %",90)]:
            self.tabla.heading(col, text=txt, command=lambda c=col: self._ordenar(c))
            self.tabla.column(col, width=w, anchor="w" if col=="producto" else "center")
        sc = ttk.Scrollbar(fr_t, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=sc.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        sc.pack(side="right", fill="y")
        self.tabla.tag_configure("positivo", foreground="#27AE60")
        self.tabla.tag_configure("negativo", foreground="#C0392B")
        self._orden_col = None; self._orden_asc = True
        self._datos = []

    def _filtrar_mes(self):
        self.var_desde.set(str(date.today().replace(day=1)))
        self.var_hasta.set(str(date.today()))
        self._consultar()

    def _consultar(self):
        rep = self.inventario.reporte_ganancias(self.var_desde.get(), self.var_hasta.get())
        self._datos = rep["detalle"]
        self.labels_resumen["total_ingresos"].config(text=f"${rep['total_ingresos']:,.2f}")
        self.labels_resumen["total_costo"].config(text=f"${rep['total_costo']:,.2f}")
        ganancia = rep["ganancia_total"]
        self.labels_resumen["ganancia_total"].config(
            text=f"${ganancia:,.2f}",
            fg="white" if ganancia >= 0 else "#FFD700")
        self._poblar_tabla()

    def _poblar_tabla(self):
        for row in self.tabla.get_children(): self.tabla.delete(row)
        for d in self._datos:
            tag = "positivo" if d["ganancia"] >= 0 else "negativo"
            self.tabla.insert("", "end", values=(
                d["nombre"], d["unidades"],
                f"${d['ingresos']:,.2f}", f"${d['costo_total']:,.2f}",
                f"${d['ganancia']:,.2f}", f"{d['margen']:.1f}%"
            ), tags=(tag,))

    def _ordenar(self, col):
        indices = {"producto":0,"unidades":1,"ingresos":2,"costo":3,"ganancia":4,"margen":5}
        keys = {"producto":"nombre","unidades":"unidades","ingresos":"ingresos",
                "costo":"costo_total","ganancia":"ganancia","margen":"margen"}
        rev = self._orden_col == col and self._orden_asc
        self._orden_col = col; self._orden_asc = not rev
        self._datos.sort(key=lambda d: d[keys[col]], reverse=rev)
        self._poblar_tabla()
