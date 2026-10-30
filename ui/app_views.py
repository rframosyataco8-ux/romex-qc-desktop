# ============================================================
# Romex QC Desktop — Vistas profesionales v2.4
# ============================================================
import customtkinter as ctk
from config import (
    COMPANY_NAME, PLANT_NAME, DOC_CODE, MONTH_NAMES,
    MICRO_KEYS, MICRO_LABELS, FISICO_LABELS, BASELINES, COLORS
)
from utils.charts import (
    create_micro_bar_chart, create_fisico_bar_chart,
    create_trend_chart, destroy_chart
)

ACCENT = "#1565c0"
ACCENT_SOFT = "#e3f2fd"
CARD = "#ffffff"
TEXT = "#1a2332"
TEXT_SEC = "#5a6a7a"
BORDER = "#d0d7de"
OK = "#0d7a3f"
SURFACE = "#f0f4f8"


class MainAppViews:
    def _get_row(self, rows, month):
        for r in rows:
            if r["Mes"] == month:
                return r
        return None

    def _render_content(self):
        for w in self.content.winfo_children():
            w.destroy()
        destroy_chart(self.chart_canvas, self.chart_fig)
        destroy_chart(self.trend_canvas, self.trend_fig)
        self.chart_canvas = self.chart_fig = None
        self.trend_canvas = self.trend_fig = None
        self.entry_vars = {}
        if not self.active_producto:
            return

        bl = BASELINES.get(self.active_codigo, {})
        mes_name = MONTH_NAMES.get(self.active_month, str(self.active_month))

        info = ctk.CTkFrame(self.content, fg_color=CARD, corner_radius=12)
        info.pack(fill="x", pady=(0, 14))

        top = ctk.CTkFrame(info, fg_color="transparent")
        top.pack(fill="x", padx=22, pady=(16, 6))
        ctk.CTkLabel(top, text=COMPANY_NAME, font=ctk.CTkFont(size=13, weight="bold"), text_color=ACCENT).pack(side="left")
        ctk.CTkLabel(top, text=f"{DOC_CODE}  ·  {PLANT_NAME}", font=ctk.CTkFont(size=11), text_color=TEXT_SEC).pack(side="right")

        ctk.CTkLabel(info, text=f"Resultados  ·  {mes_name} {self.active_year}",
                     font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT).pack(anchor="w", padx=22, pady=(2, 10))

        grid = ctk.CTkFrame(info, fg_color="transparent")
        grid.pack(fill="x", padx=22, pady=(0, 16))
        cells = [
            ("Producto", self.active_producto["Nombre"]),
            ("Lote", self.active_producto["Lote"]),
            ("Mes / Año", f"{mes_name}  {self.active_year}"),
            ("Siembra", bl.get("fecha_siembra", "—")),
        ]
        for i, (lbl, val) in enumerate(cells):
            cell = ctk.CTkFrame(grid, fg_color="#f8fafc", corner_radius=8)
            cell.grid(row=0, column=i, sticky="ew", padx=3)
            grid.columnconfigure(i, weight=1)
            ctk.CTkLabel(cell, text=lbl, font=ctk.CTkFont(size=10), text_color=TEXT_SEC).pack(anchor="w", padx=12, pady=(8, 0))
            ctk.CTkLabel(cell, text=str(val), font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT).pack(anchor="w", padx=12, pady=(1, 8))

        if self.active_mode == "micro":
            self._render_micro(bl, mes_name)
        else:
            self._render_fisico(bl, mes_name)

    def _render_micro(self, bl, mes_name):
        row = self._get_row(self.micro_rows, self.active_month)
        baseline = bl.get("micro", {})
        card = ctk.CTkFrame(self.content, fg_color=CARD, corner_radius=12)
        card.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(card, text="Microbiología  (ufc/gr)", font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT).pack(anchor="w", padx=22, pady=(16, 10))

        table = ctk.CTkFrame(card, fg_color="transparent")
        table.pack(fill="x", padx=22, pady=(0, 6))
        hdr = ctk.CTkFrame(table, fg_color="#f0f4f8", corner_radius=8)
        hdr.pack(fill="x", pady=(0, 4))
        for col, w in [("Parámetro", 140), ("Siembra", 100), ("Resultado", 120), ("Estado", 100)]:
            ctk.CTkLabel(hdr, text=col, width=w, font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SEC).pack(side="left", padx=8, pady=8)

        data = {}
        dbmap = {"rtamv": "RTAMV", "mohos": "Mohos", "coliformes": "Coliformes", "ecoli": "EColi",
                 "enterobacterias": "Enterobacterias", "levaduras": "Levaduras", "saureus": "SAureus"}
        for key in MICRO_KEYS:
            val = row.get(dbmap.get(key, key), 0) if row else 0
            data[key] = val
            rf = ctk.CTkFrame(table, fg_color="transparent")
            rf.pack(fill="x", pady=1)
            ctk.CTkLabel(rf, text=MICRO_LABELS[key], width=140, anchor="w", font=ctk.CTkFont(size=12), text_color=TEXT).pack(side="left", padx=8, pady=5)
            ctk.CTkLabel(rf, text=str(baseline.get(key, 0)), width=100, font=ctk.CTkFont(size=12), text_color=TEXT_SEC).pack(side="left", padx=8)
            var = ctk.StringVar(value=str(val if val is not None else 0))
            self.entry_vars[key] = var
            ent = ctk.CTkEntry(rf, textvariable=var, width=100, height=32, corner_radius=8,
                               fg_color="#f8fafc", border_color=BORDER, text_color=TEXT, font=ctk.CTkFont(size=12),
                               state="normal" if self.is_admin else "disabled")
            ent.pack(side="left", padx=8)
            if self.is_admin:
                ent.bind("<FocusOut>", lambda e, k=key: self._autosave_micro())
            ctk.CTkLabel(rf, text="LIBERADO", width=100, font=ctk.CTkFont(size=11), text_color=OK).pack(side="left", padx=8)

        if self.is_admin:
            ctk.CTkButton(card, text="Guardar", width=140, height=34, corner_radius=8,
                          fg_color=ACCENT, hover_color="#0d47a1", font=ctk.CTkFont(size=12, weight="bold"),
                          command=self._autosave_micro).pack(anchor="e", padx=22, pady=(6, 16))
        else:
            ctk.CTkFrame(card, height=10, fg_color="transparent").pack()

        cc = ctk.CTkFrame(self.content, fg_color=CARD, corner_radius=12)
        cc.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(cc, text=f"Comparación  ·  Siembra vs {mes_name}", font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT).pack(anchor="w", padx=22, pady=(16, 6))
        host = ctk.CTkFrame(cc, fg_color="transparent")
        host.pack(fill="x", padx=14, pady=(0, 14))
        try:
            widget, canvas, fig = create_micro_bar_chart(host, data, baseline=baseline, mes_label=mes_name)
            widget.pack(fill="x")
            self.chart_canvas, self.chart_fig = canvas, fig
        except Exception:
            ctk.CTkLabel(host, text="Gráfico no disponible", text_color=TEXT_SEC).pack(pady=16)

        if self.micro_rows:
            tc = ctk.CTkFrame(self.content, fg_color=CARD, corner_radius=12)
            tc.pack(fill="x", pady=(0, 14))
            ctk.CTkLabel(tc, text="Tendencia  ·  RTAMV", font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT).pack(anchor="w", padx=22, pady=(16, 6))
            th = ctk.CTkFrame(tc, fg_color="transparent")
            th.pack(fill="x", padx=14, pady=(0, 14))
            try:
                w2, c2, f2 = create_trend_chart(th, self.micro_rows, "RTAMV", "RTAMV", COLORS.get("rtamv", ACCENT),
                                                 baseline_value=baseline.get("rtamv"), y_label="ufc/gr")
                w2.pack(fill="x")
                self.trend_canvas, self.trend_fig = c2, f2
            except Exception:
                pass

    def _render_fisico(self, bl, mes_name):
        row = self._get_row(self.fisico_rows, self.active_month)
        baseline = bl.get("fisico", {})
        fields = list(baseline.keys()) if baseline else ["humedad", "ph", "ceniza", "grasa"]
        card = ctk.CTkFrame(self.content, fg_color=CARD, corner_radius=12)
        card.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(card, text="Físicoquímico", font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT).pack(anchor="w", padx=22, pady=(16, 10))

        table = ctk.CTkFrame(card, fg_color="transparent")
        table.pack(fill="x", padx=22, pady=(0, 6))
        hdr = ctk.CTkFrame(table, fg_color="#f0f4f8", corner_radius=8)
        hdr.pack(fill="x", pady=(0, 4))
        for col, w in [("Parámetro", 140), ("Siembra", 100), ("Resultado", 120), ("Estado", 100)]:
            ctk.CTkLabel(hdr, text=col, width=w, font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SEC).pack(side="left", padx=8, pady=8)

        data = {}
        dbmap = {"humedad": "Humedad", "ph": "PH", "ceniza": "Ceniza", "grasa": "Grasa", "fineza": "Fineza", "acidez": "Acidez"}
        for key in fields:
            val = row.get(dbmap.get(key, key)) if row else None
            data[key] = val
            rf = ctk.CTkFrame(table, fg_color="transparent")
            rf.pack(fill="x", pady=1)
            ctk.CTkLabel(rf, text=FISICO_LABELS.get(key, key), width=140, anchor="w", font=ctk.CTkFont(size=12), text_color=TEXT).pack(side="left", padx=8, pady=5)
            bv = baseline.get(key)
            ctk.CTkLabel(rf, text=f"{bv:.2f}" if bv is not None else "—", width=100, font=ctk.CTkFont(size=12), text_color=TEXT_SEC).pack(side="left", padx=8)
            display = f"{float(val):.2f}" if val is not None else ""
            var = ctk.StringVar(value=display)
            self.entry_vars[key] = var
            ent = ctk.CTkEntry(rf, textvariable=var, width=100, height=32, corner_radius=8,
                               fg_color="#f8fafc", border_color=BORDER, text_color=TEXT, font=ctk.CTkFont(size=12),
                               state="normal" if self.is_admin else "disabled")
            ent.pack(side="left", padx=8)
            if self.is_admin:
                ent.bind("<FocusOut>", lambda e, k=key: self._autosave_fisico())
            ctk.CTkLabel(rf, text="CONFORME", width=100, font=ctk.CTkFont(size=11), text_color=OK).pack(side="left", padx=8)

        if self.is_admin:
            ctk.CTkButton(card, text="Guardar", width=140, height=34, corner_radius=8,
                          fg_color=ACCENT, hover_color="#0d47a1", font=ctk.CTkFont(size=12, weight="bold"),
                          command=self._autosave_fisico).pack(anchor="e", padx=22, pady=(6, 16))
        else:
            ctk.CTkFrame(card, height=10, fg_color="transparent").pack()

        cc = ctk.CTkFrame(self.content, fg_color=CARD, corner_radius=12)
        cc.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(cc, text=f"Comparación  ·  Siembra vs {mes_name}", font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT).pack(anchor="w", padx=22, pady=(16, 6))
        host = ctk.CTkFrame(cc, fg_color="transparent")
        host.pack(fill="x", padx=14, pady=(0, 14))
        try:
            widget, canvas, fig = create_fisico_bar_chart(host, data, fields, baseline=baseline, mes_label=mes_name)
            widget.pack(fill="x")
            self.chart_canvas, self.chart_fig = canvas, fig
        except Exception:
            ctk.CTkLabel(host, text="Gráfico no disponible", text_color=TEXT_SEC).pack(pady=16)
