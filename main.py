# main.py  ← VERSIÓN FINAL Y CORRECTA (agosto 2025)
import customtkinter as ctk
from core.database import init_db
from ui.login_window import LoginWindow
from ui.main_app import MainApp

# Creamos la BD y tablas la primera vez
init_db()

def iniciar_aplicacion_principal():
    """Esta función se llama solo DESPUÉS de hacer login correctamente"""
    app = MainApp()
    app.mainloop()

# === INICIO DEL PROGRAMA ===
# 
# Primero mostramos el login
login_window = LoginWindow(callback_inicio_sesion=iniciar_aplicacion_principal)
login_window.mainloop()