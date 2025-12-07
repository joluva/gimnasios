# main.py
import customtkinter as ctk
from core.database import init_db
from ui.login_window import LoginWindow

# Crear base de datos y tablas automáticamente
init_db()

def mostrar_ventana_principal():
    app = ctk.CTk()
    app.title("GimnasioPro – Panel Principal")
    app.geometry("1200x800")

    # Aquí irá todo el sistema real (menú, pestañas, etc.)
    # Por ahora solo una bienvenida gigante
    ctk.CTkLabel(
        app,
        text="¡BIENVENIDO A GIMNASIOPRO!",
        font=ctk.CTkFont(size=40, weight="bold")
    ).pack(expand=True)

    # Información de la sesión actual
    from core.auth import CURRENT_USER, CURRENT_EMPRESA_ID
    rol = CURRENT_USER["rol"] if CURRENT_USER else "Desconocido"
    empresa = "Todas (SuperAdmin)" if CURRENT_USER["rol"] == "SuperAdmin" else f"ID {CURRENT_EMPRESA_ID}"

    ctk.CTkLabel(
        app,
        text=f"Usuario: {CURRENT_USER['username'] if CURRENT_USER else '??'} | Rol: {rol} | Empresa: {empresa}",
        font=ctk.CTkFont(size=16)
    ).pack(pady=20)

    app.mainloop()

# Iniciar con ventana de login
login_window = LoginWindow(callback_inicio_sesion=mostrar_ventana_principal)
login_window.mainloop()