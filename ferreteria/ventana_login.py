"""ventana_login.py - Pantalla de inicio de sesión."""
import tkinter as tk
from tkinter import messagebox

COLOR_PRIMARIO = "#2F5496"

class VentanaLogin(tk.Tk):
    def __init__(self, inventario):
        super().__init__()
        self.inventario = inventario
        self.usuario_logueado = None
        self.title("Ferretería Gian — Iniciar sesión")
        self.resizable(False, False)
        self.configure(bg="#F4F6F7")
        self._construir()
        self.update_idletasks()
        x = (self.winfo_screenwidth()//2) - (self.winfo_width()//2)
        y = (self.winfo_screenheight()//2) - (self.winfo_height()//2)
        self.geometry(f"+{x}+{y}")

    def _construir(self):
        tk.Frame(self, bg=COLOR_PRIMARIO, height=8).pack(fill="x")
        frame = tk.Frame(self, bg="#F4F6F7", padx=50, pady=40)
        frame.pack()
        tk.Label(frame, text="🔧 Ferretería Gian", font=("Segoe UI", 18, "bold"),
                 bg="#F4F6F7", fg=COLOR_PRIMARIO).pack(pady=(0, 4))
        tk.Label(frame, text="Sistema de Control de Stock", font=("Segoe UI", 10),
                 bg="#F4F6F7", fg="#777777").pack(pady=(0, 24))

        tk.Label(frame, text="Usuario", font=("Segoe UI", 10), bg="#F4F6F7", anchor="w").pack(fill="x")
        self.var_usuario = tk.StringVar(value="dueño")
        tk.Entry(frame, textvariable=self.var_usuario, font=("Segoe UI", 11), width=28).pack(pady=(2,12))

        tk.Label(frame, text="Contraseña", font=("Segoe UI", 10), bg="#F4F6F7", anchor="w").pack(fill="x")
        self.var_pass = tk.StringVar()
        self.entry_pass = tk.Entry(frame, textvariable=self.var_pass, font=("Segoe UI", 11),
                                    width=28, show="•")
        self.entry_pass.pack(pady=(2, 20))
        self.entry_pass.bind("<Return>", lambda e: self._ingresar())

        tk.Button(frame, text="Ingresar al sistema", bg=COLOR_PRIMARIO, fg="white",
                  font=("Segoe UI", 11, "bold"), relief="flat", width=24, cursor="hand2",
                  command=self._ingresar).pack(pady=(0, 10))

        tk.Label(frame, text="Contraseña por defecto: 1234", font=("Segoe UI", 8, "italic"),
                 bg="#F4F6F7", fg="#AAAAAA").pack()

    def _ingresar(self):
        nombre = self.var_usuario.get().strip()
        password = self.var_pass.get()
        if not nombre or not password:
            messagebox.showerror("Error", "Ingresá usuario y contraseña.", parent=self)
            return
        row = self.inventario.verificar_usuario(nombre, password)
        if row:
            self.usuario_logueado = {"id": row[0], "nombre": row[1], "rol": row[2]}
            self.destroy()
        else:
            messagebox.showerror("Acceso denegado", "Usuario o contraseña incorrectos.", parent=self)
            self.var_pass.set("")
