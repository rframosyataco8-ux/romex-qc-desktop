# ============================================================
# Romex QC Desktop — Login · estética visual v2.8
# ============================================================

import customtkinter as ctk
from tkinter import messagebox
from config import APP_TITLE, COMPANY_NAME, PLANT_NAME, APP_VERSION, DOC_CODE
from db.queries import login_user
from db.connection import test_connection, DatabaseError


BG = "#040b14"
PRIMARY = "#1565c0"
PRIMARY_DARK = "#0d47a1"
PRIMARY_MID = "#1976d2"
CARD = "#ffffff"
TEXT = "#0f172a"
TEXT_SEC = "#64748b"
MUTED = "#94a3b8"
BORDER = "#e2e8f0"
INPUT_BG = "#f8fafc"
OK = "#15803d"
ERR = "#dc2626"


class LoginWindow(ctk.CTk):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success
        self.title(f"Acceso · {APP_TITLE}")
        self.geometry("1020x640")
        self.resizable(False, False)
        self.configure(fg_color=BG)

        self.update_idletasks()
        w, h = 1020, 640
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._build()
        self.after(120, self._check_db)

    def _build(self):
        left = ctk.CTkFrame(self, fg_color=PRIMARY, corner_radius=0, width=450)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        li = ctk.CTkFrame(left, fg_color="transparent")
        li.pack(expand=True, fill="both", padx=56, pady=64)

        badge = ctk.CTkFrame(li, fg_color="#0d47a1", width=64, height=64, corner_radius=20)
        badge.pack(anchor="w")
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text="R", font=ctk.CTkFont(size=28, weight="bold"), text_color="#ffffff").place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(li, text="Romex QC", font=ctk.CTkFont(size=36, weight="bold"), text_color="#ffffff").pack(anchor="w", pady=(32, 0))
        ctk.CTkLabel(li, text="Estudio de Vida Útil", font=ctk.CTkFont(size=16), text_color="#bfdbfe").pack(anchor="w", pady=(10, 0))

        ctk.CTkFrame(li, fg_color="#93c5fd", height=3, width=56).pack(anchor="w", pady=(40, 36))

        ctk.CTkLabel(li, text=COMPANY_NAME, font=ctk.CTkFont(size=14, weight="bold"), text_color="#e0f2fe").pack(anchor="w")
        ctk.CTkLabel(li, text=PLANT_NAME, font=ctk.CTkFont(size=13), text_color="#93c5fd").pack(anchor="w", pady=(8, 0))
        ctk.CTkLabel(li, text=f"Documento  {DOC_CODE}  ·  Edición 19", font=ctk.CTkFont(size=12), text_color="#7dd3fc").pack(anchor="w", pady=(24, 0))

        ctk.CTkLabel(li, text=f"Versión {APP_VERSION}", font=ctk.CTkFont(size=11), text_color="#7dd3fc").pack(side="bottom", anchor="w")

        right = ctk.CTkFrame(self, fg_color=CARD, corner_radius=0)
        right.pack(side="left", fill="both", expand=True)

        form = ctk.CTkFrame(right, fg_color="transparent")
        form.pack(expand=True, padx=72, pady=64)

        ctk.CTkLabel(form, text="Iniciar sesión", font=ctk.CTkFont(size=30, weight="bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(form, text="Credenciales de Control de Calidad", font=ctk.CTkFont(size=14), text_color=TEXT_SEC).pack(anchor="w", pady=(12, 0))

        self.db_status = ctk.CTkLabel(form, text="", font=ctk.CTkFont(size=12), text_color=MUTED)
        self.db_status.pack(anchor="w", pady=(32, 0))

        ctk.CTkLabel(form, text="USUARIO", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SEC).pack(anchor="w", pady=(32, 0))
        self.entry_user = ctk.CTkEntry(
            form, placeholder_text="Nombre de usuario",
            height=50, corner_radius=14,
            fg_color=INPUT_BG, border_color=BORDER, border_width=1,
            text_color=TEXT, placeholder_text_color=MUTED, font=ctk.CTkFont(size=14)
        )
        self.entry_user.pack(fill="x", pady=(12, 0))

        ctk.CTkLabel(form, text="CONTRASEÑA", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SEC).pack(anchor="w", pady=(22, 0))
        self.entry_pass = ctk.CTkEntry(
            form, placeholder_text="••••••••",
            show="•", height=50, corner_radius=14,
            fg_color=INPUT_BG, border_color=BORDER, border_width=1,
            text_color=TEXT, placeholder_text_color=MUTED, font=ctk.CTkFont(size=14)
        )
        self.entry_pass.pack(fill="x", pady=(12, 0))
        self.entry_pass.bind("<Return>", lambda e: self._do_login())

        self.lbl_error = ctk.CTkLabel(form, text="", font=ctk.CTkFont(size=12), text_color=ERR)
        self.lbl_error.pack(anchor="w", pady=(16, 0))

        self.btn_login = ctk.CTkButton(
            form, text="Entrar al sistema",
            height=52, corner_radius=14,
            fg_color=PRIMARY, hover_color=PRIMARY_DARK,
            font=ctk.CTkFont(size=15, weight="bold"), command=self._do_login
        )
        self.btn_login.pack(fill="x", pady=(20, 0))

        ctk.CTkLabel(
            form, text="Acceso restringido al personal autorizado",
            font=ctk.CTkFont(size=12), text_color=MUTED
        ).pack(anchor="w", pady=(28, 0))

        self.entry_user.focus()

    def _check_db(self):
        ok, msg = test_connection()
        if ok:
            self.db_status.configure(text="●  Conectado a SQL Server", text_color=OK)
        else:
            self.db_status.configure(text="●  Sin conexión a la base de datos", text_color=ERR)
            self.lbl_error.configure(text=(msg[:90] + "…") if len(msg) > 90 else msg)

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
            self.btn_login.configure(text="Acceso concedido…", fg_color=OK)
            self.after(250, lambda: self._finish_login(user))
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
