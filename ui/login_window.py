# ============================================================
# Romex QC Desktop — Login · diseño sistema v2.7
# ============================================================

import customtkinter as ctk
from tkinter import messagebox
from config import APP_TITLE, COMPANY_NAME, PLANT_NAME, APP_VERSION, DOC_CODE
from db.queries import login_user
from db.connection import test_connection, DatabaseError


BG = "#050d18"
PRIMARY = "#1565c0"
PRIMARY_DARK = "#0d47a1"
PRIMARY_MID = "#1976d2"
CARD = "#ffffff"
TEXT = "#15202b"
TEXT_SEC = "#546e7a"
MUTED = "#90a4ae"
BORDER = "#e2e8f0"
INPUT_BG = "#f8fafc"
OK = "#1b7a3d"
ERR = "#c62828"


class LoginWindow(ctk.CTk):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success
        self.title(f"Acceso · {APP_TITLE}")
        self.geometry("1000x620")
        self.resizable(False, False)
        self.configure(fg_color=BG)

        self.update_idletasks()
        w, h = 1000, 620
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._build()
        self.after(120, self._check_db)

    def _build(self):
        left = ctk.CTkFrame(self, fg_color=PRIMARY, corner_radius=0, width=440)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        li = ctk.CTkFrame(left, fg_color="transparent")
        li.pack(expand=True, fill="both", padx=52, pady=60)

        badge = ctk.CTkFrame(li, fg_color="#0d47a1", width=60, height=60, corner_radius=18)
        badge.pack(anchor="w")
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text="R", font=ctk.CTkFont(size=26, weight="bold"), text_color="#ffffff").place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(li, text="Romex QC", font=ctk.CTkFont(size=34, weight="bold"), text_color="#ffffff").pack(anchor="w", pady=(28, 0))
        ctk.CTkLabel(li, text="Estudio de Vida Útil", font=ctk.CTkFont(size=15), text_color="#bbdefb").pack(anchor="w", pady=(8, 0))

        ctk.CTkFrame(li, fg_color="#64b5f6", height=3, width=52).pack(anchor="w", pady=(36, 32))

        ctk.CTkLabel(li, text=COMPANY_NAME, font=ctk.CTkFont(size=14, weight="bold"), text_color="#e3f2fd").pack(anchor="w")
        ctk.CTkLabel(li, text=PLANT_NAME, font=ctk.CTkFont(size=13), text_color="#90caf9").pack(anchor="w", pady=(6, 0))
        ctk.CTkLabel(li, text=f"Documento  {DOC_CODE}  ·  Edición 19", font=ctk.CTkFont(size=12), text_color="#64b5f6").pack(anchor="w", pady=(22, 0))

        ctk.CTkLabel(li, text=f"Versión {APP_VERSION}", font=ctk.CTkFont(size=11), text_color="#64b5f6").pack(side="bottom", anchor="w")

        right = ctk.CTkFrame(self, fg_color=CARD, corner_radius=0)
        right.pack(side="left", fill="both", expand=True)

        form = ctk.CTkFrame(right, fg_color="transparent")
        form.pack(expand=True, padx=68, pady=60)

        ctk.CTkLabel(form, text="Iniciar sesión", font=ctk.CTkFont(size=28, weight="bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(form, text="Credenciales de Control de Calidad", font=ctk.CTkFont(size=13), text_color=TEXT_SEC).pack(anchor="w", pady=(10, 0))

        self.db_status = ctk.CTkLabel(form, text="", font=ctk.CTkFont(size=12), text_color=MUTED)
        self.db_status.pack(anchor="w", pady=(28, 0))

        ctk.CTkLabel(form, text="USUARIO", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SEC).pack(anchor="w", pady=(28, 0))
        self.entry_user = ctk.CTkEntry(
            form, placeholder_text="Nombre de usuario",
            height=48, corner_radius=12,
            fg_color=INPUT_BG, border_color=BORDER, border_width=1,
            text_color=TEXT, placeholder_text_color=MUTED, font=ctk.CTkFont(size=14)
        )
        self.entry_user.pack(fill="x", pady=(10, 0))

        ctk.CTkLabel(form, text="CONTRASEÑA", font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SEC).pack(anchor="w", pady=(20, 0))
        self.entry_pass = ctk.CTkEntry(
            form, placeholder_text="••••••••",
            show="•", height=48, corner_radius=12,
            fg_color=INPUT_BG, border_color=BORDER, border_width=1,
            text_color=TEXT, placeholder_text_color=MUTED, font=ctk.CTkFont(size=14)
        )
        self.entry_pass.pack(fill="x", pady=(10, 0))
        self.entry_pass.bind("<Return>", lambda e: self._do_login())

        self.lbl_error = ctk.CTkLabel(form, text="", font=ctk.CTkFont(size=12), text_color=ERR)
        self.lbl_error.pack(anchor="w", pady=(14, 0))

        self.btn_login = ctk.CTkButton(
            form, text="Entrar al sistema",
            height=50, corner_radius=12,
            fg_color=PRIMARY, hover_color=PRIMARY_DARK,
            font=ctk.CTkFont(size=15, weight="bold"), command=self._do_login
        )
        self.btn_login.pack(fill="x", pady=(18, 0))

        ctk.CTkLabel(
            form, text="Acceso restringido al personal autorizado",
            font=ctk.CTkFont(size=11), text_color=MUTED
        ).pack(anchor="w", pady=(24, 0))

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
