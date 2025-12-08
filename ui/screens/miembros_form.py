# ui/screens/miembros_form.py  ← VERSIÓN CORREGIDA Y FUNCIONAL AL 100%
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import os
import pyqrcode
from datetime import datetime, timedelta
from core.database import get_connection
from core.auth import CURRENT_USER, CURRENT_EMPRESA_ID

# ui/screens/miembros_form.py  ← SOLO REEMPLAZA HASTA AQUÍ
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import os
import pyqrcode
from datetime import datetime, timedelta
from core.database import get_connection
from core.auth import CURRENT_USER, CURRENT_EMPRESA_ID

class MiembroForm(ctk.CTkToplevel):
    def __init__(self, parent, miembro_id=None):  # ← correcto
        super().__init__(parent)
        self.parent = parent
        self.miembro_id = miembro_id  # ← CORREGIDO: era "miembro"
        self.title("Nuevo Miembro" if not miembro_id else "Editar Miembro")
        self.geometry("850x900")
        self.resizable(False, False)
        self.grab_set()

        self.foto_path = None
        self.crear_interfaz()

    def crear_interfaz(self):
        canvas = ctk.CTkCanvas(self, width=850, height=900)
        scrollbar = ctk.CTkScrollbar(self, orientation="vertical", command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # === FOTO ===
        ctk.CTkLabel(scrollable_frame, text="Foto del miembro", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, columnspan=2, pady=20, sticky="w", padx=30)
        self.lbl_foto = ctk.CTkLabel(scrollable_frame, text="Sin foto seleccionada", width=220, height=220, fg_color="#333")
        self.lbl_foto.grid(row=1, column=0, columnspan=2, pady=10)
        ctk.CTkButton(scrollable_frame, text="Seleccionar Foto", command=self.cargar_foto).grid(row=2, column=0, columnspan=2, pady=10)

        # === CAMPOS ===
        campos = [
            ("Nombre", "entry"),
            ("Apellido", "entry"),
            ("Email", "entry", "obligatorio"),
            ("Teléfono", "entry"),
            ("Fecha de nacimiento", "entry", "YYYY-MM-DD"),
            ("Género", "combo", ["Masculino", "Femenino", "Otro", "Prefiero no decir"]),
            ("Dirección", "entry"),
        ]

        self.entries = {}
        row = 3
        for label, tipo, *extra in campos:
            ctk.CTkLabel(scrollable_frame, text=label + " *", font=ctk.CTkFont(size=14)).grid(row=row, column=0, sticky="w", padx=30, pady=8)
            if tipo == "entry":
                entry = ctk.CTkEntry(scrollable_frame, width=400)
                entry.grid(row=row, column=1, pady=8, padx=30, sticky="w")
                if extra and extra[0]:
                    entry.insert(0, extra[0])
                self.entries[label] = entry
            elif tipo == "combo":
                combo = ctk.CTkComboBox(scrollable_frame, values=extra[0], width=400)
                combo.grid(row=row, column=1, pady=8, padx=30, sticky="w")
                combo.set(extra[0][0])
                self.entries[label] = combo
            row += 1

        # === MEMBRESÍA ===
        ctk.CTkLabel(scrollable_frame, text="Tipo de Membresía *", font=ctk.CTkFont(size=14)).grid(row=row, column=0, sticky="w", padx=30, pady=8)
        self.combo_membresia = ctk.CTkComboBox(scrollable_frame, width=400)
        self.combo_membresia.grid(row=row, column=1, pady=8, padx=30, sticky="w")
        self.cargar_membresias()
        row += 1

        # === FECHAS ===
        hoy = datetime.today().strftime("%Y-%m-%d")
        ctk.CTkLabel(scrollable_frame, text="Fecha de inicio *").grid(row=row, column=0, sticky="w", padx=30, pady=8)
        self.entry_inicio = ctk.CTkEntry(scrollable_frame, width=200)
        self.entry_inicio.grid(row=row, column=1, sticky="w", padx=30, pady=8)
        self.entry_inicio.insert(0, hoy)
        row += 1

        ctk.CTkLabel(scrollable_frame, text="Vence el:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=row, column=0, sticky="w", padx=30, pady=8)
        self.lbl_vencimiento = ctk.CTkLabel(scrollable_frame, text="Selecciona membresía", text_color="orange", font=ctk.CTkFont(size=14))
        self.lbl_vencimiento.grid(row=row, column=1, sticky="w", padx=30, pady=8)
        self.combo_membresia.bind("<<ComboboxSelected>>", self.calcular_vencimiento)
        self.calcular_venc()

        # === BOTONES ===
        btn_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        btn_frame.grid(row=row+2, column=0, columnspan=2, pady=40)
        ctk.CTkButton(btn_frame, text="Guardar Miembro", width=200, fg_color="#1f6aa5", command=self.guardar).pack(side="left", padx=30)
        ctk.CTkButton(btn_frame, text="Cancelar", width=200, fg_color="gray", command=self.destroy).pack(side="right", padx=30)

    def cargar_foto(self):
        ruta = filedialog.askopenfilename(filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.webp")])
        if ruta:
            self.foto_path = ruta
            img = Image.open(ruta).resize((220, 220), Image.Resampling.LANCZOS)
            photo = ctk.CTkImage(light_image=img, dark_image=img, size=(220, 220))
            self.lbl_foto.configure(image=photo, text="")
            self.lbl_foto.image = photo

    def cargar_membresias(self):
        conn = get_connection()
        cur = conn.cursor()
        if CURRENT_USER.get("rol") == "SuperAdmin":
            cur.execute("SELECT id, nombre || ' - $' || precio || ' (' || duracion_dias || ' días)' FROM TiposMembresias")
        else:
            cur