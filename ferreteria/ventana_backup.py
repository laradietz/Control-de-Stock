"""ventana_backup.py - Ventana para hacer y restaurar backups de la base de datos."""
import tkinter as tk
from tkinter import ttk, messagebox
from backup import hacer_backup, listar_backups, restaurar_backup

COLOR_PRIMARIO = "#2F5496"
COLOR_FONDO = "#F4F6F7"


class VentanaBackup(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Respaldo de datos — Ferretería Gian")
        self.geometry("620x420")
        self.configure(bg=COLOR_FONDO)
        self.transient(master)
        self.grab_set()
        self._construir()
        self._refrescar()

    def _construir(self):
        tk.Label(self, text="💾 Respaldo automático de datos", font=("Segoe UI", 14, "bold"),
                 bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(pady=(15, 4))
        tk.Label(self, text="Los backups se guardan en la carpeta db/backups/ y se eliminan automáticamente después de 30 días.",
                 bg=COLOR_FONDO, font=("Segoe UI", 9, "italic"), fg="#666666", wraplength=560).pack(pady=(0, 10))

        tk.Button(self, text="📦 Hacer backup ahora", bg="#27AE60", fg="white",
                  font=("Segoe UI", 11, "bold"), relief="flat", cursor="hand2",
                  command=self._hacer_backup).pack(pady=4)

        tk.Label(self, text="Backups disponibles:", bg=COLOR_FONDO,
                 font=("Segoe UI", 10, "bold"), fg=COLOR_PRIMARIO).pack(anchor="w", padx=20, pady=(10, 3))

        fr_t = tk.Frame(self, bg=COLOR_FONDO)
        fr_t.pack(fill="both", expand=True, padx=20)
        cols = ("archivo", "fecha", "tamaño")
        self.tabla = ttk.Treeview(fr_t, columns=cols, show="headings", height=10)
        self.tabla.heading("archivo", text="Archivo")
        self.tabla.heading("fecha", text="Fecha")
        self.tabla.heading("tamaño", text="Tamaño")
        self.tabla.column("archivo", width=280)
        self.tabla.column("fecha", width=150, anchor="center")
        self.tabla.column("tamaño", width=90, anchor="center")
        sc = ttk.Scrollbar(fr_t, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=sc.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        sc.pack(side="right", fill="y")

        fr_bot = tk.Frame(self, bg=COLOR_FONDO)
        fr_bot.pack(pady=10)
        tk.Button(fr_bot, text="⚠ Restaurar backup seleccionado", bg="#C0392B", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                  command=self._restaurar).pack(side="left", padx=6)
        tk.Button(fr_bot, text="Cerrar", bg="#AAAAAA", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                  command=self.destroy).pack(side="left", padx=6)

        self.rutas = []

    def _refrescar(self):
        for row in self.tabla.get_children():
            self.tabla.delete(row)
        backups = listar_backups()
        self.rutas = []
        for nombre, fecha, tamaño, ruta in backups:
            self.tabla.insert("", "end", values=(nombre, fecha, tamaño))
            self.rutas.append(ruta)

    def _hacer_backup(self):
        try:
            ruta = hacer_backup()
            messagebox.showinfo("Backup realizado", f"Backup guardado en:\n{ruta}", parent=self)
            self._refrescar()
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)

    def _restaurar(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccioná un backup de la lista.", parent=self)
            return
        idx = self.tabla.index(sel[0])
        ruta = self.rutas[idx]
        if not messagebox.askyesno("Confirmar restauración",
                                    f"¿Restaurar la base de datos desde este backup?\n\n{ruta}\n\n"
                                    "⚠ Los datos actuales se sobreescribirán.\n"
                                    "(Se hará un backup automático del estado actual antes de restaurar.)",
                                    parent=self):
            return
        try:
            restaurar_backup(ruta)
            messagebox.showinfo("Restaurado", "Base de datos restaurada correctamente.\n"
                                               "Reiniciá el programa para que los cambios tomen efecto.", parent=self)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)
