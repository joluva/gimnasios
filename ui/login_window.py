# ui/login_window.py  ← VERSIÓN FINAL QUE FUNCIONA
import customtkinter as ctk
from tkinter import messagebox
from core.auth import CURRENT_USER, CURRENT_EMPRESA_ID
from core.database import get_connection

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class LoginWindow(ctk.CTk):
    def __init__(self, callback_inicio_sesion):
        super().__init__()
        self.callback_inicio_sesion = callback_inicio_sesion
        self.title("GimnasioPro – Iniciar Sesión")
        self.geometry("420x580")
        self.resizable(False, False)
        self._center_window()

        ctk.CTkLabel(self, text="GIMNASIOPRO", font=ctk.CTkFont(size=36, weight="bold")).pack(pady=60)

        frame = ctk.CTkFrame(self)
        frame.pack(pady=30, padx=60, fill="both", expand=True)

        ctk.CTkLabel(frame, text="Usuario").pack(pady=(30, 8))
        self.entry_user = ctk.CTkEntry(frame, placeholder_text="admin")
        self.entry_user.pack(pady=5, fill="x")

        ctk.CTkLabel(frame, text="Contraseña").pack(pady=(20, 8))
        self.entry_pass = ctk.CTkEntry(frame, placeholder_text="••••••••", show="*")
        self.entry_pass.pack(pady=5, fill="x")

        ctk.CTkButton(frame, text="Iniciar Sesión", height=45, command=self.intentar_login).pack(pady=40)

        ctk.CTkLabel(self,
            text="Credenciales de prueba:\nadmin → admin123 (SuperAdmin)\ndemo → demo123 (Admin del gimnasio)",
            text_color="#888888", font=ctk.CTkFont(size=11)).pack(side="bottom", pady=30)

    def _center_window(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 210
        y = (self.winfo_screenheight() // 2) - 290
        self.geometry(f"+{x}+{y}")

    def intentar_login(self):
        user = self.entry_user.get().strip()
        pwd = self.entry_pass.get().strip()

        if not user or not pwd:
            messagebox.showerror("Error", "Completa usuario y contraseña")
            return

        # Credenciales hardcodeadas para prueba rápida
        if user == "admin" and pwd == "admin123":
            CURRENT_USER.update({
                "id": 1, "username": "admin", "rol": "SuperAdmin", "empresa_id": None
            })
            self.destroy()
            self.callback_inicio_sesion()
            return

        if user == "demo" and pwd == "demo123":
            # Buscamos la primera empresa
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT id FROM Empresas LIMIT 1")
            row = cur.fetchone()
            conn.close()
            empresa_id = row["id"] if row else None

            CURRENT_USER.update({
                "id": 2, "username": "demo", "rol": "Admin", "empresa_id": empresa_id
            })
            self.destroy()
            self.callback_inicio_sesion()
            return

        messagebox.showerror("Error", "Usuario o contraseña incorrectos")