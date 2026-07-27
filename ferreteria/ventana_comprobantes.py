"""ventana_comprobantes.py - Carga y consulta de comprobantes (facturas/remitos) de proveedores."""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil
import subprocess
import sys
from datetime import datetime
from modelos import Comprobante

COLOR_PRIMARIO = "#2F5496"
COLOR_FONDO = "#F4F6F7"

COMPROBANTES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports", "comprobantes")
EXTENSIONES_VALIDAS = (".pdf", ".jpg", ".jpeg", ".png")


class VentanaComprobantes(tk.Toplevel):
    def __init__(self, master, inventario, usuario="dueño"):
        super().__init__(master)
        self.inventario = inventario
        self.usuario = usuario
        self.title("Comprobantes de Compra — Ferretería Gian")
        self.geometry("900x600")
        self.configure(bg=COLOR_FONDO)
        self.transient(master)
        self.grab_set()
        os.makedirs(COMPROBANTES_DIR, exist_ok=True)
        self._construir()
        self._cargar_proveedores()
        self._refrescar()

    def _construir(self):
        tk.Label(self, text="🧾 Comprobantes de Compra a Proveedores", font=("Segoe UI", 14, "bold"),
                 bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(pady=(12, 4))
        tk.Label(self, text="Subí facturas, remitos o fotos de comprobantes que te entregan los proveedores, como respaldo.",
                 bg=COLOR_FONDO, font=("Segoe UI", 9, "italic"), fg="#666666").pack(pady=(0, 8))

        fr_form = tk.LabelFrame(self, text="Subir nuevo comprobante", bg=COLOR_FONDO,
                                 font=("Segoe UI", 10, "bold"), fg=COLOR_PRIMARIO, padx=12, pady=10)
        fr_form.pack(fill="x", padx=15, pady=6)

        tk.Label(fr_form, text="Proveedor:", bg=COLOR_FONDO, font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.combo_prov = ttk.Combobox(fr_form, state="readonly", font=("Segoe UI", 10), width=25)
        self.combo_prov.grid(row=0, column=1, padx=4, sticky="w")

        tk.Label(fr_form, text="N° comprobante:", bg=COLOR_FONDO, font=("Segoe UI", 10)).grid(row=0, column=2, sticky="w", padx=4)
        self.var_numero = tk.StringVar()
        tk.Entry(fr_form, textvariable=self.var_numero, font=("Segoe UI", 10), width=18).grid(row=0, column=3, padx=4)

        tk.Label(fr_form, text="Monto ($):", bg=COLOR_FONDO, font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", padx=4, pady=4)
        self.var_monto = tk.StringVar()
        tk.Entry(fr_form, textvariable=self.var_monto, font=("Segoe UI", 10), width=15).grid(row=1, column=1, padx=4, sticky="w")

        tk.Label(fr_form, text="Notas:", bg=COLOR_FONDO, font=("Segoe UI", 10)).grid(row=1, column=2, sticky="w", padx=4)
        self.var_notas = tk.StringVar()
        tk.Entry(fr_form, textvariable=self.var_notas, font=("Segoe UI", 10), width=24).grid(row=1, column=3, padx=4)

        self.lbl_archivo = tk.Label(fr_form, text="Ningún archivo seleccionado", bg=COLOR_FONDO,
                                     font=("Segoe UI", 9, "italic"), fg="#888888")
        self.lbl_archivo.grid(row=2, column=0, columnspan=3, sticky="w", padx=4, pady=(8, 4))

        tk.Button(fr_form, text="📎 Elegir archivo (PDF o foto)", bg="#2F5496", fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  command=self._elegir_archivo).grid(row=3, column=0, columnspan=2, sticky="w", padx=4, pady=4)

        tk.Button(fr_form, text="✅ Guardar comprobante", bg="#27AE60", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
                  command=self._guardar).grid(row=3, column=2, columnspan=2, sticky="w", padx=4, pady=4)

        self.archivo_seleccionado = None

        tk.Label(self, text="Comprobantes cargados:", bg=COLOR_FONDO,
                 font=("Segoe UI", 10, "bold"), fg=COLOR_PRIMARIO).pack(anchor="w", padx=15, pady=(8, 2))

        fr_filtro = tk.Frame(self, bg=COLOR_FONDO)
        fr_filtro.pack(fill="x", padx=15)
        tk.Label(fr_filtro, text="Filtrar por proveedor:", bg=COLOR_FONDO, font=("Segoe UI", 9)).pack(side="left")
        self.combo_filtro = ttk.Combobox(fr_filtro, state="readonly", font=("Segoe UI", 9), width=25)
        self.combo_filtro.pack(side="left", padx=6)
        self.combo_filtro.bind("<<ComboboxSelected>>", lambda e: self._refrescar())

        fr_t = tk.Frame(self, bg=COLOR_FONDO)
        fr_t.pack(fill="both", expand=True, padx=15, pady=6)
        cols = ("fecha", "proveedor", "numero", "monto", "archivo", "notas")
        self.tabla = ttk.Treeview(fr_t, columns=cols, show="headings", height=10)
        for col, txt, w in [("fecha", "Fecha", 140), ("proveedor", "Proveedor", 160),
                              ("numero", "N° Comprobante", 110), ("monto", "Monto", 90),
                              ("archivo", "Archivo", 160), ("notas", "Notas", 150)]:
            self.tabla.heading(col, text=txt)
            self.tabla.column(col, width=w, anchor="center" if col in ("monto",) else "w")
        sc = ttk.Scrollbar(fr_t, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=sc.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        sc.pack(side="right", fill="y")

        fr_bot = tk.Frame(self, bg=COLOR_FONDO)
        fr_bot.pack(pady=8)
        tk.Button(fr_bot, text="👁 Abrir archivo", bg=COLOR_PRIMARIO, fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  command=self._abrir_archivo).pack(side="left", padx=4)
        tk.Button(fr_bot, text="🗑 Eliminar", bg="#C0392B", fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  command=self._eliminar).pack(side="left", padx=4)
        tk.Button(fr_bot, text="Cerrar", bg="#AAAAAA", fg="white",
                  font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                  command=self.destroy).pack(side="left", padx=4)

    def _cargar_proveedores(self):
        self.proveedores = self.inventario.obtener_proveedores()
        nombres = [p.nombre for p in self.proveedores]
        self.combo_prov["values"] = nombres
        self.combo_filtro["values"] = ["(Todos)"] + nombres
        self.combo_filtro.current(0)
        if nombres:
            self.combo_prov.current(0)

    def _elegir_archivo(self):
        ruta = filedialog.askopenfilename(
            parent=self,
            title="Seleccionar comprobante",
            filetypes=[("Comprobantes", "*.pdf *.jpg *.jpeg *.png"),
                       ("PDF", "*.pdf"), ("Imágenes", "*.jpg *.jpeg *.png"), ("Todos", "*.*")]
        )
        if not ruta:
            return
        if not ruta.lower().endswith(EXTENSIONES_VALIDAS):
            messagebox.showerror("Formato no válido", "Solo se aceptan archivos PDF, JPG o PNG.", parent=self)
            return
        self.archivo_seleccionado = ruta
        self.lbl_archivo.config(text=f"📄 {os.path.basename(ruta)}", fg="#27AE60")

    def _guardar(self):
        idx = self.combo_prov.current()
        if idx < 0:
            messagebox.showwarning("Atención", "Seleccioná un proveedor.", parent=self)
            return
        if not self.archivo_seleccionado:
            messagebox.showwarning("Atención", "Elegí un archivo de comprobante (PDF o foto).", parent=self)
            return
        monto = 0.0
        if self.var_monto.get().strip():
            try:
                monto = float(self.var_monto.get())
            except:
                messagebox.showerror("Error", "El monto debe ser un número válido.", parent=self)
                return

        nombre_original = os.path.basename(self.archivo_seleccionado)
        ext = os.path.splitext(nombre_original)[1]
        nombre_destino = f"comp_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        ruta_destino = os.path.join(COMPROBANTES_DIR, nombre_destino)
        try:
            shutil.copy2(self.archivo_seleccionado, ruta_destino)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo copiar el archivo:\n{e}", parent=self)
            return

        id_prov = self.proveedores[idx].id_proveedor
        comp = Comprobante(
            id_proveedor=id_prov, numero_comprobante=self.var_numero.get(),
            monto=monto, archivo_nombre=nombre_original, archivo_ruta=ruta_destino,
            notas=self.var_notas.get(), usuario=self.usuario)
        try:
            self.inventario.agregar_comprobante(comp)
            messagebox.showinfo("Guardado", "Comprobante guardado correctamente.", parent=self)
            self.var_numero.set(""); self.var_monto.set(""); self.var_notas.set("")
            self.archivo_seleccionado = None
            self.lbl_archivo.config(text="Ningún archivo seleccionado", fg="#888888")
            self._refrescar()
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self)

    def _refrescar(self):
        for row in self.tabla.get_children():
            self.tabla.delete(row)
        filtro = self.combo_filtro.get()
        id_prov_filtro = None
        if filtro and filtro != "(Todos)":
            for p in self.proveedores:
                if p.nombre == filtro:
                    id_prov_filtro = p.id_proveedor
                    break
        comprobantes = self.inventario.obtener_comprobantes(id_prov_filtro)
        self._comprobantes_actuales = comprobantes
        for c in comprobantes:
            monto_txt = f"${c.monto:,.2f}" if c.monto else "-"
            self.tabla.insert("", "end", iid=c.id_comprobante,
                               values=(c.fecha, c.proveedor_nombre, c.numero_comprobante or "-",
                                       monto_txt, c.archivo_nombre, c.notas or ""))

    def _abrir_archivo(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccioná un comprobante.", parent=self)
            return
        id_c = int(sel[0])
        comp = next((c for c in self._comprobantes_actuales if c.id_comprobante == id_c), None)
        if not comp or not os.path.exists(comp.archivo_ruta):
            messagebox.showerror("Error", "El archivo no se encuentra disponible.", parent=self)
            return
        try:
            if sys.platform == "win32":
                os.startfile(comp.archivo_ruta)
            elif sys.platform == "darwin":
                subprocess.run(["open", comp.archivo_ruta])
            else:
                subprocess.run(["xdg-open", comp.archivo_ruta])
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)

    def _eliminar(self):
        sel = self.tabla.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccioná un comprobante.", parent=self)
            return
        if not messagebox.askyesno("Confirmar", "¿Eliminar este comprobante? El archivo también se borrará.", parent=self):
            return
        id_c = int(sel[0])
        ruta = self.inventario.eliminar_comprobante(id_c)
        if ruta and os.path.exists(ruta):
            try:
                os.remove(ruta)
            except Exception:
                pass
        self._refrescar()
