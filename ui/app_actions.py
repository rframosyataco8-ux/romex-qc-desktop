# ============================================================
# Romex QC Desktop — Acciones (guardar, productos, auditoría)
# ============================================================

import customtkinter as ctk
from tkinter import messagebox, simpledialog

from config import BASELINES
from db.queries import (
    upsert_micro, upsert_fisico, log_audit, get_auditoria,
    get_micro, get_fisico, create_producto
)
from db.connection import DatabaseError

OK = "#16a34a"
SURFACE = "#f1f5f9"
TEXT = "#0f172a"
TEXT_SEC = "#64748b"


class MainAppActions:
    """Guardado y acciones administrativas."""

    def _autosave_micro(self):
        if not self.is_admin or not self.active_producto:
            return
        data = {}
        for key, var in self.entry_vars.items():
            try:
                data[key] = int(float(var.get() or 0))
            except ValueError:
                data[key] = 0
        try:
            upsert_micro(
                self.active_producto["Id"], self.active_year, self.active_month,
                data, analista=self.user["nombre"]
            )
            log_audit(self.user["nombre"], "UPDATE", "MICRO",
                      self.active_codigo, self.active_year, self.active_month)
            self.lbl_save.configure(text="Guardado", text_color=OK)
            self.after(2000, lambda: self.lbl_save.configure(text=""))
            self.micro_rows = get_micro(self.active_producto["Id"], self.active_year)
        except DatabaseError as e:
            messagebox.showerror("Error al guardar", str(e))

    def _autosave_fisico(self):
        if not self.is_admin or not self.active_producto:
            return
        data = {}
        for key, var in self.entry_vars.items():
            raw = var.get().strip()
            if raw == "":
                data[key] = None
            else:
                try:
                    data[key] = float(raw)
                except ValueError:
                    data[key] = None
        try:
            upsert_fisico(
                self.active_producto["Id"], self.active_year, self.active_month,
                data, analista=self.user["nombre"]
            )
            log_audit(self.user["nombre"], "UPDATE", "FISICO",
                      self.active_codigo, self.active_year, self.active_month)
            self.lbl_save.configure(text="Guardado", text_color=OK)
            self.after(2000, lambda: self.lbl_save.configure(text=""))
            self.fisico_rows = get_fisico(self.active_producto["Id"], self.active_year)
        except DatabaseError as e:
            messagebox.showerror("Error al guardar", str(e))

    def _add_month(self):
        if not self.is_admin or not self.active_producto:
            return
        mes = simpledialog.askinteger(
            "Agregar mes", "Número de mes (1-12):",
            minvalue=1, maxvalue=12, parent=self
        )
        if not mes:
            return
        try:
            upsert_micro(self.active_producto["Id"], self.active_year, mes, {}, analista=self.user["nombre"])
            upsert_fisico(self.active_producto["Id"], self.active_year, mes, {}, analista=self.user["nombre"])
            log_audit(self.user["nombre"], "INSERT", "MES", self.active_codigo, self.active_year, mes)
            self.active_month = mes
            self._load_month_data()
        except DatabaseError as e:
            messagebox.showerror("Error", str(e))

    def _add_producto(self):
        if not self.is_admin:
            return
        nombre = simpledialog.askstring("Nuevo producto", "Nombre del producto:", parent=self)
        if not nombre:
            return
        lote = simpledialog.askstring("Nuevo producto", "Lote:", parent=self)
        if not lote:
            return
        codigo = nombre.strip().lower().replace(" ", "_")[:40]
        try:
            create_producto(codigo, nombre.strip(), lote.strip())
            log_audit(self.user["nombre"], "INSERT", "PRODUCTO", codigo)
            self._load_productos()
        except DatabaseError as e:
            messagebox.showerror("Error", str(e))

    def _show_audit(self):
        try:
            rows = get_auditoria(80)
        except DatabaseError as e:
            messagebox.showerror("Error", str(e))
            return
        win = ctk.CTkToplevel(self)
        win.title("Auditoría")
        win.geometry("720x480")
        win.transient(self)
        frame = ctk.CTkScrollableFrame(win, fg_color=SURFACE)
        frame.pack(fill="both", expand=True, padx=16, pady=16)
        if not rows:
            ctk.CTkLabel(frame, text="Sin registros", text_color=TEXT_SEC).pack(pady=40)
            return
        for r in rows:
            line = f"{r.get('CreadoEn', '')}  ·  {r.get('UsuarioNombre', '')}  ·  {r.get('Accion', '')}  {r.get('Entidad', '')}  {r.get('Codigo') or ''}"
            ctk.CTkLabel(
                frame, text=line, anchor="w",
                font=ctk.CTkFont(size=12), text_color=TEXT
            ).pack(fill="x", pady=3)

    def _logout(self):
        self.destroy()
        from ui.login_window import LoginWindow
        from ui.main_app import MainApp

        def on_ok(user):
            app = MainApp(user)
            app.mainloop()

        login = LoginWindow(on_ok)
        login.mainloop()
