# ============================================================
# Romex QC Desktop — Vistas formales v2.5
# Siembra = datos fijos del sistema web (no editables)
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
ACCENT_DARK = "#0d47a1"
ACCENT_SOFT = "#e3f2fd"
CARD = "#ffffff"
TEXT = "#1a2332"
TEXT_SEC = "#5a6a7a"
BORDER = "#d0d7de"
OK = "#0d7a3f"
WARN = "#e65100"
WARN_BG = "#fff3e0"
SURFACE = "#f0f4f8"
LOCKED_BG = "#f1f5f9"


class MainAppViews:
    def _get_row(self, rows, month):
        for r in rows:
            if r["Mes"] == month:
                return r
        return None

    def _is_siembra_month(self):
        bl = BASELINES.get(self.active_codigo, {})
        return (
            self.active_year == bl.get("anio_inicio")
            and self.active_month == bl.get("mes_inicio")
        )

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
        is_siembra = self._is_siembra_month()

        # —— Nota formal de siembra ——
        note = ctk.CTkFrame(self.content, fg_color=WARN_BG if is_siembra else ACCENT_SOFT, corner_radius=10)
        note.pack(fill="x", pady=(0, 12))
        fecha_s = bl.get("fecha_siembra", "—")
        mes_s = MONTH_NAMES.get(bl.get("mes_inicio"), "")
        anio_s = bl.get("anio_inicio", "")
        if is_siembra:
            txt = f"  SIEMBRA (punto de partida)  ·  {mes_s} {anio_s}  ·  Fecha: {fecha_s}  ·  Datos fijos del análisis inicial  ·  Solo lectura"
        else:
            txt = f"  Siembra de referencia: {mes_s} {anio_s} ({fecha_s})  ·  Comparación: siembra vs resultado del mes  ·  Columna Siembra no editable"
        ctk.CTkLabel(note, text=txt, font=ctk.CTkFont(size=11), text_color=WARN if is_siembra else ACCENT).pack(anchor="w", padx=14, pady=10)

        # —— Encabezado documento formal ——
        info = ctk.CTkFrame(self.content, fg_color=CARD, corner_radius=12)
        info.pack(fill="x", pady=(0, 14))

        bar = ctk.CTkFrame(info, fg_color="transparent")
        bar.pack(fill="x", padx=22, pady=(16, 4))
        ctk.CTkLabel(bar, text=COMPANY_NAME, font=ctk.CTkFont(size=13, weight="bold"), text_color=ACCENT).pack(side="left")
        ctk.CTkLabel(bar, text=f"{DOC_CODE}  ·  Ed. 19", font=ctk.CTkFont(size=11), text_color=TEXT_SEC).pack(side="right")

        ctk.CTkLabel(info, text=PLANT_NAME, font=ctk.CTkFont(size=11), text_color=TEXT_SEC).pack(anchor="w", padx=22)

        head = ctk.CTkFrame(info, fg_color=ACCENT_SOFT, corner_radius=8)
        head.pack(fill="x", padx=22, pady=(12, 12))
        titulo = f"{'SIEMBRA · ' if is_siembra else ''}{'Microbiología' if self.active_mode == 'micro' else 'Físicoquímico'}  ·  {self.active_producto['Nombre']}  ·  {mes_name} {self.active_year}"
        ctk.CTkLabel(head, text=titulo, font=ctk.CTkFont(size=13, weight="bold"), text_color=ACCENT_DARK).pack(padx=14, pady=10)

        grid = ctk.CTkFrame(info, fg_color="transparent")
        grid.pack(fill="x", padx=22, pady=(0, 16))
        cells = [
            ("Producto", self.active_producto["Nombre"]),
            ("Lote", self.active_producto["Lote"]),
            ("Mes / Año", f"{mes_name}  {self.active_year}"),
            ("Fecha siembra", fecha_s),
            ("Analista", "Nereyda Huachua Flores"),
            ("Estado", "SIEMBRA" if is_siembra else "EN SEGUIMIENTO"),
        ]
        for i, (lbl, val) in enumerate(cells):
            cell = ctk.CTkFrame(grid, fg_color="#f8fafc", corner_radius=8)
            cell.grid(row=i // 3, column=i % 3, sticky="ew", padx=3, pady=3)
            grid.columnconfigure(i % 3, weight=1)
            ctk.CTkLabel(cell, text=lbl.upper(), font=ctk.CTkFont(size=9), text_color=TEXT_SEC).pack(anchor="w", padx=12, pady=(8, 0))
            color = WARN if val == "SIEMBRA" else (OK if val == "EN SEGUIMIENTO" else TEXT)
            ctk.CTkLabel(cell, text=str(val), font=ctk.CTkFont(size=12, weight="bold"), text_color=color).pack(anchor="w", padx=12, pady=(2, 8))

        if self.active_mode == "micro":
            self._render_micro(bl, mes_name, is_siembra)
        else:
            self._render_fisico(bl, mes_name, is_siembra)

    def _render_micro(self, bl, mes_name, is_siembra):
        row = self._get_row(self.micro_rows, self.active_month)
        baseline = bl.get("micro", {})

        card = ctk.CTkFrame(self.content, fg_color=CARD, corner_radius=12)
        card.pack(fill="x", pady=(0, 14))

        title = "Promedio de siembra (ufc/gr) — FIJO" if is_siembra else "Microbiología (ufc/gr) — Siembra fija vs Resultado del mes"
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT).pack(anchor="w", padx=22, pady=(16, 10))

        table = ctk.CTkFrame(card, fg_color="transparent")
        table.pack(fill="x", padx=22, pady=(0, 6))

        hdr = ctk.CTkFrame(table, fg_color="#e8eef4", corner_radius=8)
        hdr.pack(fill="x", pady=(0, 4))
        for col, w in [("Parámetro", 150), ("Siembra (fijo)", 120), ("Resultado mes", 120), ("Estado", 110)]:
            ctk.CTkLabel(hdr, text=col, width=w, font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SEC).pack(side="left", padx=8, pady=9)

        data = {}
        dbmap = {
            "rtamv": "RTAMV", "mohos": "Mohos", "coliformes": "Coliformes", "ecoli": "EColi",
            "enterobacterias": "Enterobacterias", "levaduras": "Levaduras", "saureus": "SAureus"
        }
        for key in MICRO_KEYS:
            val = row.get(dbmap.get(key, key), 0) if row else (baseline.get(key, 0) if is_siembra else 0)
            data[key] = val
            rf = ctk.CTkFrame(table, fg_color="transparent")
            rf.pack(fill="x", pady=1)

            ctk.CTkLabel(rf, text=MICRO_LABELS[key], width=150, anchor="w",
                         font=ctk.CTkFont(size=12), text_color=TEXT).pack(side="left", padx=8, pady=5)

            # SIEMBRA FIJA — nunca editable
            base_val = baseline.get(key, 0)
            ctk.CTkLabel(
                rf, text=str(base_val), width=120,
                font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SEC,
                fg_color=LOCKED_BG, corner_radius=6
            ).pack(side="left", padx=8, pady=2, ipady=4)

            # Resultado del mes — editable solo ADMIN y si NO es solo vista siembra sin fila
            var = ctk.StringVar(value=str(val if val is not None else 0))
            self.entry_vars[key] = var
            can_edit = self.is_admin and not is_siembra
            ent = ctk.CTkEntry(
                rf, textvariable=var, width=120, height=32, corner_radius=8,
                fg_color="#f8fafc" if can_edit else LOCKED_BG,
                border_color=BORDER, text_color=TEXT, font=ctk.CTkFont(size=12),
                state="normal" if can_edit else "disabled"
            )
            ent.pack(side="left", padx=8)
            if can_edit:
                ent.bind("<FocusOut>", lambda e, k=key: self._autosave_micro())

            estado = "SIEMBRA" if is_siembra else "LIBERADO"
            ctk.CTkLabel(rf, text=estado, width=110, font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=WARN if is_siembra else OK).pack(side="left", padx=8)

        if self.is_admin and not is_siembra:
            ctk.CTkButton(card, text="Guardar resultado del mes", width=200, height=36, corner_radius=8,
                          fg_color=ACCENT, hover_color=ACCENT_DARK, font=ctk.CTkFont(size=12, weight="bold"),
                          command=self._autosave_micro).pack(anchor="e", padx=22, pady=(8, 16))
        else:
            ctk.CTkLabel(card, text="Columna Siembra: datos del análisis inicial (no modificables)",
                         font=ctk.CTkFont(size=10), text_color=TEXT_SEC).pack(anchor="w", padx=22, pady=(4, 14))

        self._draw_micro_charts(data, baseline, mes_name)

    def _draw_micro_charts(self, data, baseline, mes_name):
        cc = ctk.CTkFrame(self.content, fg_color=CARD, corner_radius=12)
        cc.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(cc, text=f"Gráfico  ·  Siembra (fijo) vs {mes_name}",
                     font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT).pack(anchor="w", padx=22, pady=(16, 6))
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
            ctk.CTkLabel(tc, text="Tendencia  ·  RTAMV (línea de siembra de referencia)",
                         font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT).pack(anchor="w", padx=22, pady=(16, 6))
            th = ctk.CTkFrame(tc, fg_color="transparent")
            th.pack(fill="x", padx=14, pady=(0, 14))
            try:
                w2, c2, f2 = create_trend_chart(
                    th, self.micro_rows, "RTAMV", "RTAMV", COLORS.get("rtamv", ACCENT),
                    baseline_value=baseline.get("rtamv"), y_label="ufc/gr"
                )
                w2.pack(fill="x")
                self.trend_canvas, self.trend_fig = c2, f2
            except Exception:
                pass

    def _render_fisico(self, bl, mes_name, is_siembra):
        row = self._get_row(self.fisico_rows, self.active_month)
        baseline = bl.get("fisico", {})
        fields = list(baseline.keys()) if baseline else ["humedad", "ph", "ceniza", "grasa"]

        card = ctk.CTkFrame(self.content, fg_color=CARD, corner_radius=12)
        card.pack(fill="x", pady=(0, 14))

        title = "Promedio de siembra — FIJO" if is_siembra else "Físicoquímico — Siembra fija vs Resultado del mes"
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT).pack(anchor="w", padx=22, pady=(16, 10))

        table = ctk.CTkFrame(card, fg_color="transparent")
        table.pack(fill="x", padx=22, pady=(0, 6))

        hdr = ctk.CTkFrame(table, fg_color="#e8eef4", corner_radius=8)
        hdr.pack(fill="x", pady=(0, 4))
        for col, w in [("Parámetro", 150), ("Siembra (fijo)", 120), ("Resultado mes", 120), ("Estado", 110)]:
            ctk.CTkLabel(hdr, text=col, width=w, font=ctk.CTkFont(size=11, weight="bold"), text_color=TEXT_SEC).pack(side="left", padx=8, pady=9)

        data = {}
        dbmap = {"humedad": "Humedad", "ph": "PH", "ceniza": "Ceniza", "grasa": "Grasa", "fineza": "Fineza", "acidez": "Acidez"}
        for key in fields:
            val = row.get(dbmap.get(key, key)) if row else (baseline.get(key) if is_siembra else None)
            data[key] = val
            rf = ctk.CTkFrame(table, fg_color="transparent")
            rf.pack(fill="x", pady=1)

            ctk.CTkLabel(rf, text=FISICO_LABELS.get(key, key), width=150, anchor="w",
                         font=ctk.CTkFont(size=12), text_color=TEXT).pack(side="left", padx=8, pady=5)

            bv = baseline.get(key)
            base_txt = f"{bv:.2f}" if bv is not None else "—"
            ctk.CTkLabel(
                rf, text=base_txt, width=120,
                font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_SEC,
                fg_color=LOCKED_BG, corner_radius=6
            ).pack(side="left", padx=8, pady=2, ipady=4)

            display = f"{float(val):.2f}" if val is not None else ""
            var = ctk.StringVar(value=display)
            self.entry_vars[key] = var
            can_edit = self.is_admin and not is_siembra
            ent = ctk.CTkEntry(
                rf, textvariable=var, width=120, height=32, corner_radius=8,
                fg_color="#f8fafc" if can_edit else LOCKED_BG,
                border_color=BORDER, text_color=TEXT, font=ctk.CTkFont(size=12),
                state="normal" if can_edit else "disabled"
            )
            ent.pack(side="left", padx=8)
            if can_edit:
                ent.bind("<FocusOut>", lambda e, k=key: self._autosave_fisico())

            estado = "SIEMBRA" if is_siembra else "CONFORME"
            ctk.CTkLabel(rf, text=estado, width=110, font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=WARN if is_siembra else OK).pack(side="left", padx=8)

        if self.is_admin and not is_siembra:
            ctk.CTkButton(card, text="Guardar resultado del mes", width=200, height=36, corner_radius=8,
                          fg_color=ACCENT, hover_color=ACCENT_DARK, font=ctk.CTkFont(size=12, weight="bold"),
                          command=self._autosave_fisico).pack(anchor="e", padx=22, pady=(8, 16))
        else:
            ctk.CTkLabel(card, text="Columna Siembra: datos del análisis inicial (no modificables)",
                         font=ctk.CTkFont(size=10), text_color=TEXT_SEC).pack(anchor="w", padx=22, pady=(4, 14))

        cc = ctk.CTkFrame(self.content, fg_color=CARD, corner_radius=12)
        cc.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(cc, text=f"Gráfico  ·  Siembra (fijo) vs {mes_name}",
                     font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT).pack(anchor="w", padx=22, pady=(16, 6))
        host = ctk.CTkFrame(cc, fg_color="transparent")
        host.pack(fill="x", padx=14, pady=(0, 14))
        try:
            widget, canvas, fig = create_fisico_bar_chart(host, data, fields, baseline=baseline, mes_label=mes_name)
            widget.pack(fill="x")
            self.chart_canvas, self.chart_fig = canvas, fig
        except Exception:
            ctk.CTkLabel(host, text="Gráfico no disponible", text_color=TEXT_SEC).pack(pady=16)
