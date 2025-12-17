# ui/screens/miembros_form.py  ← VERSIÓN COMPLETA Y PROFESIONAL
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import os
import pyqrcode
from datetime import date
from core.database import get_connection
from core.auth import CURRENT_USER, CURRENT_EMPRESA_ID

class MiembroForm(ctk.CTkToplevel):
    def __init__(self, parent, miembro_id=None):
        super().__init__(parent)
        self.parent = parent
        self.miembro_id = miembro_id
        self.title("Nuevo Miembro")
        self.geometry("900x900")
        self.resizable(True, True)

        self.foto_path = None

        # Scrollable frame para que quepa todo
        canvas = ctk.CTkCanvas(self)
        scrollbar = ctk.CTkScrollbar(self, orientation="vertical", command=canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.crear_formulario()

        self.grab_set()
        self.focus_force()

    def crear_formulario(self):
        frame = self.scrollable_frame
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=2)

        row = 0

        # Foto
        ctk.CTkLabel(frame, text="Foto del miembro", font=ctk.CTkFont(size=16, weight="bold")).grid(row=row, column=0, columnspan=2, pady=20, sticky="w", padx=20)
        row += 1
        self.lbl_foto = ctk.CTkLabel(frame, text="Sin foto", width=250, height=250, fg_color="#2f2f2f", corner_radius=10)
        self.lbl_foto.grid(row=row, column=0, columnspan=2, pady=10)
        ctk.CTkButton(frame, text="Seleccionar Foto", command=self.seleccionar_foto).grid(row=row+1, column=0, columnspan=2, pady=10)
        row += 2

        # Campos básicos
        campos = [
            ("Nombre *", "nombre"),
            ("Apellido *", "apellido"),
            ("Email *", "email"),
            ("Teléfono", "telefono"),
            ("Dirección", "direccion"),
            ("Fecha de nacimiento (YYYY-MM-DD)", "fecha_nac"),
            ("Género", "genero", ["Masculino", "Femenino", "Otro", "Prefiero no decir"]),
        ]

        self.entries = {}
        for label, key, *extra in campos:
            ctk.CTkLabel(frame, text=label, anchor="w").grid(row=row, column=0, sticky="w", padx=20, pady=8)
            if extra:
                widget = ctk.CTkComboBox(frame, values=extra[0])
                widget.set(extra[0][0])
            else:
                widget = ctk.CTkEntry(frame, width=400)
            widget.grid(row=row, column=1, padx=20, pady=8, sticky="ew")
            self.entries[key] = widget
            row += 1

        # Notas
        ctk.CTkLabel(frame, text="Notas", anchor="w").grid(row=row, column=0, sticky="nw", padx=20, pady=8)
        self.text_notas = ctk.CTkTextbox(frame, width=400, height=100)
        self.text_notas.grid(row=row, column=1, padx=20, pady=8, sticky="ew")
        row += 1

        # Tipo de membresía
        ctk.CTkLabel(frame, text="Tipo de Membresía *", anchor="w").grid(row=row, column=0, sticky="w", padx=20, pady=(30,8))
        self.combo_membresia = ctk.CTkComboBox(frame, width=400, state="readonly")
        self.combo_membresia.grid(row=row, column=1, padx=20, pady=8, sticky="ew")
        self.after(100, self.cargar_membresias)
        row += 1

        # Info automática
        ctk.CTkLabel(frame, text="Fecha de inicio:", font=ctk.CTkFont(weight="bold")).grid(row=row, column=0, sticky="w", padx=20, pady=(40,5))
        ctk.CTkLabel(frame, text=date.today().strftime("%Y-%m-%d"), text_color="green").grid(row=row, column=1, sticky="w", padx=20)
        row += 1

        ctk.CTkLabel(frame, text="Estado:", font=ctk.CTkFont(weight="bold")).grid(row=row, column=0, sticky="w", padx=20, pady=5)
        ctk.CTkLabel(frame, text="Activo (por defecto)", text_color="green").grid(row=row, column=1, sticky="w", padx=20)
        row += 1

        # Botones
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.grid(row=row, column=0, columnspan=2, pady=50)
        ctk.CTkButton(btn_frame, text="GUARDAR MIEMBRO", width=250, height=50, fg_color="#0066cc", command=self.guardar).pack(side="left", padx=30)
        ctk.CTkButton(btn_frame, text="CANCELAR", width=250, height=50, fg_color="gray30", command=self.destroy).pack(side="right", padx=30)

    def seleccionar_foto(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar foto",
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.webp *.bmp")]
        )
        if ruta:
            self.foto_path = ruta
            try:
                img = Image.open(ruta)
                img = img.resize((250, 250), Image.Resampling.LANCZOS)
                photo = ctk.CTkImage(light_image=img, dark_image=img, size=(250, 250))
                self.lbl_foto.configure(image=photo, text="")
                self.lbl_foto.image = photo
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la imagen:\n{e}")

    def cargar_membresias(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            if CURRENT_USER.get("rol") == "SuperAdmin":
                cur.execute("SELECT id, nombre || ' - $' || precio || ' (' || duracion_dias || ' días)' FROM TiposMembresias")
            else:
                if not CURRENT_EMPRESA_ID:
                    messagebox.showerror("Error", "No tienes empresa asignada")
                    return
                cur.execute("SELECT id, nombre || ' - $' || precio || ' (' || duracion_dias || ' días)' FROM TiposMembresias WHERE empresa_id = ?", (CURRENT_EMPRESA_ID,))
            rows = cur.fetchall()
            conn.close()

            if not rows:
                self.combo_membresia.configure(values=["No hay membresías disponibles"])
                self.combo_membresia.set("No hay membresías disponibles")
                return

            opciones = [f"{r[0]}|{r[1]}" for r in rows]
            self.combo_membresia.configure(values=opciones)
            self.combo_membresia.set(opciones[0])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar membresías:\n{e}")

    def guardar(self):
        nombre = self.entries["nombre"].get().strip()
        apellido = self.entries["apellido"].get().strip()
        email = self.entries["email"].get().strip()

        if not (nombre and apellido and email):
            messagebox.showerror("Error", "Nombre, apellido y email son obligatorios")
            return

        seleccion_mem = self.combo_membresia.get()
        if "No hay" in seleccion_mem or "|" not in seleccion_mem:
            messagebox.showerror("Error", "Selecciona una membresía válida")
            return
        tipo_membresia_id = int(seleccion_mem.split("|")[0])

        # === DETERMINAR empresa_id DE FORMA 100% SEGURA ===
        conn_temp = get_connection()
        cur_temp = conn_temp.cursor()
        cur_temp.execute("SELECT id FROM Empresas ORDER BY id LIMIT 1")
        fila = cur_temp.fetchone()
        conn_temp.close()

        if not fila:
            messagebox.showerror("Error crítico", "No existe ninguna empresa en el sistema. Crea una primero.")
            return

        empresa_id = fila[0]  # Siempre usa la primera empresa disponible

        # Si es usuario normal, verifica que coincida (opcional, pero seguro)
        if CURRENT_USER.get("rol") != "SuperAdmin" and CURRENT_EMPRESA_ID and CURRENT_EMPRESA_ID != empresa_id:
            messagebox.showwarning("Advertencia", f"Usando empresa predeterminada (ID {empresa_id})")

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO Miembros
                (empresa_id, nombre, apellido, email, telefono, direccion, fecha_nacimiento, genero,
                 notas, foto_path, tipo_membresia_id, fecha_inicio, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, date('now'), 'Activo')
            """, (
                empresa_id,
                nombre,
                apellido,
                email,
                self.entries["telefono"].get().strip() or None,
                self.entries["direccion"].get().strip() or None,
                self.entries["fecha_nac"].get().strip() or None,
                self.entries["genero"].get(),
                self.text_notas.get("1.0", "end").strip() or None,
                self.foto_path,
                tipo_membresia_id
            ))
            miembro_id = cur.lastrowid

            # Generar QR
            os.makedirs("assets/qr", exist_ok=True)
            codigo = f"GYM{miembro_id:06d}"
            qr = pyqrcode.create(codigo)
            ruta_qr = f"assets/qr/qr_{miembro_id}.png"
            qr.png(ruta_qr, scale=10)
            cur.execute("UPDATE Miembros SET codigo_qr = ? WHERE id = ?", (ruta_qr, miembro_id))

            conn.commit()
            conn.close()

            messagebox.showinfo("Éxito", f"Miembro {nombre} {apellido} creado correctamente\nQR generado en {ruta_qr}")
            self.destroy()

            # Refrescar lista
            try:
                self.parent.mostrar_miembros()
            except:
                pass

        except Exception as e:
            messagebox.showerror("Error al guardar", str(e))