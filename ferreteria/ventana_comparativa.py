"""ventana_comparativa.py - Comparativa de ventas entre períodos y por forma de pago."""
import tkinter as tk
from tkinter import ttk
from datetime import date

COLOR_PRIMARIO = "#2F5496"
COLOR_FONDO = "#F4F6F7"


class VentanaComparativa(tk.Toplevel):
    def __init__(self, master, inventario):
        super().__init__(master)
        self.inventario = inventario
        self.title("Comparativa de Ventas — Ferretería Gian")
        self.geometry("820x560")
        self.configure(bg=COLOR_FONDO)
        self.transient(master)
        self.grab_set()
        self._construir()
        self._consultar()

    def _construir(self):
        tk.Label(self, text="📊 Comparativa de Ventas", font=("Segoe UI", 14, "bold"),
                 bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(pady=(12, 6))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=6)

        self.tab_comp = tk.Frame(self.notebook, bg=COLOR_FONDO)
        self.notebook.add(self.tab_comp, text="  Mes actual vs mes anterior  ")

        self.tab_formas = tk.Frame(self.notebook, bg=COLOR_FONDO)
        self.notebook.add(self.tab_formas, text="  Ventas por forma de pago  ")

        self.tab_dias = tk.Frame(self.notebook, bg=COLOR_FONDO)
        self.notebook.add(self.tab_dias, text="  Ventas por día (últimos 30 días)  ")

        self._construir_tab_comparativa()
        self._construir_tab_formas()
        self._construir_tab_dias()

        tk.Button(self, text="Cerrar", bg="#AAAAAA", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                  command=self.destroy).pack(pady=8)

    def _construir_tab_comparativa(self):
        tk.Label(self.tab_comp, text="Comparativa automática: mes actual vs mes anterior",
                 bg=COLOR_FONDO, font=("Segoe UI", 10, "italic"), fg="#666666").pack(pady=8)

        self.frame_cards = tk.Frame(self.tab_comp, bg=COLOR_FONDO)
        self.frame_cards.pack(fill="x", padx=20, pady=10)

        self.lbl_cards = {}
        for lado, titulo in [("actual","MES ACTUAL"),("anterior","MES ANTERIOR")]:
            fr = tk.Frame(self.frame_cards, bg=COLOR_PRIMARIO, padx=20, pady=15)
            fr.pack(side="left", expand=True, fill="both", padx=10)
            tk.Label(fr, text=titulo, bg=COLOR_PRIMARIO, fg="white",
                     font=("Segoe UI", 11, "bold")).pack()
            self.lbl_cards[f"{lado}_periodo"] = tk.Label(fr, text="", bg=COLOR_PRIMARIO,
                                                          fg="#BDD7EE", font=("Segoe UI", 8))
            self.lbl_cards[f"{lado}_periodo"].pack()
            self.lbl_cards[f"{lado}_total"] = tk.Label(fr, text="$0", bg=COLOR_PRIMARIO,
                                                        fg="white", font=("Segoe UI", 20, "bold"))
            self.lbl_cards[f"{lado}_total"].pack(pady=4)
            self.lbl_cards[f"{lado}_ventas"] = tk.Label(fr, text="0 ventas", bg=COLOR_PRIMARIO,
                                                         fg="#BDD7EE", font=("Segoe UI", 10))
            self.lbl_cards[f"{lado}_ventas"].pack()

        self.lbl_variacion = tk.Label(self.tab_comp, text="", bg=COLOR_FONDO,
                                       font=("Segoe UI", 16, "bold"))
        self.lbl_variacion.pack(pady=16)

        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            self._fig_comp, self._ax_comp = plt.subplots(figsize=(7, 2.5), facecolor="#F4F6F7")
            self._canvas_comp = FigureCanvasTkAgg(self._fig_comp, master=self.tab_comp)
            self._canvas_comp.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=4)
            self._tiene_matplotlib = True
        except ImportError:
            self._tiene_matplotlib = False

    def _construir_tab_formas(self):
        tk.Label(self.tab_formas, text="Total recaudado por forma de pago (mes actual)",
                 bg=COLOR_FONDO, font=("Segoe UI", 10, "italic"), fg="#666666").pack(pady=8)
        cols = ("forma","total","ventas")
        self.tabla_formas = ttk.Treeview(self.tab_formas, columns=cols, show="headings", height=8)
        for col, txt, w in [("forma","Forma de pago",250),("total","Total recaudado",200),("ventas","Cantidad de ventas",160)]:
            self.tabla_formas.heading(col, text=txt)
            self.tabla_formas.column(col, width=w, anchor="w" if col=="forma" else "center")
        self.tabla_formas.pack(fill="both", expand=True, padx=20, pady=10)

    def _construir_tab_dias(self):
        self.frame_dias = tk.Frame(self.tab_dias, bg=COLOR_FONDO)
        self.frame_dias.pack(fill="both", expand=True, padx=10, pady=10)

    def _consultar(self):
        # Comparativa
        comp = self.inventario.estadisticas_ventas_comparativa()
        a = comp["actual"]; ant = comp["anterior"]
        self.lbl_cards["actual_periodo"].config(text=a["periodo"])
        self.lbl_cards["actual_total"].config(text=f"${a['total']:,.2f}")
        self.lbl_cards["actual_ventas"].config(text=f"{a['ventas']} ventas")
        self.lbl_cards["anterior_periodo"].config(text=ant["periodo"])
        self.lbl_cards["anterior_total"].config(text=f"${ant['total']:,.2f}")
        self.lbl_cards["anterior_ventas"].config(text=f"{ant['ventas']} ventas")
        variacion = comp["variacion_pct"]
        signo = "▲" if variacion >= 0 else "▼"
        color = "#27AE60" if variacion >= 0 else "#C0392B"
        self.lbl_variacion.config(text=f"{signo} {abs(variacion):.1f}% vs mes anterior", fg=color)

        if self._tiene_matplotlib:
            import matplotlib.pyplot as plt
            self._ax_comp.clear()
            periodos = ["Mes anterior", "Mes actual"]
            valores = [ant["total"], a["total"]]
            colores = ["#AAAAAA", "#2F5496"]
            bars = self._ax_comp.bar(periodos, valores, color=colores, alpha=0.85)
            for bar, val in zip(bars, valores):
                self._ax_comp.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(valores)*0.02,
                                    f"${val:,.0f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
            self._ax_comp.set_ylabel("Total ($)"); self._ax_comp.set_title("Comparativa de ventas")
            self._ax_comp.grid(axis="y", alpha=0.3)
            self._ax_comp.set_facecolor("#F4F6F7")
            self._canvas_comp.draw()

        # Formas de pago (del mes actual)
        from datetime import date
        hoy = date.today()
        desde = str(hoy.replace(day=1)); hasta = str(hoy)
        from database import conectar
        conn = conectar(); cur = conn.cursor()
        cur.execute("""SELECT forma_pago, SUM(total), COUNT(*)
                       FROM ventas WHERE anulada=0 AND DATE(fecha) BETWEEN ? AND ?
                       GROUP BY forma_pago ORDER BY SUM(total) DESC""", (desde, hasta))
        formas_data = cur.fetchall(); conn.close()
        for row in self.tabla_formas.get_children(): self.tabla_formas.delete(row)
        nombres = {"efectivo":"Efectivo","tarjeta":"Tarjeta","transferencia":"Transferencia","cuenta_corriente":"Cuenta corriente (fiado)"}
        for forma, total, cant in formas_data:
            self.tabla_formas.insert("", "end", values=(nombres.get(forma, forma), f"${total:,.2f}", cant))

        # Ventas por día (últimos 30 días)
        for w in self.frame_dias.winfo_children(): w.destroy()
        datos = self.inventario.estadisticas_ventas(30)
        if self._tiene_matplotlib:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            fig, ax = plt.subplots(figsize=(7, 3.5), facecolor="#F4F6F7")
            if datos:
                fechas = [d[0] for d in datos]; totales = [d[1] for d in datos]
                ax.bar(fechas, totales, color="#2F5496", alpha=0.8)
                ax.set_title("Recaudación diaria — últimos 30 días", fontsize=11, fontweight="bold")
                ax.set_ylabel("Total ($)"); plt.xticks(rotation=45, ha="right", fontsize=7)
                ax.grid(axis="y", alpha=0.3)
            else:
                ax.text(0.5, 0.5, "Sin datos", ha="center", va="center", transform=ax.transAxes)
            plt.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.frame_dias)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            plt.close(fig)
        else:
            cols = ("fecha","total")
            t = ttk.Treeview(self.frame_dias, columns=cols, show="headings", height=14)
            t.heading("fecha", text="Fecha"); t.heading("total", text="Total ($)")
            t.column("fecha", width=200, anchor="center"); t.column("total", width=200, anchor="center")
            t.pack(fill="both", expand=True)
            for d in datos: t.insert("", "end", values=(d[0], f"${d[1]:,.2f}"))
