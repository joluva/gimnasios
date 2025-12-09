# ui/screens/miembros_form.py  ← VERSIÓN QUE FUNCIONA EN MOBA + SSH
# ui/screens/miembros_form.py  ← VERSIÓN DEFINITIVA (funciona siempre)
import customtkinter as ctk
from tkinter import messagebox
from core.database import get_connection
from core.auth import CURRENT_USER, CURRENT_EMPRESA_ID

class MiembroForm(ctk.CTkToplevel):
    def __init__(self, parent, miembro_id=None):
        super().__init__(parent)
        self.title("Nuevo Miembro")
        self.geometry("620x780")
        self.configure(fg_color="#1a1a1a")

        # Título
        ctk.CTkLabel(self, text="ALTA DE MIEMBRO", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=40)

        main = ctk.CTkFrame(self)
        main.pack(pady=20, padx=50, fill="both", expand=True)

        # === CAMPOS ===
        self.entries = {}
        for label in ["Nombre", "Apellido", "Email", "Teléfono"]:
            frame = ctk.CTkFrame(main)
            frame.pack(fill="x", pady=10)
            ctk.CTkLabel(frame, text=f"{label}:", width=120, anchor="w").pack(side="left", padx=15)
            entry = ctk.CTkEntry(frame, width=380)
            entry.pack(side="right", padx=15, fill="x", expand=True)
            self.entries[label] = entry

        # === COMBO MEMBRESÍAS ===
        ctk.CTkLabel(main, text="Membresía *", anchor="w").pack(pady=(30,5), padx=15)
        self.combo_mem = ctk.CTkComboBox(main, width=380, state="readonly")
        self.combo_mem.pack(pady=5, padx=15)
        self.combo_mem.set("Cargando membresías...")

        # Cargar membresías al abrir
        self.after(100, self.cargar_membresias)  # ← esto evita problemas de import

        # === BOTONES ===
        btns = ctk.CTkFrame(main, fg_color="transparent")
        btns.pack(pady=50)
        ctk.CTkButton(btns, text="GUARDAR MIEMBRO", width=200, height=45,
                      fg_color="#0066cc", hover_color="#0052a3",
                      command=self.guardar).pack(side="left", padx=25)
        ctk.CTkButton(btns, text="CANCELAR", width=200, height=45,
                      fg_color="gray30", command=self.destroy).pack(side="right", padx=25)

        self.grab_set()
        self.focus_force()

    def cargar_membresias(self):
        try:
            conn = get_connection()
            cur = conn.cursor()

            # Detectar si es SuperAdmin
            es_superadmin = CURRENT_USER and CURRENT_USER.get("rol") == "SuperAdmin"

            if es_superadmin:
                cur.execute("SELECT id, nombre || ' - $' || precio || ' (' || duracion_dias || ' días)' FROM TiposMembresias")
            else:
                if not CURRENT_EMPRESA_ID:
                    messagebox.showerror("Error", "No tienes empresa asignada")
                    self.combo_mem.configure(values=["Sin empresa"])
                    conn.close()
                    return
                cur.execute("SELECT id, nombre || ' - $' || precio || ' (' || duracion_dias || ' días)' FROM TiposMembresias WHERE empresa_id = ?", 
                           (CURRENT_EMPRESA_ID,))

            filas = cur.fetchall()
            conn.close()

            if not filas:
                self.combo_mem.configure(values=["No hay membresías creadas"])
                self.combo_mem.set("No hay membresías creadas")
                return

            opciones = [f"{f[0]}|{f[1]}" for f in filas]
            self.combo_mem.configure(values=opciones)
            self.combo_mem.set(opciones[0])

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las membresías:\n{e}")
            self.combo_mem.configure(values=["Error de conexión"])

    def guardar(self):
        nombre = self.entries["Nombre"].get().strip()
        apellido = self.entries["Apellido"].get().strip()
        email = self.entries["Email"].get().strip()

        if not (nombre and apellido and email):
            messagebox.showerror("Error", "Nombre, apellido y email son obligatorios")
            return

        seleccion = self.combo_mem.get()
        if "No hay" in seleccion or "Error" in seleccion or "|" not in seleccion:
            messagebox.showerror("Error", "Selecciona una membresía válida")
            return

        try:
            membresia_id = int(seleccion.split("|")[0])
        except:
            messagebox.showerror("Error", "Membresía corrupta")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO Miembros 
                (empresa_id, nombre, apellido, email, telefono, tipo_membresia_id, estado, fecha_inicio)
                VALUES (?, ?, ?, ?, ?, ?, 'Activo', date('now'))
            """, (CURRENT_EMPRESA_ID, nombre, apellido, email,
                  self.entries["Teléfono"].get().strip(), membresia_id))
            conn.commit()
            conn.close()

            messagebox.showinfo("ÉXITO", f"Miembro {nombre} {apellido} creado correctamente")
            self.destroy()

            # Refrescar lista
            try:
                self.master.master.mostrar_miembros()
            except:
                pass

        except Exception as e:
            messagebox.showerror("Error base de datos", str(e))