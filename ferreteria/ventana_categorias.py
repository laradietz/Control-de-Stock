"""
ventana_categorias.py
Ventana modal (Toplevel) para gestionar categorías de productos (alta y listado).
"""

import tkinter as tk
from tkinter import ttk, messagebox


class VentanaCategorias(tk.Toplevel):
    """Ventana simple para visualizar y agregar categorías."""

    def __init__(self, master, inventario, on_cambio=None):
        super().__init__(master)
        self.inventario = inventario
        self.on_cambio = on_cambio

        self.title("Gestión de Categorías")
        self.geometry("380x420")
        self.configure(bg="#F4F6F7")
        self.transient(master)
        self.grab_set()

        self._construir_interfaz()
        self._refrescar_lista()

    def _construir_interfaz(self):
        tk.Label(self, text="Categorías de productos", font=("Segoe UI", 13, "bold"),
                 bg="#F4F6F7", fg="#2F5496").pack(pady=(15, 5))

        frame_lista = tk.Frame(self, bg="#F4F6F7")
        frame_lista.pack(fill="both", expand=True, padx=15, pady=5)

        self.lista = tk.Listbox(frame_lista, font=("Segoe UI", 10))
        scroll = ttk.Scrollbar(frame_lista, orient="vertical", command=self.lista.yview)
        self.lista.configure(yscrollcommand=scroll.set)
        self.lista.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        frame_nueva = tk.Frame(self, bg="#F4F6F7")
        frame_nueva.pack(fill="x", padx=15, pady=10)

        tk.Label(frame_nueva, text="Nueva categoría:", bg="#F4F6F7",
                 font=("Segoe UI", 10)).pack(side="left")
        self.var_nueva = tk.StringVar()
        tk.Entry(frame_nueva, textvariable=self.var_nueva, font=("Segoe UI", 10), width=18).pack(
            side="left", padx=8)

        tk.Button(frame_nueva, text="Agregar", bg="#27AE60", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                  command=self._agregar).pack(side="left")

        tk.Button(self, text="Cerrar", bg="#AAAAAA", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", width=12, cursor="hand2",
                  command=self.destroy).pack(pady=(0, 15))

    def _refrescar_lista(self):
        self.lista.delete(0, tk.END)
        for cat in self.inventario.obtener_categorias():
            self.lista.insert(tk.END, cat.nombre)

    def _agregar(self):
        try:
            self.inventario.agregar_categoria(self.var_nueva.get())
            self.var_nueva.set("")
            self._refrescar_lista()
            if self.on_cambio:
                self.on_cambio()
        except ValueError as e:
            messagebox.showerror("Error de validación", str(e), parent=self)
