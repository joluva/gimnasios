# test_form.py  ← EJECUTA ESTE ARCHIVO SOLO
import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class Test(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.title("PRUEBA")
        self.geometry("400x300")
        ctk.CTkLabel(self, text="SI VES ESTO → CustomTkinter funciona perfecto").pack(expand=True, pady=50)
        ctk.CTkButton(self, text="Cerrar", command=self.destroy).pack(pady=20)

app = ctk.CTk()
ctk.CTkButton(app, text="Abrir ventana", command=Test).pack(expand=True)
app.mainloop()