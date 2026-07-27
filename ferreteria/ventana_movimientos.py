"""ventana_movimientos.py - Registro manual de entradas y salidas de stock."""
import tkinter as tk
from tkinter import ttk, messagebox

COLOR_PRIMARIO = "#2F5496"
COLOR_FONDO = "#F4F6F7"

class VentanaMovimientos(tk.Toplevel):
    def __init__(self, master, inventario, usuario="dueño", on_cambio=None):
        super().__init__(master)
        self.inventario = inventario
        self.usuario = usuario
        self.on_cambio = on_cambio
        self.title("Movimientos de Stock — Ferretería Gian")
        self.geometry("900x560")
        self.configure(bg=COLOR_FONDO)
        self.transient(master)
        self.grab_set()
        self._construir()
        self._refrescar_tabla()

    def _construir(self):
        tk.Label(self, text="📦 Movimientos de Stock", font=("Segoe UI", 14, "bold"),
                 bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(pady=(15, 5))

        # Formulario de nuevo movimiento
        fr_form = tk.LabelFrame(self, text="Registrar movimiento", bg=COLOR_FONDO,
                                 font=("Segoe UI", 10, "bold"), fg=COLOR_PRIMARIO, padx=12, pady=10)
        fr_form.pack(fill="x", padx=15, pady=6)

        tk.Label(fr_form, text="Buscar producto:", bg=COLOR_FONDO, font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", padx=4)
        self.var_busq = tk.StringVar()
        self.var_busq.trace_add("write", lambda *a: self._buscar_producto())
        tk.Entry(fr_form, textvariable=self.var_busq, font=("Segoe UI", 10), width=28).grid(row=0, column=1, padx=4)

        self.combo_producto = ttk.Combobox(fr_form, state="readonly", font=("Segoe UI", 10), width=36)
        self.combo_producto.grid(row=0, column=2, padx=8)

        tk.Label(fr_form, text="Tipo:", bg=COLOR_FONDO, font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", padx=4, pady=6)
        self.var_tipo = tk.StringVar(value="entrada")
        tk.Radiobutton(fr_form, text="Entrada (llegó mercadería)", variable=self.var_tipo, value="entrada",
                       bg=COLOR_FONDO, font=("Segoe UI", 10), fg="#27AE60").grid(row=1, column=1, sticky="w")
        tk.Radiobutton(fr_form, text="Salida (pérdida / ajuste)", variable=self.var_tipo, value="salida",
                       bg=COLOR_FONDO, font=("Segoe UI", 10), fg="#C0392B").grid(row=1, column=2, sticky="w")

        tk.Label(fr_form, text="Cantidad:", bg=COLOR_FONDO, font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w", padx=4)
        self.var_cantidad = tk.StringVar(value="1")
        tk.Entry(fr_form, textvariable=self.var_cantidad, font=("Segoe UI", 10), width=10).grid(row=2, column=1, sticky="w", padx=4)

        tk.Label(fr_form, text="Motivo:", bg=COLOR_FONDO, font=("Segoe UI", 10)).grid(row=3, column=0, sticky="w", padx=4, pady=6)
        self.var_motivo = tk.StringVar()
        tk.Entry(fr_form, textvariable=self.var_motivo, font=("Segoe UI", 10), width=50).grid(row=3, column=1, columnspan=2, sticky="w", padx=4)

        tk.Button(fr_form, text="✅ Registrar movimiento", bg="#27AE60", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                  command=self._registrar).grid(row=4, column=0, columnspan=3, pady=8)

        # Historial de movimientos
        tk.Label(self, text="Historial de movimientos recientes:", bg=COLOR_FONDO,
                 font=("Segoe UI", 10, "bold"), fg=COLOR_PRIMARIO).pack(anchor="w", padx=15, pady=(5,2))

        fr_tabla = tk.Frame(self, bg=COLOR_FONDO)
        fr_tabla.pack(fill="both", expand=True, padx=15, pady=(0,10))

        cols = ("fecha","producto","tipo","cantidad","motivo","usuario")
        self.tabla = ttk.Treeview(fr_tabla, columns=cols, show="headings", height=12)
        for col, txt, w in [("fecha","Fecha",150),("producto","Producto",220),
                              ("tipo","Tipo",80),("cantidad","Cantidad",80),
                              ("motivo","Motivo",220),("usuario","Usuario",90)]:
            self.tabla.heading(col, text=txt)
            self.tabla.column(col, width=w, anchor="center" if col in ("tipo","cantidad") else "w")
        sc = ttk.Scrollbar(fr_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=sc.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        sc.pack(side="right", fill="y")
        self.tabla.tag_configure("entrada", foreground="#27AE60")
        self.tabla.tag_configure("salida", foreground="#C0392B")

        self.productos_lista = []
        self._buscar_producto()

    def _buscar_producto(self):
        texto = self.var_busq.get()
        self.productos_lista = self.inventario.obtener_productos(filtro_texto=texto)
        nombres = [f"[{p.codigo}] {p.nombre} (stock: {p.cantidad})" for p in self.productos_lista]
        self.combo_producto["values"] = nombres
        if nombres:
            self.combo_producto.current(0)

    def _registrar(self):
        idx = self.combo_producto.current()
        if idx < 0 or not self.productos_lista:
            messagebox.showwarning("Atención", "Seleccioná un producto.", parent=self)
            return
        producto = self.productos_lista[idx]
        try:
            cantidad = int(self.var_cantidad.get())
            if cantidad <= 0: raise ValueError
        except:
            messagebox.showerror("Error", "Ingresá una cantidad válida (entero mayor a 0).", parent=self)
            return
        motivo = self.var_motivo.get().strip() or "Sin motivo especificado"
        tipo = self.var_tipo.get()
        try:
            self.inventario.registrar_movimiento(
                producto.id_producto, producto.nombre, tipo, cantidad, motivo, self.usuario)
            self._refrescar_tabla()
            self._buscar_producto()
            self.var_cantidad.set("1")
            self.var_motivo.set("")
            if self.on_cambio: self.on_cambio()
            messagebox.showinfo("Registrado", f"Movimiento de {tipo} registrado correctamente.", parent=self)
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self)

    def _refrescar_tabla(self):
        for row in self.tabla.get_children(): self.tabla.delete(row)
        for mov in self.inventario.obtener_movimientos(limite=200):
            fecha, nombre, tipo, cant, motivo, usuario = mov
            self.tabla.insert("", "end", values=(fecha, nombre, tipo.upper(), cant, motivo, usuario),
                               tags=(tipo,))
