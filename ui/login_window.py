# ============================================================
# Romex QC Desktop — Login (diseño limpio y profesional)
# ============================================================

import customtkinter as ctk
from tkinter import messagebox
from config import APP_TITLE, COMPANY_NAME, PLANT_NAME, APP_VERSION
from db.queries import login_user
from db.connection import test_connection, DatabaseError


BG = "#0f172a"
CARD = "#1e293b"
ACCENT = "#2563eb"
ACCENT_HOVER = "#1d4ed8"
TEXT = "#f8fafc"
TEXT_MUTED = "#94a3b8"
BORDER = "#334155"
INPUT_BG = "#0f172a"
OK = "#22c55e"
ERR = "#f87171"


class LoginWindow(ctk.CTk):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success

        self.title(f"Iniciar sesión · {APP_TITLE}")
        self.geometry("480x560")
        self.resizable(False, False)
        self.configure(fg_color=BG)

        self.update_idletasks()
        w, h = 480, 560
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._build()
        self.after(120, self._check_db)

    def _build(self):
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(expand=True, fill="both", padx=40, pady=36)

        card = ctk.CTkFrame(outer, fg_color=CARD, corner_radius=20)
        card.pack(fill="both", expand=True, padx=8, pady=8)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=36, pady=32)

        icon = ctk.CTkFrame(inner, fg_color=ACCENT, width=56, height=56, corner_radius=14)
        icon.pack(pady=(8, 16))
        icon.pack_propagate(False)
        ctk.CTkLabel(icon, text="🔬", font=ctk.CTkFont(size=24)).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            inner, text=COMPANY_NAME,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=TEXT
        ).pack()
        ctk.CTkLabel(
            inner, text=f"{PLANT_NAME}  ·  Control de Calidad",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED
        ).pack(pady=(4, 20))

        self.db_status = ctk.CTkLabel(
            inner, text="Verificando base de datos…",
            font=ctk.CTkFont(size=11),
            text_color=TEXT_MUTED
        )
        self.db_status.pack(pady=(0, 20))

        ctk.CTkLabel(
            inner, text="Usuario",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED, anchor="w"
        ).pack(fill="x")
        self.entry_user = ctk.CTkEntry(
            inner, placeholder_text="ej. admin",
            height=44, corner_radius=10,
            fg_color=INPUT_BG, border_color=BORDER, border_width=1,
            text_color=TEXT, placeholder_text_color="#64748b",
            font=ctk.CTkFont(size=13)
        )
        self.entry_user.pack(fill="x", pady=(6, 16))

        ctk.CTkLabel(
            inner, text="Contraseña",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED, anchor="w"
        ).pack(fill="x")
        self.entry_pass = ctk.CTkEntry(
            inner, placeholder_text="••••••••",
            show="•", height=44, corner_radius=10,
            fg_color=INPUT_BG, border_color=BORDER, border_width=1,
            text_color=TEXT, placeholder_text_color="#64748b",
            font=ctk.CTkFont(size=13)
        )
        self.entry_pass.pack(fill="x", pady=(6, 8))
        self.entry_pass.bind("<Return>", lambda e: self._do_login())

        self.lbl_error = ctk.CTkLabel(
            inner, text="",
            font=ctk.CTkFont(size=11),
            text_color=ERR
        )
        self.lbl_error.pack(pady=(4, 12))

        self.btn_login = ctk.CTkButton(
            inner, text="Iniciar sesión",
            height=44, corner_radius=10,
            fg_color=ACCENT, hover_color=ACCENT_HOVER,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._do_login
        )
        self.btn_login.pack(fill="x", pady=(4, 20))

        ctk.CTkLabel(
            inner,
            text="admin / admin123   ·   nereyda / romex2026\nlector / lector123",
            font=ctk.CTkFont(size=10),
            text_color="#64748b",
            justify="center"
        ).pack()

        ctk.CTkLabel(
            inner, text=f"v{APP_VERSION}",
            font=ctk.CTkFont(size=10),
            text_color="#475569"
        ).pack(side="bottom", pady=(16, 0))

        self.entry_user.focus()

    def _check_db(self):
        ok, msg = test_connection()
        if ok:
            self.db_status.configure(text=f"●  {msg}", text_color=OK)
        else:
            self.db_status.configure(text="●  Sin conexión a SQL Server", text_color=ERR)
            short = msg[:100] + ("…" if len(msg) > 100 else "")
            self.lbl_error.configure(text=short)

    def _do_login(self):
        usuario = self.entry_user.get().strip()
        password = self.entry_pass.get()

        if not usuario or not password:
            self.lbl_error.configure(text="Ingresa usuario y contraseña")
            return

        self.btn_login.configure(state="disabled", text="Verificando…")
        self.lbl_error.configure(text="")
        self.update()

        try:
            user = login_user(usuario, password)
            if user is None:
                self.lbl_error.configure(text="Usuario o contraseña incorrectos")
                self.btn_login.configure(state="normal", text="Iniciar sesión")
                return
            self.on_success(user)
            self.destroy()
        except DatabaseError as e:
            self.lbl_error.configure(text="Error de base de datos")
            messagebox.showerror("Error de conexión", str(e))
            self.btn_login.configure(state="normal", text="Iniciar sesión")
        except Exception as e:
            self.lbl_error.configure(text=str(e)[:80])
            self.btn_login.configure(state="normal", text="Iniciar sesión")
