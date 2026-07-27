"""
ventana_producto.py
Ventana modal (Toplevel) para dar de alta o editar un producto.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from modelos import Producto


class VentanaProducto(tk.Toplevel):
    """
    Ventana emergente con formulario para crear o editar un Producto.

    Parámetros:
        master: ventana padre.
        inventario: instancia de Inventario (lógica de negocio).
        on_guardar: callback sin argumentos, ejecutado tras guardar con éxito.
        producto: objeto Producto a editar (None para alta nueva).
    """

    def __init__(self, master, inventario, on_guardar, producto=None):
        super().__init__(master)
        self.inventario = inventario
        self.on_guardar = on_guardar
        self.producto = producto
        self.es_edicion = producto is not None

        self.title("Editar producto" if self.es_edicion else "Nuevo producto")
        self.resizable(False, False)
        self.configure(bg="#F4F6F7")
        self.transient(master)
        self.grab_set()

        self._construir_formulario()
        self._cargar_combos()

        if self.es_edicion:
            self._cargar_datos_producto()

        self.update_idletasks()
        self._centrar()

    def _centrar(self):
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f"+{x}+{y}")

    def _construir_formulario(self):
        contenedor = tk.Frame(self, bg="#F4F6F7", padx=20, pady=20)
        contenedor.pack()

        titulo = "Editar Producto" if self.es_edicion else "Nuevo Producto"
        tk.Label(contenedor, text=titulo, font=("Segoe UI", 14, "bold"),
                 bg="#F4F6F7", fg="#2F5496").grid(row=0, column=0, columnspan=2, pady=(0, 15))

        etiquetas_estilo = {"bg": "#F4F6F7", "font": ("Segoe UI", 10), "anchor": "w"}
        entry_estilo = {"font": ("Segoe UI", 10), "width": 32}

        # Código
        tk.Label(contenedor, text="Código *", **etiquetas_estilo).grid(row=1, column=0, sticky="w", pady=4)
        self.var_codigo = tk.StringVar()
        tk.Entry(contenedor, textvariable=self.var_codigo, **entry_estilo).grid(row=1, column=1, pady=4)

        # Nombre
        tk.Label(contenedor, text="Nombre *", **etiquetas_estilo).grid(row=2, column=0, sticky="w", pady=4)
        self.var_nombre = tk.StringVar()
        tk.Entry(contenedor, textvariable=self.var_nombre, **entry_estilo).grid(row=2, column=1, pady=4)

        # Categoría
        tk.Label(contenedor, text="Categoría", **etiquetas_estilo).grid(row=3, column=0, sticky="w", pady=4)
        self.combo_categoria = ttk.Combobox(contenedor, state="readonly",
                                             font=("Segoe UI", 10), width=30)
        self.combo_categoria.grid(row=3, column=1, pady=4)

        # Proveedor
        tk.Label(contenedor, text="Proveedor", **etiquetas_estilo).grid(row=4, column=0, sticky="w", pady=4)
        self.combo_proveedor = ttk.Combobox(contenedor, state="readonly",
                                             font=("Segoe UI", 10), width=30)
        self.combo_proveedor.grid(row=4, column=1, pady=4)

        # Precio
        tk.Label(contenedor, text="Precio ($) *", **etiquetas_estilo).grid(row=5, column=0, sticky="w", pady=4)
        self.var_precio = tk.StringVar()
        tk.Entry(contenedor, textvariable=self.var_precio, **entry_estilo).grid(row=5, column=1, pady=4)

        # Cantidad
        tk.Label(contenedor, text="Cantidad disponible *", **etiquetas_estilo).grid(row=6, column=0, sticky="w", pady=4)
        self.var_cantidad = tk.StringVar()
        tk.Entry(contenedor, textvariable=self.var_cantidad, **entry_estilo).grid(row=6, column=1, pady=4)

        # Stock mínimo
        tk.Label(contenedor, text="Stock mínimo *", **etiquetas_estilo).grid(row=7, column=0, sticky="w", pady=4)
        self.var_stock_min = tk.StringVar(value="5")
        tk.Entry(contenedor, textvariable=self.var_stock_min, **entry_estilo).grid(row=7, column=1, pady=4)

        # Precio de costo
        tk.Label(contenedor, text="Precio de costo ($)", **etiquetas_estilo).grid(row=8, column=0, sticky="w", pady=4)
        self.var_precio_costo = tk.StringVar(value="0")
        tk.Entry(contenedor, textvariable=self.var_precio_costo, **entry_estilo).grid(row=8, column=1, pady=4)

        # Ubicación en el local
        tk.Label(contenedor, text="Ubicación / Góndola", **etiquetas_estilo).grid(row=9, column=0, sticky="w", pady=4)
        self.var_ubicacion = tk.StringVar()
        tk.Entry(contenedor, textvariable=self.var_ubicacion, **entry_estilo).grid(row=9, column=1, pady=4)

        # Fecha de vencimiento
        tk.Label(contenedor, text="Vencimiento (AAAA-MM-DD)", **etiquetas_estilo).grid(row=10, column=0, sticky="w", pady=4)
        self.var_vencimiento = tk.StringVar()
        tk.Entry(contenedor, textvariable=self.var_vencimiento, **entry_estilo).grid(row=10, column=1, pady=4)

        tk.Label(contenedor, text="* Campos obligatorios  |  Precio de costo: necesario para reporte de ganancias", bg="#F4F6F7",
                 font=("Segoe UI", 8, "italic"), fg="#888888").grid(
            row=11, column=0, columnspan=2, sticky="w", pady=(2, 10))

        # Botones
        frame_botones = tk.Frame(contenedor, bg="#F4F6F7")
        frame_botones.grid(row=12, column=0, columnspan=2, pady=(5, 0))

        tk.Button(frame_botones, text="Guardar", bg="#2F5496", fg="white",
                  font=("Segoe UI", 10, "bold"), width=12, relief="flat",
                  cursor="hand2", command=self._guardar).pack(side="left", padx=5)

        tk.Button(frame_botones, text="Cancelar", bg="#AAAAAA", fg="white",
                  font=("Segoe UI", 10, "bold"), width=12, relief="flat",
                  cursor="hand2", command=self.destroy).pack(side="left", padx=5)

    def _cargar_combos(self):
        self.categorias = self.inventario.obtener_categorias()
        self.proveedores = self.inventario.obtener_proveedores()

        self.combo_categoria["values"] = ["(Sin categoría)"] + [c.nombre for c in self.categorias]
        self.combo_proveedor["values"] = ["(Sin proveedor)"] + [p.nombre for p in self.proveedores]

        self.combo_categoria.current(0)
        self.combo_proveedor.current(0)

    def _cargar_datos_producto(self):
        p = self.producto
        self.var_codigo.set(p.codigo)
        self.var_nombre.set(p.nombre)
        self.var_precio.set(str(p.precio))
        self.var_cantidad.set(str(p.cantidad))
        self.var_stock_min.set(str(p.stock_minimo))
        self.var_precio_costo.set(str(getattr(p, "precio_costo", 0)))
        self.var_ubicacion.set(getattr(p, "ubicacion", "") or "")
        self.var_vencimiento.set(getattr(p, "fecha_vencimiento", "") or "")

        if p.id_categoria:
            for i, c in enumerate(self.categorias):
                if c.id_categoria == p.id_categoria:
                    self.combo_categoria.current(i + 1); break
        if p.id_proveedor:
            for i, pr in enumerate(self.proveedores):
                if pr.id_proveedor == p.id_proveedor:
                    self.combo_proveedor.current(i + 1); break

    def _guardar(self):
        idx_cat = self.combo_categoria.current()
        id_categoria = self.categorias[idx_cat - 1].id_categoria if idx_cat > 0 else None
        idx_prov = self.combo_proveedor.current()
        id_proveedor = self.proveedores[idx_prov - 1].id_proveedor if idx_prov > 0 else None

        try:
            precio_costo = float(self.var_precio_costo.get() or 0)
        except:
            precio_costo = 0

        venc = self.var_vencimiento.get().strip() or None

        producto = Producto(
            id_producto=self.producto.id_producto if self.es_edicion else None,
            codigo=self.var_codigo.get(),
            nombre=self.var_nombre.get(),
            id_categoria=id_categoria,
            precio=self.var_precio.get(),
            cantidad=self.var_cantidad.get(),
            stock_minimo=self.var_stock_min.get(),
            id_proveedor=id_proveedor
        )
        producto.precio_costo = precio_costo
        producto.ubicacion = self.var_ubicacion.get().strip()
        producto.fecha_vencimiento = venc

        try:
            if self.es_edicion:
                self.inventario.actualizar_producto(producto)
                messagebox.showinfo("Éxito", "Producto actualizado correctamente.", parent=self)
            else:
                self.inventario.agregar_producto(producto)
                messagebox.showinfo("Éxito", "Producto agregado correctamente.", parent=self)
            self.on_guardar()
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Error de validación", str(e), parent=self)
