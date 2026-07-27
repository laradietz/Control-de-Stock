"""ventana_estadisticas.py - Estadísticas de ventas con gráficos usando matplotlib."""
import tkinter as tk
from tkinter import ttk, messagebox

COLOR_PRIMARIO = "#2F5496"
COLOR_FONDO = "#F4F6F7"

class VentanaEstadisticas(tk.Toplevel):
    def __init__(self, master, inventario):
        super().__init__(master)
        self.inventario = inventario
        self.title("Estadísticas — Ferretería Gian")
        self.geometry("900x580")
        self.configure(bg=COLOR_FONDO)
        self.transient(master)
        self.grab_set()
        self._construir()
        self._cargar()

    def _construir(self):
        tk.Label(self, text="📊 Estadísticas de Ventas", font=("Segoe UI", 14, "bold"),
                 bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(pady=(15, 5))

        # Selector de período
        fr_per = tk.Frame(self, bg=COLOR_FONDO)
        fr_per.pack(pady=5)
        tk.Label(fr_per, text="Período:", bg=COLOR_FONDO, font=("Segoe UI", 10)).pack(side="left")
        self.var_dias = tk.IntVar(value=30)
        for texto, valor in [("Últimos 7 días", 7), ("Últimos 30 días", 30), ("Últimos 90 días", 90)]:
            tk.Radiobutton(fr_per, text=texto, variable=self.var_dias, value=valor,
                           bg=COLOR_FONDO, font=("Segoe UI", 10),
                           command=self._cargar).pack(side="left", padx=8)

        # Notebook con pestañas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=5)

        # Pestaña 1: ventas por día
        self.tab_dias = tk.Frame(self.notebook, bg=COLOR_FONDO)
        self.notebook.add(self.tab_dias, text="  Ventas por día  ")

        # Pestaña 2: productos más vendidos
        self.tab_top = tk.Frame(self.notebook, bg=COLOR_FONDO)
        self.notebook.add(self.tab_top, text="  Productos más vendidos  ")

        # Pestaña 3: stock bajo
        self.tab_stock = tk.Frame(self.notebook, bg=COLOR_FONDO)
        self.notebook.add(self.tab_stock, text="  Alerta de stock  ")

        tk.Button(self, text="Cerrar", bg="#AAAAAA", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", width=12, cursor="hand2",
                  command=self.destroy).pack(pady=8)

    def _cargar(self):
        self._cargar_ventas_por_dia()
        self._cargar_top_productos()
        self._cargar_stock_bajo()

    def _cargar_ventas_por_dia(self):
        for w in self.tab_dias.winfo_children(): w.destroy()
        datos = self.inventario.estadisticas_ventas(self.var_dias.get())

        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

            fig, ax = plt.subplots(figsize=(8, 3.8), facecolor="#F4F6F7")
            if datos:
                fechas = [d[0] for d in datos]
                totales = [d[1] for d in datos]
                ax.bar(fechas, totales, color="#2F5496", alpha=0.8)
                ax.set_title("Recaudación por día ($)", fontsize=12, fontweight="bold")
                ax.set_xlabel("Fecha"); ax.set_ylabel("Total ($)")
                plt.xticks(rotation=45, ha="right", fontsize=7)
                ax.grid(axis="y", alpha=0.3)
                # Total del período
                total_periodo = sum(totales)
                ax.text(0.98, 0.97, f"Total: ${total_periodo:,.2f}", transform=ax.transAxes,
                        ha="right", va="top", fontsize=10, fontweight="bold", color="#2F5496")
            else:
                ax.text(0.5, 0.5, "Sin datos para el período seleccionado",
                        ha="center", va="center", transform=ax.transAxes, fontsize=12, color="#888888")
            plt.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.tab_dias)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            plt.close(fig)
        except ImportError:
            self._tabla_ventas_dias(datos)

    def _tabla_ventas_dias(self, datos):
        """Fallback tabla si no hay matplotlib."""
        cols = ("fecha", "total")
        tabla = ttk.Treeview(self.tab_dias, columns=cols, show="headings", height=15)
        tabla.heading("fecha", text="Fecha"); tabla.heading("total", text="Total ($)")
        tabla.column("fecha", width=200, anchor="center"); tabla.column("total", width=200, anchor="center")
        tabla.pack(fill="both", expand=True, padx=10, pady=10)
        for d in datos:
            tabla.insert("", "end", values=(d[0], f"${d[1]:,.2f}"))

    def _cargar_top_productos(self):
        for w in self.tab_top.winfo_children(): w.destroy()
        datos = self.inventario.productos_mas_vendidos(10)

        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

            fig, ax = plt.subplots(figsize=(8, 3.8), facecolor="#F4F6F7")
            if datos:
                nombres = [d[0][:30] + "..." if len(d[0]) > 30 else d[0] for d in datos]
                cantidades = [d[1] for d in datos]
                colores = ["#2F5496","#27AE60","#C0392B","#D68910","#8E44AD",
                           "#16A085","#E74C3C","#3498DB","#F39C12","#1ABC9C"]
                bars = ax.barh(nombres, cantidades, color=colores[:len(datos)])
                ax.set_title("Productos más vendidos (unidades)", fontsize=12, fontweight="bold")
                ax.set_xlabel("Unidades vendidas")
                for bar, val in zip(bars, cantidades):
                    ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                            str(val), va="center", fontsize=9)
                plt.tight_layout()
            else:
                ax.text(0.5, 0.5, "Sin ventas registradas aún",
                        ha="center", va="center", transform=ax.transAxes, fontsize=12, color="#888888")
            canvas = FigureCanvasTkAgg(fig, master=self.tab_top)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            plt.close(fig)
        except ImportError:
            cols = ("producto", "unidades")
            tabla = ttk.Treeview(self.tab_top, columns=cols, show="headings", height=10)
            tabla.heading("producto", text="Producto"); tabla.heading("unidades", text="Unidades")
            tabla.column("producto", width=350); tabla.column("unidades", width=150, anchor="center")
            tabla.pack(fill="both", expand=True, padx=10, pady=10)
            for d in datos: tabla.insert("", "end", values=(d[0], d[1]))

    def _cargar_stock_bajo(self):
        for w in self.tab_stock.winfo_children(): w.destroy()
        productos = self.inventario.productos_stock_bajo()

        tk.Label(self.tab_stock,
                 text=f"⚠ {len(productos)} producto(s) con stock igual o menor al mínimo",
                 bg="#FFF3CD", fg="#856404", font=("Segoe UI", 11, "bold")).pack(
            fill="x", padx=10, pady=8)

        cols = ("codigo","nombre","categoria","cantidad","minimo","proveedor")
        tabla = ttk.Treeview(self.tab_stock, columns=cols, show="headings", height=14)
        for col, txt, w in [("codigo","Código",90),("nombre","Nombre",240),("categoria","Categoría",130),
                              ("cantidad","Cant.",70),("minimo","Mínimo",70),("proveedor","Proveedor",160)]:
            tabla.heading(col, text=txt)
            tabla.column(col, width=w, anchor="center" if col in ("cantidad","minimo","codigo") else "w")
        sc = ttk.Scrollbar(self.tab_stock, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=sc.set)
        tabla.pack(side="left", fill="both", expand=True, padx=(10,0), pady=(0,10))
        sc.pack(side="right", fill="y", pady=(0,10))
        tabla.tag_configure("bajo", background="#FFC7CE")
        for p in productos:
            tabla.insert("", "end", values=(p.codigo,p.nombre,p.categoria_nombre,
                                             p.cantidad,p.stock_minimo,p.proveedor_nombre), tags=("bajo",))
