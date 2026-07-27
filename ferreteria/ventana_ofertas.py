"""ventana_ofertas.py - Gestión de ofertas y descuentos por producto."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from modelos import Oferta

COLOR_PRIMARIO = "#2F5496"
COLOR_FONDO = "#F4F6F7"


class VentanaOfertas(tk.Toplevel):
    def __init__(self, master, inventario, on_cambio=None):
        super().__init__(master)
        self.inventario = inventario
        self.on_cambio = on_cambio
        self.title("Ofertas y Descuentos — Ferretería Gian")
        self.geometry("900x560")
        self.configure(bg=COLOR_FONDO)
        self.transient(master)
        self.grab_set()
        self._construir()
        self._refrescar()

    def _construir(self):
        tk.Label(self, text="🏷 Ofertas y Descuentos", font=("Segoe UI", 14, "bold"),
                 bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(pady=(12, 4))
        tk.Label(self, text="Las ofertas se aplican automáticamente en la ventana de venta cuando se cumple la cantidad mínima.",
                 bg=COLOR_FONDO, font=("Segoe UI", 9, "italic"), fg="#666666").pack(pady=(0, 6))

        # Formulario
        fr_form = tk.LabelFrame(self, text="Nueva oferta", bg=COLOR_FONDO,
                                 font=("Segoe UI", 10, "bold"), fg=COLOR_PRIMARIO, padx=12, pady=10)
        fr_form.pack(fill="x", padx=15, pady=6)

        tk.Label(fr_form, text="Producto:", bg=COLOR_FONDO, font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.combo_producto = ttk.Combobox(fr_form, state="readonly", font=("Segoe UI", 10), width=32)
        self.combo_producto.grid(row=0, column=1, columnspan=2, padx=4, sticky="w")

        tk.Label(fr_form, text="Nombre oferta:", bg=COLOR_FONDO, font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", padx=4, pady=4)
        self.var_nombre = tk.StringVar()
        tk.Entry(fr_form, textvariable=self.var_nombre, font=("Segoe UI", 10), width=30).grid(row=1, column=1, padx=4)

        tk.Label(fr_form, text="Tipo:", bg=COLOR_FONDO, font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w", padx=4, pady=4)
        self.var_tipo = tk.StringVar(value="porcentaje")
        tk.Radiobutton(fr_form, text="% de descuento", variable=self.var_tipo, value="porcentaje",
                       bg=COLOR_FONDO, font=("Segoe UI", 10)).grid(row=2, column=1, sticky="w", padx=4)
        tk.Radiobutton(fr_form, text="Precio fijo especial", variable=self.var_tipo, value="precio_fijo",
                       bg=COLOR_FONDO, font=("Segoe UI", 10)).grid(row=2, column=2, sticky="w", padx=4)

        tk.Label(fr_form, text="Valor:", bg=COLOR_FONDO, font=("Segoe UI", 10)).grid(row=3, column=0, sticky="w", padx=4, pady=4)
        self.var_valor = tk.StringVar()
        tk.Entry(fr_form, textvariable=self.var_valor, font=("Segoe UI", 10), width=12).grid(row=3, column=1, padx=4, sticky="w")
        tk.Label(fr_form, text="(ej: 15 para 15% de descuento, o 999 para precio fijo $999)",
                 bg=COLOR_FONDO, font=("Segoe UI", 8), fg="#888888").grid(row=3, column=2, padx=4, sticky="w")

        tk.Label(fr_form, text="Cant. mínima:", bg=COLOR_FONDO, font=("Segoe UI", 10)).grid(row=4, column=0, sticky="w", padx=4, pady=4)
        self.var_cant_min = tk.StringVar(value="1")
        tk.Entry(fr_form, textvariable=self.var_cant_min, font=("Segoe UI", 10), width=8).grid(row=4, column=1, padx=4, sticky="w")
        tk.Label(fr_form, text="(aplica si el cliente compra al menos esta cantidad)",
                 bg=COLOR_FONDO, font=("Segoe UI", 8), fg="#888888").grid(row=4, column=2, padx=4, sticky="w")

        fr_fechas = tk.Frame(fr_form, bg=COLOR_FONDO)
        fr_fechas.grid(row=5, column=0, columnspan=3, sticky="w", padx=4, pady=4)
        tk.Label(fr_fechas, text="Vigencia (opcional):", bg=COLOR_FONDO, font=("Segoe UI", 10)).pack(side="left")
        tk.Label(fr_fechas, text="Desde:", bg=COLOR_FONDO, font=("Segoe UI", 10)).pack(side="left", padx=(8,0))
        self.var_desde = tk.StringVar()
        tk.Entry(fr_fechas, textvariable=self.var_desde, font=("Segoe UI", 10), width=12).pack(side="left", padx=4)
        tk.Label(fr_fechas, text="Hasta:", bg=COLOR_FONDO, font=("Segoe UI", 10)).pack(side="left", padx=(8,0))
        self.var_hasta = tk.StringVar()
        tk.Entry(fr_fechas, textvariable=self.var_hasta, font=("Segoe UI", 10), width=12).pack(side="left", padx=4)
        tk.Label(fr_fechas, text="(formato: AAAA-MM-DD)", bg=COLOR_FONDO, font=("Segoe UI", 8), fg="#888888").pack(side="left")

        tk.Button(fr_form, text="✅ Crear oferta", bg="#27AE60", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                  command=self._crear).grid(row=6, column=0, columnspan=3, pady=8)

        # Tabla de ofertas activas
        tk.Label(self, text="Ofertas activas:", bg=COLOR_FONDO,
                 font=("Segoe UI", 10, "bold"), fg=COLOR_PRIMARIO).pack(anchor="w", padx=15, pady=(6,2))

        fr_t = tk.Frame(self, bg=COLOR_FONDO)
        fr_t.pack(fill="both", expand=True, padx=15, pady=(0,4))
        cols = ("nombre_oferta","producto","tipo","valor","cant_min","desde","hasta")
        self.tabla = ttk.Treeview(fr_t, columns=cols, show="headings", height=7)
        for col, txt, w in [("nombre_oferta","Oferta",140),("producto","Producto",220),
                              ("tipo","Tipo",100),("valor","Valor",80),
                              ("cant_min","Cant. min.",80),("desde","Desde",90),("hasta","Hasta",90)]:
            self.tabla.heading(col, text=txt)
            self.tabla.column(col, width=w, anchor="center" if col in ("valor","cant_min","tipo") else "w")
        sc = ttk.Scrollbar(fr_t, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=sc.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        sc.pack(side="right", fill="y")

        fr_bot = tk.Frame(self, bg=COLOR_FONDO)
        fr_bot.pack(pady=8)
        tk.Button(fr_bot, text="⏸ Desactivar oferta", bg="#D68910", fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  command=self._desactivar).pack(side="left", padx=4)
        tk.Button(fr_bot, text="🗑 Eliminar oferta", bg="#C0392B", fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  command=self._eliminar).pack(side="left", padx=4)
        tk.Button(fr_bot, text="Ver todas (incluidas inactivas)", bg="#AAAAAA", fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  command=self._ver_todas).pack(side="left", padx=4)

        self._cargar_productos()

    def _cargar_productos(self):
        self._productos = self.inventario.obtener_productos()
        self.combo_producto["values"] = [f"[{p.codigo}] {p.nombre}" for p in self._productos]
        if self._productos:
            self.combo_producto.current(0)

    def _refrescar(self, solo_activas=True):
        for row in self.tabla.get_children():
            self.tabla.delete(row)
        self._ofertas = self.inventario.obtener_ofertas(solo_activas=solo_activas)
        for o in self._ofertas:
            tipo_txt = f"Descuento {o.valor:.0f}%" if o.tipo == "porcentaje" else f"Precio ${o.valor:,.2f}"
            self.tabla.insert("", "end", iid=o.id_oferta,
                               values=(o.nombre_oferta, o.nombre_producto, tipo_txt,
                                       o.valor, o.cantidad_minima,
                                       o.fecha_desde or "—", o.fecha_hasta or "—"))

    def _ver_todas(self):
        self._refrescar(solo_activas=False)

    def _crear(self):
        idx = self.combo_producto.current()
        if idx < 0:
            messagebox.showwarning("Atención", "Seleccioná un producto.", parent=self)
            return
        nombre = self.var_nombre.get().strip()
        if not nombre:
            messagebox.showerror("Error", "Ingresá un nombre para la oferta.", parent=self)
            return
        try:
            valor = float(self.var_valor.get())
            if valor <= 0: raise ValueError
        except:
            messagebox.showerror("Error", "Ingresá un valor válido (mayor a 0).", parent=self)
            return
        try:
            cant_min = int(self.var_cant_min.get())
            if cant_min < 1: raise ValueError
        except:
            messagebox.showerror("Error", "Ingresá una cantidad mínima válida.", parent=self)
            return
        producto = self._productos[idx]
        oferta = Oferta(
            id_producto=producto.id_producto,
            nombre_oferta=nombre,
            tipo=self.var_tipo.get(),
            valor=valor,
            cantidad_minima=cant_min,
            fecha_desde=self.var_desde.get() or None,
            fecha_hasta=self.var_hasta.get() or None
        )
        self.inventario.agregar_oferta(oferta)
        messagebox.showinfo("Oferta creada", f"Oferta '{nombre}' creada correctamente.", parent=self)
        self.var_nombre.set(""); self.var_valor.set(""); self.var_cant_min.set("1")
        self.var_desde.set(""); self.var_hasta.set("")
        self._refrescar()
        if self.on_cambio: self.on_cambio()

    def _desactivar(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccioná una oferta.", parent=self)
            return
        self.inventario.desactivar_oferta(int(sel[0]))
        self._refrescar()

    def _eliminar(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccioná una oferta.", parent=self)
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar esta oferta?", parent=self):
            return
        self.inventario.eliminar_oferta(int(sel[0]))
        self._refrescar()
