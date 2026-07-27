"""ventana_usuarios.py - Gestión de usuarios y cambio de contraseña."""
import tkinter as tk
from tkinter import ttk, messagebox

COLOR_PRIMARIO = "#2F5496"
COLOR_FONDO = "#F4F6F7"


class VentanaUsuarios(tk.Toplevel):
    def __init__(self, master, inventario, usuario_actual=None):
        super().__init__(master)
        self.inventario = inventario
        self.usuario_actual = usuario_actual or {}
        self.title("Gestión de Usuarios — Ferretería Gian")
        self.geometry("600x480")
        self.configure(bg=COLOR_FONDO)
        self.transient(master)
        self.grab_set()
        self._construir()
        self._refrescar()

    def _construir(self):
        tk.Label(self, text="🔐 Usuarios del sistema", font=("Segoe UI", 14, "bold"),
                 bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(pady=(15, 8))

        # Tabla
        fr_t = tk.Frame(self, bg=COLOR_FONDO)
        fr_t.pack(fill="both", expand=True, padx=20)
        cols = ("nombre", "rol")
        self.tabla = ttk.Treeview(fr_t, columns=cols, show="headings", height=8)
        self.tabla.heading("nombre", text="Usuario")
        self.tabla.heading("rol", text="Rol")
        self.tabla.column("nombre", width=260)
        self.tabla.column("rol", width=160, anchor="center")
        sc = ttk.Scrollbar(fr_t, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=sc.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        sc.pack(side="right", fill="y")
        self.tabla.bind("<<TreeviewSelect>>", self._seleccionar)

        # Formulario
        fr_form = tk.LabelFrame(self, text="Agregar / modificar usuario", bg=COLOR_FONDO,
                                 font=("Segoe UI", 10, "bold"), fg=COLOR_PRIMARIO, padx=12, pady=10)
        fr_form.pack(fill="x", padx=20, pady=8)

        tk.Label(fr_form, text="Nombre de usuario:", bg=COLOR_FONDO, font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", padx=4, pady=3)
        self.var_nombre = tk.StringVar()
        tk.Entry(fr_form, textvariable=self.var_nombre, font=("Segoe UI", 10), width=20).grid(row=0, column=1, padx=4)

        tk.Label(fr_form, text="Contraseña:", bg=COLOR_FONDO, font=("Segoe UI", 10)).grid(row=0, column=2, sticky="w", padx=4)
        self.var_pass = tk.StringVar()
        tk.Entry(fr_form, textvariable=self.var_pass, font=("Segoe UI", 10), width=18, show="•").grid(row=0, column=3, padx=4)

        tk.Label(fr_form, text="Rol:", bg=COLOR_FONDO, font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", padx=4, pady=3)
        self.var_rol = tk.StringVar(value="empleado")
        ttk.Combobox(fr_form, textvariable=self.var_rol, values=["dueño", "empleado"],
                     state="readonly", font=("Segoe UI", 10), width=15).grid(row=1, column=1, padx=4, sticky="w")

        # Botones
        fr_bot = tk.Frame(self, bg=COLOR_FONDO)
        fr_bot.pack(pady=8)
        for texto, color, cmd in [
            ("Agregar", "#27AE60", self._agregar),
            ("Cambiar contraseña", "#2F5496", self._cambiar_pass),
            ("Eliminar", "#C0392B", self._eliminar),
            ("Limpiar", "#AAAAAA", self._limpiar),
        ]:
            tk.Button(fr_bot, text=texto, bg=color, fg="white", font=("Segoe UI", 9, "bold"),
                      relief="flat", padx=10, cursor="hand2", command=cmd).pack(side="left", padx=4)

    def _refrescar(self):
        for row in self.tabla.get_children():
            self.tabla.delete(row)
        for u in self.inventario.obtener_usuarios():
            self.tabla.insert("", "end", iid=u[0], values=(u[1], u[2]))

    def _seleccionar(self, event):
        sel = self.tabla.selection()
        if not sel:
            return
        v = self.tabla.item(sel[0])["values"]
        self.var_nombre.set(v[0])
        self.var_rol.set(v[1])

    def _limpiar(self):
        self.var_nombre.set("")
        self.var_pass.set("")
        self.var_rol.set("empleado")
        self.tabla.selection_remove(self.tabla.selection())

    def _agregar(self):
        nombre = self.var_nombre.get().strip()
        password = self.var_pass.get()
        rol = self.var_rol.get()
        if not nombre or not password:
            messagebox.showerror("Error", "Nombre y contraseña son obligatorios.", parent=self)
            return
        try:
            self.inventario.agregar_usuario(nombre, password, rol)
            messagebox.showinfo("Usuario creado", f"Usuario '{nombre}' creado con rol '{rol}'.", parent=self)
            self._refrescar()
            self._limpiar()
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self)

    def _cambiar_pass(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccioná un usuario de la tabla.", parent=self)
            return
        nueva = self.var_pass.get()
        if not nueva:
            messagebox.showerror("Error", "Ingresá la nueva contraseña.", parent=self)
            return
        id_u = int(sel[0])
        self.inventario.cambiar_password(id_u, nueva)
        messagebox.showinfo("Actualizado", "Contraseña cambiada correctamente.", parent=self)
        self._limpiar()

    def _eliminar(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccioná un usuario.", parent=self)
            return
        nombre = self.tabla.item(sel[0])["values"][0]
        if nombre == self.usuario_actual.get("nombre"):
            messagebox.showerror("Error", "No podés eliminar tu propio usuario.", parent=self)
            return
        if not messagebox.askyesno("Confirmar", f"¿Eliminar el usuario '{nombre}'?", parent=self):
            return
        try:
            self.inventario.eliminar_usuario(int(sel[0]))
            self._refrescar()
            self._limpiar()
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self)
