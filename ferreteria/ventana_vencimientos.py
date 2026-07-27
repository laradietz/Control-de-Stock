"""ventana_vencimientos.py - Control de vencimiento de productos."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

COLOR_PRIMARIO = "#2F5496"
COLOR_FONDO = "#F4F6F7"


class VentanaVencimientos(tk.Toplevel):
    def __init__(self, master, inventario, on_cambio=None):
        super().__init__(master)
        self.inventario = inventario
        self.on_cambio = on_cambio
        self.title("Control de Vencimientos — Ferretería Gian")
        self.geometry("860x520")
        self.configure(bg=COLOR_FONDO)
        self.transient(master)
        self.grab_set()
        self._construir()
        self._refrescar()

    def _construir(self):
        tk.Label(self, text="📅 Control de Vencimientos", font=("Segoe UI", 14, "bold"),
                 bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(pady=(12, 4))
        tk.Label(self, text="Productos con fecha de vencimiento cargada, ordenados del más próximo al más lejano.",
                 bg=COLOR_FONDO, font=("Segoe UI", 9, "italic"), fg="#666666").pack(pady=(0, 6))

        fr_filtro = tk.Frame(self, bg=COLOR_FONDO)
        fr_filtro.pack(fill="x", padx=15, pady=4)
        tk.Label(fr_filtro, text="Mostrar próximos:", bg=COLOR_FONDO, font=("Segoe UI", 10)).pack(side="left")
        self.var_dias = tk.IntVar(value=30)
        for txt, val in [("30 días",30),("60 días",60),("90 días",90),("Todos",3650)]:
            tk.Radiobutton(fr_filtro, text=txt, variable=self.var_dias, value=val,
                           bg=COLOR_FONDO, font=("Segoe UI", 10),
                           command=self._refrescar).pack(side="left", padx=8)

        fr_t = tk.Frame(self, bg=COLOR_FONDO)
        fr_t.pack(fill="both", expand=True, padx=15, pady=6)
        cols = ("codigo","nombre","categoria","fecha_venc","dias","cantidad","proveedor")
        self.tabla = ttk.Treeview(fr_t, columns=cols, show="headings", height=14)
        for col, txt, w in [("codigo","Código",80),("nombre","Nombre",240),
                              ("categoria","Categoría",120),("fecha_venc","Vencimiento",110),
                              ("dias","Días restantes",110),("cantidad","Stock",60),
                              ("proveedor","Proveedor",140)]:
            self.tabla.heading(col, text=txt)
            self.tabla.column(col, width=w, anchor="center" if col in ("dias","cantidad","fecha_venc","codigo") else "w")
        sc = ttk.Scrollbar(fr_t, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=sc.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        sc.pack(side="right", fill="y")
        self.tabla.tag_configure("vencido", background="#F8D7DA", foreground="#721C24")
        self.tabla.tag_configure("urgente", background="#FFF3CD", foreground="#856404")
        self.tabla.tag_configure("ok", foreground="#155724")

        self.lbl_estado = tk.Label(self, text="", bg=COLOR_FONDO, font=("Segoe UI", 10))
        self.lbl_estado.pack(pady=6)

        fr_bot = tk.Frame(self, bg=COLOR_FONDO)
        fr_bot.pack(pady=4)
        tk.Button(fr_bot, text="Cerrar", bg="#AAAAAA", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                  command=self.destroy).pack()

    def _refrescar(self):
        for row in self.tabla.get_children(): self.tabla.delete(row)
        productos = self.inventario.productos_proximos_vencer(self.var_dias.get())
        vencidos = sum(1 for p in productos if p["vencido"])
        urgentes = sum(1 for p in productos if not p["vencido"] and p["dias_restantes"] is not None and p["dias_restantes"] <= 7)
        for p in productos:
            dias = p["dias_restantes"]
            if p["vencido"]:
                dias_txt = f"VENCIDO ({abs(dias)} días)"
                tag = "vencido"
            elif dias is not None and dias <= 7:
                dias_txt = f"⚠ {dias} días"
                tag = "urgente"
            elif dias is not None:
                dias_txt = f"{dias} días"
                tag = "ok"
            else:
                dias_txt = "—"
                tag = "ok"
            self.tabla.insert("", "end", values=(
                p["codigo"], p["nombre"], p["categoria"],
                p["fecha_vencimiento"], dias_txt, p["cantidad"], p["proveedor"]
            ), tags=(tag,))
        partes = []
        if vencidos: partes.append(f"⛔ {vencidos} vencido(s)")
        if urgentes: partes.append(f"⚠ {urgentes} vence en menos de 7 días")
        if not partes: partes.append(f"✓ Sin vencimientos urgentes en los próximos {self.var_dias.get()} días")
        self.lbl_estado.config(text="   |   ".join(partes),
                                fg="#C0392B" if (vencidos or urgentes) else "#27AE60")
