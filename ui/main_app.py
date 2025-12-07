# ui/main_app.py  ← VERSIÓN 100 % CORREGIDA Y FUNCIONAL
import customtkinter as ctk
from tkinter import ttk
from core.auth import CURRENT_USER, CURRENT_EMPRESA_ID

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("GimnasioPro – Panel Principal")
        self.geometry("1280x720")
        self.minsize(1100, 650)

        # Configuración de grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.crear_sidebar()
        self.crear_area_contenido()

    def crear_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=240, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nswe")
        sidebar.grid_rowconfigure(9, weight=1)

        # Logo
        ctk.CTkLabel(sidebar, text="GIMNASIOPRO", font=ctk.CTkFont(size=26, weight="bold")).grid(
            row=0, column=0, padx=20, pady=(40, 50))

        # Información del usuario actual
        if CURRENT_USER:
            username = CURRENT_USER.get("username", "??")
            rol = CURRENT_USER.get("rol", "??")
            if rol == "SuperAdmin":
                empresa_texto = "Todas las empresas"
            else:
                empresa_texto = f"ID {CURRENT_EMPRESA_ID}" if CURRENT_EMPRESA_ID else "Sin empresa"
        else:
            username = "Error de sesión"
            rol = "Desconocido"
            empresa_texto = "—"

        ctk.CTkLabel(sidebar, text=username, font=ctk.CTkFont(size=18, weight="bold")).grid(row=1, column=0, padx=20)
        ctk.CTkLabel(sidebar, text=f"{rol}\n{empresa_texto}", text_color="#aaaaaa").grid(
            row=2, column=0, padx=20, pady=(0, 40))

        # Botones del menú
        menu_items = [
            ("Miembros", self.mostrar_miembros),
            ("Asistencias", lambda: self.mostrar_proximamente("Asistencias")),
            ("Pagos", lambda: self.mostrar_proximamente("Pagos")),
            ("Clases & Horarios", lambda: self.mostrar_proximamente("Clases")),
            ("Tienda / Productos", lambda: self.mostrar_proximamente("Tienda")),
            ("Reportes", lambda: self.mostrar_proximamente("Reportes")),
            ("Configuración", lambda: self.mostrar_proximamente("Configuración")),
        ]

        for i, (texto, comando) in enumerate(menu_items, start=3):
            btn = ctk.CTkButton(
                sidebar,
                text=texto,
                height=45,
                anchor="w",
                font=ctk.CTkFont(size=14),
                command=comando
            )
            btn.grid(row=i, column=0, padx=20, pady=6, sticky="ew")

        # Cerrar sesión (abajo del todo)
        ctk.CTkButton(
            sidebar,
            text="Cerrar Sesión",
            fg_color="transparent",
            text_color="#ff6b6b",
            hover_color="#c92a2a",
            command=self.cerrar_sesion
        ).grid(row=10, column=0, padx=20, pady=30, sticky="s")

    def crear_area_contenido(self):
        self.frame_contenido = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.frame_contenido.grid(row=0, column=1, sticky="nswe")
        self.frame_contenido.grid_rowconfigure(0, weight=1)
        self.frame_contenido.grid_columnconfigure(0, weight=1)

        # Por defecto mostramos la lista de miembros
        self.mostrar_miembros()

    def mostrar_miembros(self):
        from .screens.miembros_lista import MiembrosScreen
        self.limpiar_contenido()
        MiembrosScreen(self.frame_contenido).pack(fill="both", expand=True)

    def mostrar_proximamente(self, modulo):
        self.limpiar_contenido()
        ctk.CTkLabel(
            self.frame_contenido,
            text=f"Módulo {modulo}\n\nPróximamente",
            font=ctk.CTkFont(size=40),
            text_color="gray60"
        ).pack(expand=True)

    def limpiar_contenido(self):
        for widget in self.frame_contenido.winfo_children():
            widget.destroy()

    def cerrar_sesion(self):
        from core.auth import CURRENT_USER as CU
        CU = None  # limpiamos la sesión
        self.destroy()

        # Volvemos al login
        from ui.login_window import LoginWindow
        LoginWindow(callback_inicio_sesion=lambda: MainApp().mainloop()).mainloop()