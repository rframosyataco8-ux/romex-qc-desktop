# ============================================================
# Romex QC Desktop v2.0
# Exportadora Romex S.A. · Planta Chincha
# Estudio de Vida Útil — Aplicación de escritorio
# ============================================================
"""
Punto de entrada de la aplicación.

Uso:
    python main.py
"""

import sys
import os

# Asegurar que el directorio del proyecto esté en el path
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import customtkinter as ctk
from ui.login_window import LoginWindow
from ui.main_app import MainApp


def main():
    # Tema global
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    def on_login_success(user):
        app = MainApp(user)
        app.mainloop()

    login = LoginWindow(on_success=on_login_success)
    login.mainloop()


if __name__ == "__main__":
    main()
