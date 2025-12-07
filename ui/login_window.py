# ui/login_window.py  ← VERSIÓN CORREGIDA (2025
import customtkinter as ctk
from tkinter import messagebox
from core.database import get_connection
from core.auth import login, CURRENT_USER

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class LoginWindow(ctk.CTk):
    def __init__(self, callback_inicio_sesion):
        super().__init__()
        self.callback_inicio_sesion = callback_inicio_sesion
        self.title("GimnasioPro – Login")
        self.geometry("420x580")
        self.resizable(False, False)
        self._center_window()

        ctk.CTkLabel(self, text="GIMNASIOPRO", font=ctk.CTkFont(size=36, weight="bold")).pack(pady=50)

        frame = ctk.CTkFrame(self)
        frame.pack(pady=20, padx=50, fill="both", expand=True)

        ctk.CTkLabel(frame, text="Usuario").pack(pady=(30, 8))
        self.entry_user = ctk.CTkEntry(frame, placeholder_text="admin")
        self.entry_user.pack(pady=5, fill="x")

        ctk.CTkLabel(frame, text="Contraseña").pack(pady=(20, 8))
        self.entry_pass = ctk.CTkEntry(frame, placeholder_text="••••••••", show="*")
        self.entry_pass.pack(pady=5, fill="x")

        ctk.CTkButton(frame, text="Iniciar Sesión", height=40, command=self.intentar_login).pack(pady=30)

        # Credenciales rápidas para prueba
        info = ctk.CTkLabel(self,
            text="Prueba rápida:\nadmin  →  admin123\n demo  →  demo123",
            text_color="#888888", font=ctk.CTkFont(size=11))
        info.pack(side="bottom", pady=30)

    def _center_window(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (420 // 2)
        y = (self.winfo_screenheight() // 2) - (580 // 2)
        self.geometry(f"+{x}+{y}")

    def intentar_login(self):
        user = self.entry_user.get().strip()
        pwd = self.entry_pass.get().strip()

        if not user or not pwd:
            messagebox.showerror("Error", "Ingresa usuario y contraseña")
            return

        # Credenciales de prueba hardcodeadas (para que funcione sin bcrypt al inicio)
        if user == "admin" and pwd == "admin123":
            from core.auth import CURRENT_USER
            CURRENT_USER = {"username": "admin", "rol": "SuperAdmin", "empresa_id": None}
            self.destroy()
            self.callback_inicio_sesion()
            return

        if user == "demo" and pwd == "demo123":
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT id FROM Empresas LIMIT 1")
            row = cur.fetchone()
            conn.close()
            empresa_id = row["id"] if row else None

            from core.auth import CURRENT_USER
            CURRENT_USER = {"username": "demo", "rol": "Admin", "empresa_id": empresa_id}
            self.destroy()
            self.callback_inicio_sesion()
            return

        messagebox.showerror("Error", "Credenciales incorrectas")