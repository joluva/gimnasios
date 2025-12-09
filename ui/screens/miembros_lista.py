# ui/screens/miembros_lista.py
import customtkinter as ctk
from tkinter import ttk
from core.database import get_connection
from core.auth import CURRENT_EMPRESA_ID, CURRENT_USER

class MiembrosScreen(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        ctk.CTkLabel(self, text="Gestión de Miembros", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=20)

        # Barra de búsqueda
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", padx=30, pady=10)

        self.entry_buscar = ctk.CTkEntry(search_frame, placeholder_text="Buscar por nombre, email o teléfono...")
        self.entry_buscar.pack(side="left", fill="x", expand=True, padx=(0,10))
        self.entry_buscar.bind("<KeyRelease>", self.buscar_miembro)

        ctk.CTkButton(search_frame, text="Nuevo Miembro", width=140, command=self.nuevo_miembro).pack(side="right")

        # Tabla
        columnas = ("ID", "Nombre Completo", "Email", "Teléfono", "Membresía", "Estado", "Vence")
        self.tree = ttk.Treeview(self, columns=columnas, show="headings", height=20)
        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=30, pady=20)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.cargar_miembros()

    # def cargar_miembros(self, filtro=""):
    #     # Limpiar tabla
    #     for i in self.tree.get_children():
    #         self.tree.delete(i)

    #     conn = get_connection()
    #     cur = conn.cursor()

    #     if CURRENT_USER["rol"] == "SuperAdmin":
    #         sql = """SELECT m.id, m.nombre || ' ' || m.apellido, m.email, m.telefono,
    #                         tm.nombre, m.estado, m.fecha_fin
    #                  FROM Miembros m
    #                  LEFT JOIN TiposMembresias tm ON m.tipo_membresia_id = tm.id
    #                  WHERE m.nombre || m.apellido || m.email LIKE ?"""
    #         params = (f"%{filtro}%",)
    #     else:
    #         sql = """SELECT m.id, m.nombre || ' ' || m.apellido, m.email, m.telefono,
    #                         tm.nombre, m.estado, m.fecha_fin
    #                  FROM Miembros m
    #                  LEFT JOIN TiposMembresias tm ON m.tipo_membresia_id = tm.id
    #                  WHERE m.empresa_id = ? AND (m.nombre || m.apellido || m.email LIKE ?)"""
    #         params = (CURRENT_EMPRESA_ID, f"%{filtro}%")

    #     cur.execute(sql, params)
    #     for row in cur.fetchall():
    #         self.tree.insert("", "end", values=row)
    #     conn.close()
    
    def cargar_miembros(self, filtro=""):
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = get_connection()
        cur = conn.cursor()

        query = """
            SELECT m.id, m.nombre || ' ' || m.apellido, m.email, m.telefono,
                tm.nombre, m.estado, m.fecha_fin
             FROM Miembros m
            LEFT JOIN TiposMembresias tm ON m.tipo_membresia_id = tm.id
            WHERE m.empresa_id = ?
            AND (m.nombre || m.apellido || m.email LIKE ?)
    """
        cur.execute(query, (CURRENT_EMPRESA_ID, f"%{filtro}%"))
        for row in cur.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()
    

    def buscar_miembro(self, event=None):
        texto = self.entry_buscar.get()
        self.cargar_miembros(texto)

    def nuevo_miembro(self):
        from .miembros_form import MiembroForm
        MiembroForm(self.winfo_toplevel())  # abre el formulario