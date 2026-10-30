# ============================================================
# Romex QC Desktop — Ventana principal (diseño profesional v2.2)
# Exportadora Romex S.A. · Planta Chincha
# ============================================================

import customtkinter as ctk
from tkinter import messagebox, simpledialog
from datetime import date

from config import (
    APP_TITLE, COMPANY_NAME, PLANT_NAME, DOC_CODE, APP_VERSION,
    MONTH_NAMES, MONTH_NAMES_SHORT, MICRO_KEYS, MICRO_LABELS,
    FISICO_KEYS, FISICO_LABELS, BASELINES, COLORS
)
from db.queries import (
    get_productos, get_producto_by_codigo, create_producto,
    get_micro, get_fisico, upsert_micro, upsert_fisico,
    log_audit, get_auditoria, get_all_users, create_user
)
from db.connection import DatabaseError
from utils.charts import (
    create_micro_bar_chart, create_fisico_bar_chart,
    create_trend_chart, destroy_chart
)

# Paleta corporativa (Material Design — sistema web original)
SIDEBAR_BG = "#0d1b2a"
SIDEBAR_HOVER = "#1b2838"
SIDEBAR_ACTIVE = "#1565c0"
ACCENT = "#1565c0"
ACCENT_DARK = "#0d47a1"
ACCENT_SOFT = "#e3f2fd"
SURFACE = "#f0f4f8"
CARD = "#ffffff"
TEXT = "#1a2332"
TEXT_SEC = "#5a6a7a"
BORDER = "#d0d7de"
OK = "#0d7a3f"

from ui.app_views import MainAppViews
from ui.app_actions import MainAppActions


class MainApp(ctk.CTk, MainAppViews, MainAppActions):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.is_admin = user["rol"] == "ADMIN"
        self.title(f"{APP_TITLE}  ·  {user['nombre']}")
        self.geometry("1360x840")
        self.minsize(1120, 720)
        self.configure(fg_color=SURFACE)
        self.productos = []
        self.active_codigo = None
        self.active_producto = None
        self.active_year = 2026
        self.active_month = 5
        self.active_mode = "micro"
        self.micro_rows = []
        self.fisico_rows = []
        self.chart_canvas = None
        self.chart_fig = None
        self.trend_canvas = None
        self.trend_fig = None
        self.entry_vars = {}
        self.product_btns = {}
        self._build_layout()
        self.after(60, self._load_productos)

    def _build_layout(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=272, corner_radius=0, fg_color=SIDEBAR_BG)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        hdr = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        hdr.pack(fill="x", padx=22, pady=(28, 6))
        ctk.CTkLabel(hdr, text="Romex QC", font=ctk.CTkFont(size=20, weight="bold"), text_color="#ffffff").pack(anchor="w")
        ctk.CTkLabel(hdr, text=f"Estudio de vida útil  ·  v{APP_VERSION}", font=ctk.CTkFont(size=11), text_color="#90a4ae").pack(anchor="w", pady=(4, 0))

        ctk.CTkLabel(self.sidebar, text="PRODUCTOS", font=ctk.CTkFont(size=10, weight="bold"), text_color="#78909c").pack(anchor="w", padx=22, pady=(32, 10))

        self.product_list = ctk.CTkScrollableFrame(
            self.sidebar, fg_color="transparent",
            scrollbar_button_color="#37474f", scrollbar_button_hover_color="#546e7a"
        )
        self.product_list.pack(fill="both", expand=True, padx=12, pady=4)

        if self.is_admin:
            act = ctk.CTkFrame(self.sidebar, fg_color="transparent")
            act.pack(fill="x", padx=16, pady=(10, 6))
            ctk.CTkButton(act, text="+  Nuevo producto", height=36, corner_radius=8,
                fg_color=SIDEBAR_HOVER, hover_color="#263238", font=ctk.CTkFont(size=12),
                command=self._add_producto).pack(fill="x", pady=3)
            ctk.CTkButton(act, text="Auditoría", height=36, corner_radius=8,
                fg_color=SIDEBAR_HOVER, hover_color="#263238", font=ctk.CTkFont(size=12),
                command=self._show_audit).pack(fill="x", pady=3)

        foot = ctk.CTkFrame(self.sidebar, fg_color="#132033", corner_radius=0, height=108)
        foot.pack(side="bottom", fill="x")
        foot.pack_propagate(False)
        ctk.CTkLabel(foot, text=self.user["nombre"], font=ctk.CTkFont(size=13, weight="bold"), text_color="#eceff1").pack(anchor="w", padx=22, pady=(18, 0))
        rol = "Administrador" if self.is_admin else "Solo lectura"
        ctk.CTkLabel(foot, text=f"{rol}  ·  {PLANT_NAME}", font=ctk.CTkFont(size=11), text_color="#90a4ae").pack(anchor="w", padx=22, pady=(2, 0))
        ctk.CTkButton(foot, text="Cerrar sesión", height=30, corner_radius=6,
            fg_color="transparent", hover_color="#263238", text_color="#90a4ae",
            font=ctk.CTkFont(size=11), command=self._logout).pack(anchor="w", padx=16, pady=(10, 0))

        # Main
        self.main = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0)
        self.main.pack(side="left", fill="both", expand=True)

        top = ctk.CTkFrame(self.main, fg_color=CARD, height=68, corner_radius=0)
        top.pack(fill="x")
        top.pack_propagate(False)
        top_inner = ctk.CTkFrame(top, fg_color="transparent")
        top_inner.pack(fill="both", expand=True, padx=28, pady=14)

        self.lbl_title = ctk.CTkLabel(top_inner, text="Seleccione un producto",
            font=ctk.CTkFont(size=18, weight="bold"), text_color=TEXT)
        self.lbl_title.pack(side="left")

        self.lbl_lote = ctk.CTkLabel(top_inner, text="", font=ctk.CTkFont(size=12, weight="bold"),
            text_color=ACCENT, fg_color=ACCENT_SOFT, corner_radius=14)
        self.lbl_lote.pack(side="left", padx=(14, 0), ipadx=12, ipady=5)

        self.year_var = ctk.StringVar(value="2026")
        ctk.CTkOptionMenu(top_inner, values=["2025", "2026", "2027"], variable=self.year_var,
            width=92, height=34, fg_color="#f8fafc", button_color=BORDER,
            button_hover_color="#cfd8dc", text_color=TEXT, font=ctk.CTkFont(size=12),
            command=self._on_year_change).pack(side="right", padx=(8, 0))

        self.mode_frame = ctk.CTkFrame(top_inner, fg_color="#e8eef4", corner_radius=10)
        self.mode_frame.pack(side="right", padx=(16, 8))
        self.btn_micro = ctk.CTkButton(self.mode_frame, text="Microbiología", width=124, height=32,
            corner_radius=8, fg_color=CARD, text_color=ACCENT, hover_color="#f8fafc",
            font=ctk.CTkFont(size=12, weight="bold"), command=lambda: self._set_mode("micro"))
        self.btn_micro.pack(side="left", padx=3, pady=3)
        self.btn_fisico = ctk.CTkButton(self.mode_frame, text="Físicoquímico", width=124, height=32,
            corner_radius=8, fg_color="transparent", text_color=TEXT_SEC, hover_color="#f8fafc",
            font=ctk.CTkFont(size=12), command=lambda: self._set_mode("fisico"))
        self.btn_fisico.pack(side="left", padx=3, pady=3)

        self.lbl_save = ctk.CTkLabel(top_inner, text="", font=ctk.CTkFont(size=11), text_color=TEXT_SEC)
        self.lbl_save.pack(side="right", padx=(0, 12))

        self.tabs_frame = ctk.CTkFrame(self.main, fg_color=CARD, height=48, corner_radius=0)
        self.tabs_frame.pack(fill="x")
        self.tabs_frame.pack_propagate(False)
        self.tabs_inner = ctk.CTkFrame(self.tabs_frame, fg_color="transparent")
        self.tabs_inner.pack(fill="both", expand=True, padx=24, pady=6)

        self.content = ctk.CTkScrollableFrame(self.main, fg_color=SURFACE, scrollbar_button_color="#cfd8dc")
        self.content.pack(fill="both", expand=True, padx=24, pady=20)

        self.status = ctk.CTkLabel(self.main, text=f"{COMPANY_NAME}  ·  {DOC_CODE}  ·  {PLANT_NAME}",
            font=ctk.CTkFont(size=10), text_color=TEXT_SEC, anchor="w", height=28)
        self.status.pack(fill="x", padx=28, pady=(0, 8))

    def _load_productos(self):
        try:
            self.productos = get_productos(solo_activos=True)
        except DatabaseError as e:
            messagebox.showerror("Error", str(e))
            return
        self._render_product_list()
        if self.productos:
            self._select_producto(self.productos[0]["Codigo"])

    def _render_product_list(self):
        for w in self.product_list.winfo_children():
            w.destroy()
        self.product_btns = {}
        for p in self.productos:
            codigo = p["Codigo"]
            btn = ctk.CTkButton(
                self.product_list,
                text=f"{p['Nombre']}\nLote {p['Lote']}",
                anchor="w", height=54, corner_radius=10,
                fg_color="transparent", hover_color=SIDEBAR_HOVER,
                text_color="#cfd8dc", font=ctk.CTkFont(size=12),
                command=lambda c=codigo: self._select_producto(c)
            )
            btn.pack(fill="x", pady=3, padx=4)
            self.product_btns[codigo] = btn

    def _select_producto(self, codigo):
        self.active_codigo = codigo
        self.active_producto = next((p for p in self.productos if p["Codigo"] == codigo), None)
        if not self.active_producto:
            return
        for c, btn in self.product_btns.items():
            if c == codigo:
                btn.configure(fg_color=SIDEBAR_ACTIVE, text_color="#ffffff")
            else:
                btn.configure(fg_color="transparent", text_color="#cfd8dc")
        self.lbl_title.configure(text=self.active_producto["Nombre"])
        self.lbl_lote.configure(text=f"  Lote {self.active_producto['Lote']}  ")
        self._load_month_data()

    def _on_year_change(self, value):
        self.active_year = int(value)
        self._load_month_data()

    def _set_mode(self, mode):
        self.active_mode = mode
        if mode == "micro":
            self.btn_micro.configure(fg_color=CARD, text_color=ACCENT, font=ctk.CTkFont(size=12, weight="bold"))
            self.btn_fisico.configure(fg_color="transparent", text_color=TEXT_SEC, font=ctk.CTkFont(size=12))
        else:
            self.btn_fisico.configure(fg_color=CARD, text_color=ACCENT, font=ctk.CTkFont(size=12, weight="bold"))
            self.btn_micro.configure(fg_color="transparent", text_color=TEXT_SEC, font=ctk.CTkFont(size=12))
        self._render_content()

    def _load_month_data(self):
        if not self.active_producto:
            return
        try:
            self.micro_rows = get_micro(self.active_producto["Id"], self.active_year)
            self.fisico_rows = get_fisico(self.active_producto["Id"], self.active_year)
        except DatabaseError as e:
            messagebox.showerror("Error", str(e))
            return
        months = sorted(set([r["Mes"] for r in self.micro_rows] + [r["Mes"] for r in self.fisico_rows]))
        if not months:
            months = [BASELINES.get(self.active_codigo, {}).get("mes_inicio", 5)]
        if self.active_month not in months:
            self.active_month = months[0]
        self._render_tabs(months)
        self._render_content()

    def _render_tabs(self, months):
        for w in self.tabs_inner.winfo_children():
            w.destroy()
        for m in months:
            is_active = m == self.active_month
            ctk.CTkButton(
                self.tabs_inner, text=MONTH_NAMES_SHORT.get(m, str(m)), width=66, height=32,
                corner_radius=8,
                fg_color=ACCENT if is_active else "transparent",
                text_color="#ffffff" if is_active else TEXT_SEC,
                hover_color=ACCENT_DARK if is_active else "#f0f4f8",
                font=ctk.CTkFont(size=12, weight="bold" if is_active else "normal"),
                command=lambda mm=m: self._select_month(mm)
            ).pack(side="left", padx=3)
        if self.is_admin:
            ctk.CTkButton(
                self.tabs_inner, text="+ Mes", width=72, height=32, corner_radius=8,
                fg_color="transparent", text_color=ACCENT, hover_color=ACCENT_SOFT,
                font=ctk.CTkFont(size=12), command=self._add_month
            ).pack(side="left", padx=(12, 0))

    def _select_month(self, month):
        self.active_month = month
        months = sorted(set([r["Mes"] for r in self.micro_rows] + [r["Mes"] for r in self.fisico_rows]))
        if not months:
            months = [BASELINES.get(self.active_codigo, {}).get("mes_inicio", 5)]
        self._render_tabs(months)
        self._render_content()
