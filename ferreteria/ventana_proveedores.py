"""
ventana_proveedores.py
Ventana modal (Toplevel) para gestionar proveedores: alta, edición y eliminación.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from modelos import Proveedor


class VentanaProveedores(tk.Toplevel):
    """Ventana de administración de proveedores (CRUD)."""

    def __init__(self, master, inventario, on_cambio=None):
        super().__init__(master)
        self.inventario = inventario
        self.on_cambio = on_cambio

        self.title("Gestión de Proveedores")
        self.geometry("650x420")
        self.configure(bg="#F4F6F7")
        self.transient(master)
        self.grab_set()

        self._construir_interfaz()
        self._refrescar_tabla()

    # ------------------------------------------------------------
    def _construir_interfaz(self):
        tk.Label(self, text="Proveedores registrados", font=("Segoe UI", 13, "bold"),
                 bg="#F4F6F7", fg="#2F5496").pack(pady=(15, 5))

        frame_tabla = tk.Frame(self, bg="#F4F6F7")
        frame_tabla.pack(fill="both", expand=True, padx=15)

        columnas = ("nombre", "contacto", "telefono", "email")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=10)
        self.tabla.heading("nombre", text="Nombre")
        self.tabla.heading("contacto", text="Contacto")
        self.tabla.heading("telefono", text="Teléfono")
        self.tabla.heading("email", text="Email")

        self.tabla.column("nombre", width=160)
        self.tabla.column("contacto", width=140)
        self.tabla.column("telefono", width=120)
        self.tabla.column("email", width=180)

        scroll = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Formulario
        frame_form = tk.LabelFrame(self, text="Datos del proveedor", bg="#F4F6F7",
                                    font=("Segoe UI", 10, "bold"), fg="#2F5496", padx=10, pady=10)
        frame_form.pack(fill="x", padx=15, pady=10)

        tk.Label(frame_form, text="Nombre *", bg="#F4F6F7").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        self.var_nombre = tk.StringVar()
        tk.Entry(frame_form, textvariable=self.var_nombre, width=25).grid(row=0, column=1, padx=5, pady=3)

        tk.Label(frame_form, text="Contacto", bg="#F4F6F7").grid(row=0, column=2, sticky="w", padx=5, pady=3)
        self.var_contacto = tk.StringVar()
        tk.Entry(frame_form, textvariable=self.var_contacto, width=25).grid(row=0, column=3, padx=5, pady=3)

        tk.Label(frame_form, text="Teléfono", bg="#F4F6F7").grid(row=1, column=0, sticky="w", padx=5, pady=3)
        self.var_telefono = tk.StringVar()
        tk.Entry(frame_form, textvariable=self.var_telefono, width=25).grid(row=1, column=1, padx=5, pady=3)

        tk.Label(frame_form, text="Email", bg="#F4F6F7").grid(row=1, column=2, sticky="w", padx=5, pady=3)
        self.var_email = tk.StringVar()
        tk.Entry(frame_form, textvariable=self.var_email, width=25).grid(row=1, column=3, padx=5, pady=3)

        # Botones
        frame_botones = tk.Frame(self, bg="#F4F6F7")
        frame_botones.pack(pady=10)

        tk.Button(frame_botones, text="Agregar", bg="#27AE60", fg="white", width=12,
                  relief="flat", font=("Segoe UI", 10, "bold"), cursor="hand2",
                  command=self._agregar).pack(side="left", padx=5)

        tk.Button(frame_botones, text="Modificar", bg="#2F5496", fg="white", width=12,
                  relief="flat", font=("Segoe UI", 10, "bold"), cursor="hand2",
                  command=self._modificar).pack(side="left", padx=5)

        tk.Button(frame_botones, text="Eliminar", bg="#C0392B", fg="white", width=12,
                  relief="flat", font=("Segoe UI", 10, "bold"), cursor="hand2",
                  command=self._eliminar).pack(side="left", padx=5)

        tk.Button(frame_botones, text="Limpiar campos", bg="#AAAAAA", fg="white", width=14,
                  relief="flat", font=("Segoe UI", 10, "bold"), cursor="hand2",
                  command=self._limpiar).pack(side="left", padx=5)

        self.tabla.bind("<<TreeviewSelect>>", self._seleccionar_fila)

    # ------------------------------------------------------------
    def _refrescar_tabla(self):
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        for prov in self.inventario.obtener_proveedores():
            self.tabla.insert("", "end", iid=prov.id_proveedor,
                               values=(prov.nombre, prov.contacto, prov.telefono, prov.email))

    def _seleccionar_fila(self, event):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        item = self.tabla.item(seleccion[0])
        valores = item["values"]
        self.var_nombre.set(valores[0])
        self.var_contacto.set(valores[1])
        self.var_telefono.set(valores[2])
        self.var_email.set(valores[3])

    def _limpiar(self):
        self.var_nombre.set("")
        self.var_contacto.set("")
        self.var_telefono.set("")
        self.var_email.set("")
        self.tabla.selection_remove(self.tabla.selection())

    def _obtener_id_seleccionado(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            return None
        return int(seleccion[0])

    # ------------------------------------------------------------
    def _agregar(self):
        proveedor = Proveedor(
            nombre=self.var_nombre.get(),
            contacto=self.var_contacto.get(),
            telefono=self.var_telefono.get(),
            email=self.var_email.get()
        )
        try:
            self.inventario.agregar_proveedor(proveedor)
            self._refrescar_tabla()
            self._limpiar()
            if self.on_cambio:
                self.on_cambio()
        except ValueError as e:
            messagebox.showerror("Error de validación", str(e), parent=self)

    def _modificar(self):
        id_sel = self._obtener_id_seleccionado()
        if not id_sel:
            messagebox.showwarning("Atención", "Seleccione un proveedor de la tabla para modificar.", parent=self)
            return
        proveedor = Proveedor(
            id_proveedor=id_sel,
            nombre=self.var_nombre.get(),
            contacto=self.var_contacto.get(),
            telefono=self.var_telefono.get(),
            email=self.var_email.get()
        )
        try:
            self.inventario.actualizar_proveedor(proveedor)
            self._refrescar_tabla()
            self._limpiar()
            if self.on_cambio:
                self.on_cambio()
        except ValueError as e:
            messagebox.showerror("Error de validación", str(e), parent=self)

    def _eliminar(self):
        id_sel = self._obtener_id_seleccionado()
        if not id_sel:
            messagebox.showwarning("Atención", "Seleccione un proveedor de la tabla para eliminar.", parent=self)
            return
        if not messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este proveedor?\n"
                                                  "Los productos asociados quedarán sin proveedor.", parent=self):
            return
        try:
            self.inventario.eliminar_proveedor(id_sel)
            self._refrescar_tabla()
            self._limpiar()
            if self.on_cambio:
                self.on_cambio()
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self)
