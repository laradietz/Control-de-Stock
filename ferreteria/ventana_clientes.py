"""ventana_clientes.py - Gestión de clientes y su historial de compras."""
import tkinter as tk
from tkinter import ttk, messagebox
from modelos import Cliente

COLOR_PRIMARIO = "#2F5496"
COLOR_FONDO = "#F4F6F7"

class VentanaClientes(tk.Toplevel):
    def __init__(self, master, inventario, on_cambio=None):
        super().__init__(master)
        self.inventario = inventario
        self.on_cambio = on_cambio
        self.title("Gestión de Clientes — Ferretería Gian")
        self.geometry("780x540")
        self.configure(bg=COLOR_FONDO)
        self.transient(master)
        self.grab_set()
        self._construir()
        self._refrescar()

    def _construir(self):
        tk.Label(self, text="👥 Clientes", font=("Segoe UI", 14, "bold"),
                 bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(pady=(15, 5))

        # Búsqueda
        fr_bus = tk.Frame(self, bg=COLOR_FONDO)
        fr_bus.pack(fill="x", padx=15, pady=4)
        tk.Label(fr_bus, text="Buscar:", bg=COLOR_FONDO, font=("Segoe UI", 10)).pack(side="left")
        self.var_busqueda = tk.StringVar()
        self.var_busqueda.trace_add("write", lambda *a: self._refrescar())
        tk.Entry(fr_bus, textvariable=self.var_busqueda, font=("Segoe UI", 10), width=28).pack(side="left", padx=6)

        # Tabla
        fr_t = tk.Frame(self, bg=COLOR_FONDO)
        fr_t.pack(fill="both", expand=True, padx=15)
        cols = ("nombre","telefono","email","direccion","fecha_alta")
        self.tabla = ttk.Treeview(fr_t, columns=cols, show="headings", height=8)
        for col, txt, w in [("nombre","Nombre",160),("telefono","Teléfono",110),
                              ("email","Email",160),("direccion","Dirección",150),("fecha_alta","Alta",90)]:
            self.tabla.heading(col, text=txt)
            self.tabla.column(col, width=w)
        sc = ttk.Scrollbar(fr_t, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=sc.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        sc.pack(side="right", fill="y")
        self.tabla.bind("<<TreeviewSelect>>", self._seleccionar)

        # Formulario
        fr_form = tk.LabelFrame(self, text="Datos del cliente", bg=COLOR_FONDO,
                                 font=("Segoe UI", 10, "bold"), fg=COLOR_PRIMARIO, padx=10, pady=8)
        fr_form.pack(fill="x", padx=15, pady=6)
        campos = [("Nombre *","var_nombre"),("Teléfono","var_tel"),("Email","var_email"),("Dirección","var_dir")]
        self.vars = {}
        for i, (lbl, var) in enumerate(campos):
            tk.Label(fr_form, text=lbl, bg=COLOR_FONDO, font=("Segoe UI", 9)).grid(row=0, column=i*2, sticky="w", padx=4)
            v = tk.StringVar()
            self.vars[var] = v
            tk.Entry(fr_form, textvariable=v, font=("Segoe UI", 9), width=18).grid(row=0, column=i*2+1, padx=4)

        # Historial
        tk.Label(self, text="Historial de compras:", bg=COLOR_FONDO,
                 font=("Segoe UI", 10, "bold"), fg=COLOR_PRIMARIO).pack(anchor="w", padx=15)
        fr_h = tk.Frame(self, bg=COLOR_FONDO)
        fr_h.pack(fill="x", padx=15, pady=(2,6))
        cols2 = ("id","fecha","total","estado")
        self.tabla_hist = ttk.Treeview(fr_h, columns=cols2, show="headings", height=4)
        for col, txt, w in [("id","Venta",70),("fecha","Fecha",160),("total","Total",100),("estado","Estado",80)]:
            self.tabla_hist.heading(col, text=txt)
            self.tabla_hist.column(col, width=w, anchor="center" if col in ("id","total","estado") else "w")
        self.tabla_hist.pack(fill="x")

        # Botones
        fr_bot = tk.Frame(self, bg=COLOR_FONDO)
        fr_bot.pack(pady=8)
        for texto, color, cmd in [
            ("Agregar","#27AE60",self._agregar),
            ("Modificar","#2F5496",self._modificar),
            ("Eliminar","#C0392B",self._eliminar),
            ("Limpiar","#AAAAAA",self._limpiar),
        ]:
            tk.Button(fr_bot, text=texto, bg=color, fg="white", font=("Segoe UI", 10, "bold"),
                      relief="flat", width=10, cursor="hand2", command=cmd).pack(side="left", padx=4)

    def _refrescar(self):
        for row in self.tabla.get_children(): self.tabla.delete(row)
        for c in self.inventario.obtener_clientes(self.var_busqueda.get()):
            self.tabla.insert("", "end", iid=c.id_cliente,
                               values=(c.nombre,c.telefono,c.email,c.direccion,c.fecha_alta))

    def _seleccionar(self, event):
        sel = self.tabla.selection()
        if not sel: return
        v = self.tabla.item(sel[0])["values"]
        self.vars["var_nombre"].set(v[0]); self.vars["var_tel"].set(v[1])
        self.vars["var_email"].set(v[2]); self.vars["var_dir"].set(v[3])
        # Cargar historial
        for row in self.tabla_hist.get_children(): self.tabla_hist.delete(row)
        for r in self.inventario.historial_cliente(int(sel[0])):
            estado = "ANULADA" if r[3] else "OK"
            self.tabla_hist.insert("", "end", values=(f"{r[0]:05d}", r[1], f"${r[2]:,.2f}", estado))

    def _limpiar(self):
        for v in self.vars.values(): v.set("")
        self.tabla.selection_remove(self.tabla.selection())
        for row in self.tabla_hist.get_children(): self.tabla_hist.delete(row)

    def _get_cliente(self, id_cliente=None):
        return Cliente(id_cliente=id_cliente,
                       nombre=self.vars["var_nombre"].get(),
                       telefono=self.vars["var_tel"].get(),
                       email=self.vars["var_email"].get(),
                       direccion=self.vars["var_dir"].get())

    def _agregar(self):
        try:
            self.inventario.agregar_cliente(self._get_cliente())
            self._refrescar(); self._limpiar()
            if self.on_cambio: self.on_cambio()
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self)

    def _modificar(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccioná un cliente.", parent=self); return
        try:
            self.inventario.actualizar_cliente(self._get_cliente(int(sel[0])))
            self._refrescar(); self._limpiar()
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self)

    def _eliminar(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccioná un cliente.", parent=self); return
        if not messagebox.askyesno("Confirmar", "¿Eliminar este cliente?", parent=self): return
        self.inventario.eliminar_cliente(int(sel[0]))
        self._refrescar(); self._limpiar()
