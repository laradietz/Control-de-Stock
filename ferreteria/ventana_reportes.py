"""
ventana_reportes.py
Ventana de reportes: resumen general y listado de productos con stock bajo.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from exportador import exportar_excel, exportar_pdf


class VentanaReportes(tk.Toplevel):
    """Ventana que muestra estadísticas generales y alertas de stock bajo."""

    def __init__(self, master, inventario):
        super().__init__(master)
        self.inventario = inventario

        self.title("Reportes de Stock")
        self.geometry("750x500")
        self.configure(bg="#F4F6F7")
        self.transient(master)
        self.grab_set()

        self._construir_interfaz()
        self._refrescar()

    def _construir_interfaz(self):
        tk.Label(self, text="Reporte General de Inventario", font=("Segoe UI", 14, "bold"),
                 bg="#F4F6F7", fg="#2F5496").pack(pady=(15, 10))

        # Panel de estadísticas
        self.frame_stats = tk.Frame(self, bg="#F4F6F7")
        self.frame_stats.pack(fill="x", padx=20)

        self.labels_stats = {}
        for clave, texto in [
            ("total_productos", "Total de productos"),
            ("total_unidades", "Unidades totales en stock"),
            ("valor_total", "Valor total del inventario"),
            ("productos_stock_bajo", "Productos con stock bajo"),
        ]:
            frame = tk.Frame(self.frame_stats, bg="white", relief="ridge", bd=1)
            frame.pack(side="left", expand=True, fill="both", padx=5, pady=5)
            tk.Label(frame, text=texto, bg="white", font=("Segoe UI", 9),
                     fg="#555555", wraplength=140).pack(pady=(8, 2))
            lbl_valor = tk.Label(frame, text="0", bg="white", font=("Segoe UI", 16, "bold"),
                                  fg="#2F5496")
            lbl_valor.pack(pady=(0, 8))
            self.labels_stats[clave] = lbl_valor

        # Tabla de productos con stock bajo
        tk.Label(self, text="⚠ Productos que requieren reposición (stock ≤ mínimo)",
                 bg="#F4F6F7", font=("Segoe UI", 11, "bold"), fg="#C0392B").pack(
            pady=(15, 5), anchor="w", padx=20)

        frame_tabla = tk.Frame(self, bg="#F4F6F7")
        frame_tabla.pack(fill="both", expand=True, padx=20)

        columnas = ("codigo", "nombre", "categoria", "cantidad", "minimo", "proveedor")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings", height=10)
        encabezados = {
            "codigo": "Código", "nombre": "Nombre", "categoria": "Categoría",
            "cantidad": "Cant. actual", "minimo": "Stock mínimo", "proveedor": "Proveedor"
        }
        anchos = {"codigo": 80, "nombre": 220, "categoria": 130,
                  "cantidad": 90, "minimo": 90, "proveedor": 150}
        for col in columnas:
            self.tabla.heading(col, text=encabezados[col])
            self.tabla.column(col, width=anchos[col], anchor="center" if col in
                               ("cantidad", "minimo", "codigo") else "w")

        scroll = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scroll.set)
        self.tabla.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.tabla.tag_configure("bajo", background="#FFC7CE")

        # Botones exportación
        frame_botones = tk.Frame(self, bg="#F4F6F7")
        frame_botones.pack(pady=12)

        tk.Button(frame_botones, text="Exportar reporte a Excel", bg="#27AE60", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", width=22, cursor="hand2",
                  command=self._exportar_excel).pack(side="left", padx=5)

        tk.Button(frame_botones, text="Exportar reporte a PDF", bg="#C0392B", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", width=22, cursor="hand2",
                  command=self._exportar_pdf).pack(side="left", padx=5)

        tk.Button(frame_botones, text="Cerrar", bg="#AAAAAA", fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", width=12, cursor="hand2",
                  command=self.destroy).pack(side="left", padx=5)

    def _refrescar(self):
        stats = self.inventario.estadisticas_generales()
        self.labels_stats["total_productos"].config(text=str(stats["total_productos"]))
        self.labels_stats["total_unidades"].config(text=str(stats["total_unidades"]))
        self.labels_stats["valor_total"].config(text=f"${stats['valor_total']:,.2f}")
        self.labels_stats["productos_stock_bajo"].config(text=str(stats["productos_stock_bajo"]))

        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        self.productos_bajo = self.inventario.productos_stock_bajo()
        for p in self.productos_bajo:
            self.tabla.insert("", "end", values=(
                p.codigo, p.nombre, p.categoria_nombre, p.cantidad,
                p.stock_minimo, p.proveedor_nombre
            ), tags=("bajo",))

    def _exportar_excel(self):
        try:
            ruta = exportar_excel(self.productos_bajo if self.productos_bajo
                                   else self.inventario.obtener_productos(),
                                   nombre_archivo="reporte_stock_bajo.xlsx")
            messagebox.showinfo("Exportación exitosa", f"Reporte exportado a:\n{ruta}", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar:\n{e}", parent=self)

    def _exportar_pdf(self):
        try:
            ruta = exportar_pdf(self.productos_bajo if self.productos_bajo
                                 else self.inventario.obtener_productos(),
                                 nombre_archivo="reporte_stock_bajo.pdf",
                                 titulo="Reporte de Stock Bajo - Ferretería")
            messagebox.showinfo("Exportación exitosa", f"Reporte exportado a:\n{ruta}", parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar:\n{e}", parent=self)
