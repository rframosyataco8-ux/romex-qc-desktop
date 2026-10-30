# ============================================================
# Romex QC Desktop — Ventana de Login
# ============================================================

import customtkinter as ctk
from tkinter import messagebox
from config import APP_TITLE, COMPANY_NAME, PLANT_NAME, APP_VERSION
from db.queries import login_user
from db.connection import test_connection, DatabaseError


class LoginWindow(ctk.CTk):
    def __init__(self, on_success):
        super().__init__()
        self.on_success = on_success

        self.title(f"Iniciar sesión · {APP_TITLE}")
        self.geometry("440x520")
        self.resizable(False, False)
        self.configure(fg_color="#0f172a")

        self.update_idletasks()
        w, h = 440, 520
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._build_ui()
        self.after(100, self._check_db)

    def _build_ui(self):
        card = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=16, border_width=0)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.88, relheight=0.90)

        icon_frame = ctk.CTkFrame(card, fg_color="#1565c0", width=64, height=64, corner_radius=16)
        icon_frame.pack(pady=(28, 8))
        icon_frame.pack_propagate(False)
        ctk.CTkLabel(icon_frame, text="🔬", font=ctk.CTkFont(size=28)).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            card, text=COMPANY_NAME,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#f1f5f9"
        ).pack(pady=(4, 0))

        ctk.CTkLabel(
            card, text=f"{PLANT_NAME}  ·  Control de Calidad",
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8"
        ).pack(pady=(2, 18))

        self.db_status = ctk.CTkLabel(
            card, text="Verificando base de datos…",
            font=ctk.CTkFont(size=11),
            text_color="#64748b"
        )
        self.db_status.pack(pady=(0, 12))

        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="x", padx=32)

        ctk.CTkLabel(form, text="Usuario", font=ctk.CTkFont(size=12), text_color="#cbd5e1", anchor="w").pack(fill="x")
        self.entry_user = ctk.CTkEntry(
            form, placeholder_text="ej. admin",
            height=40, corner_radius=8,
            fg_color="#0f172a", border_color="#334155",
            text_color="#f1f5f9", placeholder_text_color="#64748b"
        )
        self.entry_user.pack(fill="x", pady=(4, 12))

        ctk.CTkLabel(form, text="Contraseña", font=ctk.CTkFont(size=12), text_color="#cbd5e1", anchor="w").pack(fill="x")
        self.entry_pass = ctk.CTkEntry(
            form, placeholder_text="••••••••",
            show="•", height=40, corner_radius=8,
            fg_color="#0f172a", border_color="#334155",
            text_color="#f1f5f9", placeholder_text_color="#64748b"
        )
        self.entry_pass.pack(fill="x", pady=(4, 8))
        self.entry_pass.bind("<Return>", lambda e: self._do_login())

        self.lbl_error = ctk.CTkLabel(form, text="", font=ctk.CTkFont(size=11), text_color="#f87171")
        self.lbl_error.pack(pady=(0, 8))

        self.btn_login = ctk.CTkButton(
            form, text="Iniciar sesión",
            height=42, corner_radius=8,
            fg_color="#1565c0", hover_color="#0d47a1",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._do_login
        )
        self.btn_login.pack(fill="x", pady=(4, 16))

        ctk.CTkLabel(
            card,
            text="Usuarios de prueba:\nadmin / admin123   ·   nereyda / romex2026\nlector / lector123",
            font=ctk.CTkFont(size=10),
            text_color="#64748b",
            justify="center"
        ).pack(pady=(0, 8))

        ctk.CTkLabel(
            card, text=f"v{APP_VERSION}",
            font=ctk.CTkFont(size=10),
            text_color="#475569"
        ).pack(side="bottom", pady=10)

        self.entry_user.focus()

    def _check_db(self):
        ok, msg = test_connection()
        if ok:
            self.db_status.configure(text=f"● {msg}", text_color="#4ade80")
        else:
            self.db_status.configure(text="● Sin conexión a SQL Server", text_color="#f87171")
            self.lbl_error.configure(text=msg[:120] + ("…" if len(msg) > 120 else ""))

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
