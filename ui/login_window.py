# ============================================================
# Romex QC Desktop — Login corporativo profesional
# ============================================================

import customtkinter as ctk
from tkinter import messagebox
from config import APP_TITLE, COMPANY_NAME, PLANT_NAME, APP_VERSION, DOC_CODE
from db.queries import login_user
from db.connection import test_connection, DatabaseError


# Paleta corporativa (alineada al sistema web Material)
BG = "#0d1b2a"
PANEL = "#1b2838"
CARD = "#ffffff"
PRIMARY = "#1565c0"
PRIMARY_DARK = "#0d47a1"
PRIMARY_SOFT = "#e3f2fd"
TEXT = "#1a2332"
TEXT_SEC = "#5a6a7a"
MUTED = "#90a4ae"
BORDER = "#e0e6ed"
OK = "#0d7a3f"
ERR = "#c62828"


class LoginWindow(ctk.CTk):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success

        self.title(f"Acceso · {APP_TITLE}")
        self.geometry("920x560")
        self.resizable(False, False)
        self.configure(fg_color=BG)

        self.update_idletasks()
        w, h = 920, 560
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._build()
        self.after(100, self._check_db)

    def _build(self):
        # —— Panel izquierdo (marca) ——
        left = ctk.CTkFrame(self, fg_color=PRIMARY, corner_radius=0, width=380)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        left_inner = ctk.CTkFrame(left, fg_color="transparent")
        left_inner.pack(expand=True, fill="both", padx=40, pady=48)

        ctk.CTkLabel(
            left_inner, text="Romex QC",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#ffffff"
        ).pack(anchor="w")

        ctk.CTkLabel(
            left_inner, text="Estudio de Vida Útil",
            font=ctk.CTkFont(size=15),
            text_color="#bbdefb"
        ).pack(anchor="w", pady=(6, 0))

        ctk.CTkFrame(left_inner, fg_color="#64b5f6", height=2, width=64).pack(anchor="w", pady=(28, 28))

        ctk.CTkLabel(
            left_inner, text=COMPANY_NAME,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#e3f2fd"
        ).pack(anchor="w")
        ctk.CTkLabel(
            left_inner, text=PLANT_NAME,
            font=ctk.CTkFont(size=12),
            text_color="#90caf9"
        ).pack(anchor="w", pady=(4, 0))
        ctk.CTkLabel(
            left_inner, text=f"Documento  {DOC_CODE}",
            font=ctk.CTkFont(size=11),
            text_color="#64b5f6"
        ).pack(anchor="w", pady=(16, 0))

        ctk.CTkLabel(
            left_inner, text=f"Versión {APP_VERSION}",
            font=ctk.CTkFont(size=10),
            text_color="#64b5f6"
        ).pack(side="bottom", anchor="w")

        # —— Panel derecho (formulario) ——
        right = ctk.CTkFrame(self, fg_color=CARD, corner_radius=0)
        right.pack(side="left", fill="both", expand=True)

        form = ctk.CTkFrame(right, fg_color="transparent")
        form.pack(expand=True, padx=56, pady=48)

        ctk.CTkLabel(
            form, text="Iniciar sesión",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT
        ).pack(anchor="w")
        ctk.CTkLabel(
            form, text="Use sus credenciales de Control de Calidad",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SEC
        ).pack(anchor="w", pady=(6, 28))

        self.db_status = ctk.CTkLabel(
            form, text="Comprobando conexión…",
            font=ctk.CTkFont(size=11),
            text_color=MUTED
        )
        self.db_status.pack(anchor="w", pady=(0, 20))

        ctk.CTkLabel(form, text="Usuario", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SEC).pack(anchor="w")
        self.entry_user = ctk.CTkEntry(
            form, placeholder_text="Nombre de usuario",
            height=42, corner_radius=8,
            fg_color="#f8fafc", border_color=BORDER, border_width=1,
            text_color=TEXT, placeholder_text_color=MUTED,
            font=ctk.CTkFont(size=13)
        )
        self.entry_user.pack(fill="x", pady=(6, 16))

        ctk.CTkLabel(form, text="Contraseña", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SEC).pack(anchor="w")
        self.entry_pass = ctk.CTkEntry(
            form, placeholder_text="••••••••",
            show="•", height=42, corner_radius=8,
            fg_color="#f8fafc", border_color=BORDER, border_width=1,
            text_color=TEXT, placeholder_text_color=MUTED,
            font=ctk.CTkFont(size=13)
        )
        self.entry_pass.pack(fill="x", pady=(6, 8))
        self.entry_pass.bind("<Return>", lambda e: self._do_login())

        self.lbl_error = ctk.CTkLabel(form, text="", font=ctk.CTkFont(size=11), text_color=ERR)
        self.lbl_error.pack(anchor="w", pady=(4, 12))

        self.btn_login = ctk.CTkButton(
            form, text="Entrar al sistema",
            height=44, corner_radius=8,
            fg_color=PRIMARY, hover_color=PRIMARY_DARK,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._do_login
        )
        self.btn_login.pack(fill="x", pady=(4, 20))

        ctk.CTkLabel(
            form,
            text="admin / admin123    ·    nereyda / romex2026    ·    lector / lector123",
            font=ctk.CTkFont(size=10),
            text_color=MUTED
        ).pack(anchor="w")

        self.entry_user.focus()

    def _check_db(self):
        ok, msg = test_connection()
        if ok:
            self.db_status.configure(text=f"●  Conectado a SQL Server", text_color=OK)
        else:
            self.db_status.configure(text="●  Sin conexión a la base de datos", text_color=ERR)
            self.lbl_error.configure(text=(msg[:90] + "…") if len(msg) > 90 else msg)

    def _do_login(self):
        usuario = self.entry_user.get().strip()
        password = self.entry_pass.get()
        if not usuario or not password:
            self.lbl_error.configure(text="Ingrese usuario y contraseña")
            return
        self.btn_login.configure(state="disabled", text="Verificando…")
        self.lbl_error.configure(text="")
        self.update()
        try:
            user = login_user(usuario, password)
            if user is None:
                self.lbl_error.configure(text="Usuario o contraseña incorrectos")
                self.btn_login.configure(state="normal", text="Entrar al sistema")
                return
            self.on_success(user)
            self.destroy()
        except DatabaseError as e:
            self.lbl_error.configure(text="Error de base de datos")
            messagebox.showerror("Error de conexión", str(e))
            self.btn_login.configure(state="normal", text="Entrar al sistema")
        except Exception as e:
            self.lbl_error.configure(text=str(e)[:80])
            self.btn_login.configure(state="normal", text="Entrar al sistema")
