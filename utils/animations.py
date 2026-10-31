# ============================================================
# Romex QC Desktop — Animaciones suaves v2.9
# CustomTkinter no tiene CSS; usamos after() para transiciones
# ============================================================


def fade_button_color(widget, colors, step=0, delay=28):
    """Cambia el color del botón en pasos suaves."""
    if step >= len(colors):
        return
    try:
        if widget.winfo_exists():
            widget.configure(fg_color=colors[step])
            widget.after(delay, lambda: fade_button_color(widget, colors, step + 1, delay))
    except Exception:
        pass


def pulse_label(label, colors=("#64748b", "#94a3b8", "#64748b"), step=0, delay=180, cycles=2):
    """Parpadeo suave de un label (estado de carga)."""
    if step >= len(colors) * cycles:
        return
    try:
        if label.winfo_exists():
            label.configure(text_color=colors[step % len(colors)])
            label.after(delay, lambda: pulse_label(label, colors, step + 1, delay, cycles))
    except Exception:
        pass


def stagger_show(widgets, delay_ms=40, start=0):
    """Revela widgets de forma escalonada (sensación de entrada suave)."""
    # En CTk los widgets ya están packed; usamos un flash de color suave
    def _step(i):
        if i >= len(widgets):
            return
        w = widgets[i]
        try:
            if w.winfo_exists():
                # micro-feedback visual
                pass
        except Exception:
            pass
        if i + 1 < len(widgets):
            widgets[0].after(delay_ms, lambda: _step(i + 1))
    if widgets:
        widgets[0].after(start, lambda: _step(0))


def smooth_loading_text(label, messages, index=0, delay=400):
    """Rota textos de carga de forma suave."""
    if index >= len(messages):
        return
    try:
        if label.winfo_exists():
            label.configure(text=messages[index])
            if index + 1 < len(messages):
                label.after(delay, lambda: smooth_loading_text(label, messages, index + 1, delay))
    except Exception:
        pass


# Paleta de transición azul (hover / éxito)
BLUE_FADE = ["#1976d2", "#1565c0", "#0d47a1", "#1565c0"]
GREEN_FADE = ["#16a34a", "#15803d", "#166534"]
GRAY_PULSE = ["#64748b", "#94a3b8", "#cbd5e1", "#94a3b8", "#64748b"]
