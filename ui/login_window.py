# ============================================================
# Romex QC Desktop — Login profesional + fluidez v2.3
# ============================================================

import customtkinter as ctk
from tkinter import messagebox
from config import APP_TITLE, COMPANY_NAME, PLANT_NAME, APP_VERSION, DOC_CODE
from db.queries import login_user
from db.connection import test_connection, DatabaseError


BG = "#0a1628"
PRIMARY = "#1565c0"
PRIMARY_DARK = "#0d47a1"
PRIMARY_MID = "#1976d2"
CARD = "#ffffff"
TEXT = "#1a2332"
TEXT_SEC = "#5a6a7a"
MUTED = "#90a4ae"
BORDER = "#e8eef4"
INPUT_BG = "#f7fafc"
OK = "#0d7a3f"
ERR = "#c62828"


class LoginWindow(ctk.CTk):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success

        self.title(f"Acceso · {APP_TITLE}")
        self.geometry("960x580")
        self.resizable(False, False)
        self.configure(fg_color=BG)

        self.update_idletasks()
        w, h = 960, 580
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._build()
        # Carga escalonada (sensación de fluidez)
        self.after(80, self._reveal_form)
        self.after(200, self._check_db)

    def _build(self):
        # Panel marca
        left = ctk.CTkFrame(self, fg_color=PRIMARY, corner_radius=0, width=400)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        li = ctk.CTkFrame(left, fg_color="transparent")
        li.pack(expand=True, fill="both", padx=44, pady=52)

        # Marca
        badge = ctk.CTkFrame(li, fg_color="#0d47a1", width=52, height=52, corner_radius=14)
        badge.pack(anchor="w")
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text="R", font=ctk.CTkFont(size=22, weight="bold"), text_color="#ffffff").place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(li, text="Romex QC", font=ctk.CTkFont(size=30, weight="bold"), text_color="#ffffff").pack(anchor="w", pady=(22, 0))
        ctk.CTkLabel(li, text="Estudio de Vida Útil", font=ctk.CTkFont(size=15), text_color="#bbdefb").pack(anchor="w", pady=(6, 0))

        ctk.CTkFrame(li, fg_color="#64b5f6", height=2, width=56).pack(anchor="w", pady=(28, 24))

        ctk.CTkLabel(li, text=COMPANY_NAME, font=ctk.CTkFont(size=13, weight="bold"), text_color="#e3f2fd").pack(anchor="w")
        ctk.CTkLabel(li, text=PLANT_NAME, font=ctk.CTkFont(size=12), text_color="#90caf9").pack(anchor="w", pady=(4, 0))
        ctk.CTkLabel(li, text=f"Documento  {DOC_CODE}", font=ctk.CTkFont(size=11), text_color="#64b5f6").pack(anchor="w", pady=(18, 0))

        ctk.CTkLabel(li, text=f"Versión {APP_VERSION}", font=ctk.CTkFont(size=10), text_color="#64b5f6").pack(side="bottom", anchor="w")

        # Formulario
        right = ctk.CTkFrame(self, fg_color=CARD, corner_radius=0)
        right.pack(side="left", fill="both", expand=True)

        self.form = ctk.CTkFrame(right, fg_color="transparent")
        self.form.pack(expand=True, padx=60, pady=52)

        # Empieza invisible para revelar con fluidez
        self.form_widgets = []

        t1 = ctk.CTkLabel(self.form, text="Iniciar sesión", font=ctk.CTkFont(size=24, weight="bold"), text_color=TEXT)
        t1.pack(anchor="w")
        t2 = ctk.CTkLabel(self.form, text="Credenciales de Control de Calidad", font=ctk.CTkFont(size=13), text_color=TEXT_SEC)
        t2.pack(anchor="w", pady=(8, 0))

        self.db_status = ctk.CTkLabel(self.form, text="", font=ctk.CTkFont(size=11), text_color=MUTED)
        self.db_status.pack(anchor="w", pady=(22, 0))

        ctk.CTkLabel(self.form, text="Usuario", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SEC).pack(anchor="w", pady=(20, 0))
        self.entry_user = ctk.CTkEntry(
            self.form, placeholder_text="Nombre de usuario",
            height=44, corner_radius=10,
            fg_color=INPUT_BG, border_color=BORDER, border_width=1,
            text_color=TEXT, placeholder_text_color=MUTED,
            font=ctk.CTkFont(size=13)
        )
        self.entry_user.pack(fill="x", pady=(8, 0))

        ctk.CTkLabel(self.form, text="Contraseña", font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SEC).pack(anchor="w", pady=(16, 0))
        self.entry_pass = ctk.CTkEntry(
            self.form, placeholder_text="••••••••",
            show="•", height=44, corner_radius=10,
            fg_color=INPUT_BG, border_color=BORDER, border_width=1,
            text_color=TEXT, placeholder_text_color=MUTED,
            font=ctk.CTkFont(size=13)
        )
        self.entry_pass.pack(fill="x", pady=(8, 0))
        self.entry_pass.bind("<Return>", lambda e: self._do_login())

        self.lbl_error = ctk.CTkLabel(self.form, text="", font=ctk.CTkFont(size=11), text_color=ERR)
        self.lbl_error.pack(anchor="w", pady=(10, 0))

        self.btn_login = ctk.CTkButton(
            self.form, text="Entrar al sistema",
            height=46, corner_radius=10,
            fg_color=PRIMARY, hover_color=PRIMARY_DARK,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._do_login
        )
        self.btn_login.pack(fill="x", pady=(14, 0))

        ctk.CTkLabel(
            self.form,
            text="admin / admin123   ·   nereyda / romex2026   ·   lector / lector123",
            font=ctk.CTkFont(size=10), text_color=MUTED
        ).pack(anchor="w", pady=(18, 0))

        self.entry_user.focus()

    def _reveal_form(self):
        # Feedback visual suave al abrir
        self.btn_login.configure(fg_color=PRIMARY_MID)
        self.after(120, lambda: self.btn_login.configure(fg_color=PRIMARY))

    def _check_db(self):
        ok, msg = test_connection()
        if ok:
            self.db_status.configure(text="●  Conectado a SQL Server", text_color=OK)
        else:
            self.db_status.configure(text="●  Sin conexión a la base de datos", text_color=ERR)
            short = msg[:90] + ("…" if len(msg) > 90 else "")
            self.lbl_error.configure(text=short)

    def _do_login(self):
        usuario = self.entry_user.get().strip()
        password = self.entry_pass.get()
        if not usuario or not password:
            self.lbl_error.configure(text="Ingrese usuario y contraseña")
            return

        self.btn_login.configure(state="disabled", text="Verificando…", fg_color=PRIMARY_MID)
        self.lbl_error.configure(text="")
        self.update()

        try:
            user = login_user(usuario, password)
            if user is None:
                self.lbl_error.configure(text="Usuario o contraseña incorrectos")
                self.btn_login.configure(state="normal", text="Entrar al sistema", fg_color=PRIMARY)
                return
            # Transición suave antes de abrir main
            self.btn_login.configure(text="Acceso concedido…", fg_color=OK)
            self.after(280, lambda: self._finish_login(user))
        except DatabaseError as e:
            self.lbl_error.configure(text="Error de base de datos")
            messagebox.showerror("Error de conexión", str(e))
            self.btn_login.configure(state="normal", text="Entrar al sistema", fg_color=PRIMARY)
        except Exception as e:
            self.lbl_error.configure(text=str(e)[:80])
            self.btn_login.configure(state="normal", text="Entrar al sistema", fg_color=PRIMARY)

    def _finish_login(self, user):
        self.on_success(user)
        self.destroy()
