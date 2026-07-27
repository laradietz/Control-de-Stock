"""ventana_cuenta_corriente.py - Cuenta corriente (fiado) de clientes."""
import tkinter as tk
from tkinter import ttk, messagebox

COLOR_PRIMARIO = "#2F5496"
COLOR_FONDO = "#F4F6F7"


class VentanaCuentaCorriente(tk.Toplevel):
    def __init__(self, master, inventario, usuario="dueño"):
        super().__init__(master)
        self.inventario = inventario
        self.usuario = usuario
        self.title("Cuenta Corriente — Ferretería Gian")
        self.geometry("860x580")
        self.configure(bg=COLOR_FONDO)
        self.transient(master)
        self.grab_set()
        self._construir()
        self._refrescar_deudores()

    def _construir(self):
        tk.Label(self, text="💳 Cuenta Corriente de Clientes", font=("Segoe UI", 14, "bold"),
                 bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(pady=(12, 4))
        tk.Label(self, text="Clientes con saldo pendiente (vendido en forma de pago 'Fiado')",
                 bg=COLOR_FONDO, font=("Segoe UI", 9, "italic"), fg="#666666").pack(pady=(0, 6))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=6)

        self.tab_deudores = tk.Frame(self.notebook, bg=COLOR_FONDO)
        self.notebook.add(self.tab_deudores, text="  Clientes con deuda  ")

        self.tab_movimientos = tk.Frame(self.notebook, bg=COLOR_FONDO)
        self.notebook.add(self.tab_movimientos, text="  Historial del cliente  ")

        self._construir_tab_deudores()
        self._construir_tab_movimientos()

    def _construir_tab_deudores(self):
        cols = ("nombre", "saldo")
        self.tabla_deudores = ttk.Treeview(self.tab_deudores, columns=cols, show="headings", height=14)
        self.tabla_deudores.heading("nombre", text="Cliente")
        self.tabla_deudores.heading("saldo", text="Deuda total")
        self.tabla_deudores.column("nombre", width=380)
        self.tabla_deudores.column("saldo", width=160, anchor="center")
        sc = ttk.Scrollbar(self.tab_deudores, orient="vertical", command=self.tabla_deudores.yview)
        self.tabla_deudores.configure(yscrollcommand=sc.set)
        self.tabla_deudores.pack(side="left", fill="both", expand=True, padx=(10,0), pady=10)
        sc.pack(side="left", fill="y", pady=10)
        self.tabla_deudores.tag_configure("deuda_alta", foreground="#C0392B", font=("Segoe UI", 10, "bold"))
        self.tabla_deudores.bind("<<TreeviewSelect>>", self._seleccionar_cliente)

        fr_bot = tk.Frame(self.tab_deudores, bg=COLOR_FONDO)
        fr_bot.pack(fill="x", padx=10, pady=8)

        tk.Label(fr_bot, text="Registrar pago:", bg=COLOR_FONDO, font=("Segoe UI", 10, "bold")).pack(side="left")
        tk.Label(fr_bot, text="$", bg=COLOR_FONDO, font=("Segoe UI", 10)).pack(side="left", padx=(8,0))
        self.var_pago = tk.StringVar()
        tk.Entry(fr_bot, textvariable=self.var_pago, font=("Segoe UI", 10), width=12).pack(side="left", padx=4)
        tk.Label(fr_bot, text="Descripción:", bg=COLOR_FONDO, font=("Segoe UI", 10)).pack(side="left", padx=(8,0))
        self.var_desc_pago = tk.StringVar(value="Pago en efectivo")
        tk.Entry(fr_bot, textvariable=self.var_desc_pago, font=("Segoe UI", 10), width=22).pack(side="left", padx=4)
        tk.Button(fr_bot, text="✅ Registrar pago", bg="#27AE60", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                  command=self._registrar_pago).pack(side="left", padx=8)

        self.lbl_total_deuda = tk.Label(self.tab_deudores, text="", bg=COLOR_FONDO,
                                         font=("Segoe UI", 11, "bold"), fg="#C0392B")
        self.lbl_total_deuda.pack(pady=4)

    def _construir_tab_movimientos(self):
        fr_sel = tk.Frame(self.tab_movimientos, bg=COLOR_FONDO)
        fr_sel.pack(fill="x", padx=10, pady=8)
        tk.Label(fr_sel, text="Cliente:", bg=COLOR_FONDO, font=("Segoe UI", 10)).pack(side="left")
        self.combo_cliente_hist = ttk.Combobox(fr_sel, state="readonly", font=("Segoe UI", 10), width=30)
        self.combo_cliente_hist.pack(side="left", padx=6)
        self.combo_cliente_hist.bind("<<ComboboxSelected>>", lambda e: self._cargar_historial())

        self.lbl_saldo_cliente = tk.Label(fr_sel, text="", bg=COLOR_FONDO,
                                           font=("Segoe UI", 11, "bold"))
        self.lbl_saldo_cliente.pack(side="left", padx=16)

        cols = ("fecha", "tipo", "monto", "descripcion")
        fr_t = tk.Frame(self.tab_movimientos, bg=COLOR_FONDO)
        fr_t.pack(fill="both", expand=True, padx=10)
        self.tabla_hist = ttk.Treeview(fr_t, columns=cols, show="headings", height=16)
        for col, txt, w in [("fecha","Fecha",150),("tipo","Tipo",90),("monto","Monto",110),("descripcion","Descripción",350)]:
            self.tabla_hist.heading(col, text=txt)
            self.tabla_hist.column(col, width=w, anchor="center" if col in ("tipo","monto") else "w")
        sc = ttk.Scrollbar(fr_t, orient="vertical", command=self.tabla_hist.yview)
        self.tabla_hist.configure(yscrollcommand=sc.set)
        self.tabla_hist.pack(side="left", fill="both", expand=True)
        sc.pack(side="right", fill="y")
        self.tabla_hist.tag_configure("cargo", foreground="#C0392B")
        self.tabla_hist.tag_configure("pago", foreground="#27AE60")

        self._clientes = []
        self._cargar_combo_clientes()

    def _cargar_combo_clientes(self):
        self._clientes = self.inventario.obtener_clientes()
        self.combo_cliente_hist["values"] = [c.nombre for c in self._clientes]
        if self._clientes:
            self.combo_cliente_hist.current(0)
            self._cargar_historial()

    def _refrescar_deudores(self):
        for row in self.tabla_deudores.get_children():
            self.tabla_deudores.delete(row)
        deudores = self.inventario.clientes_con_deuda()
        total = 0
        for id_c, nombre, saldo in deudores:
            tags = ("deuda_alta",) if saldo > 10000 else ()
            self.tabla_deudores.insert("", "end", iid=id_c,
                                        values=(nombre, f"${saldo:,.2f}"), tags=tags)
            total += saldo
        self.lbl_total_deuda.config(text=f"Total en deuda: ${total:,.2f}" if total > 0 else "Sin deudas pendientes ✓")
        self._cargar_combo_clientes()

    def _seleccionar_cliente(self, event):
        sel = self.tabla_deudores.selection()
        if not sel:
            return
        id_c = int(sel[0])
        saldo = self.inventario.obtener_saldo_cliente(id_c)
        self.var_pago.set(f"{saldo:.2f}")

    def _registrar_pago(self):
        sel = self.tabla_deudores.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccioná un cliente de la lista.", parent=self)
            return
        id_c = int(sel[0])
        try:
            monto = float(self.var_pago.get())
        except:
            messagebox.showerror("Error", "Ingresá un monto válido.", parent=self)
            return
        desc = self.var_desc_pago.get() or "Pago"
        try:
            self.inventario.registrar_pago_cuenta(id_c, monto, desc, self.usuario)
            messagebox.showinfo("Pago registrado", f"Pago de ${monto:,.2f} registrado correctamente.", parent=self)
            self.var_pago.set("")
            self._refrescar_deudores()
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self)

    def _cargar_historial(self):
        idx = self.combo_cliente_hist.current()
        if idx < 0 or not self._clientes:
            return
        cliente = self._clientes[idx]
        saldo = self.inventario.obtener_saldo_cliente(cliente.id_cliente)
        color = "#C0392B" if saldo > 0 else "#27AE60"
        self.lbl_saldo_cliente.config(text=f"Saldo: ${saldo:,.2f}", fg=color)
        for row in self.tabla_hist.get_children():
            self.tabla_hist.delete(row)
        for m in self.inventario.obtener_cuenta_corriente(cliente.id_cliente):
            tipo_txt = "CARGO" if m.tipo == "cargo" else "PAGO"
            self.tabla_hist.insert("", "end", values=(m.fecha, tipo_txt, f"${m.monto:,.2f}", m.descripcion),
                                    tags=(m.tipo,))
