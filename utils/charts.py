# ============================================================
# Romex QC Desktop — Gráficos con Matplotlib
# ============================================================

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from config import COLORS, MICRO_LABELS, FISICO_LABELS, MONTH_NAMES, MONTH_NAMES_SHORT


def _style_ax(ax, title=""):
    ax.set_facecolor("#f8fafc")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#cbd5e1")
    ax.spines["bottom"].set_color("#cbd5e1")
    ax.tick_params(colors="#475569", labelsize=8)
    if title:
        ax.set_title(title, fontsize=11, fontweight="600", color="#1e293b", pad=8)


def create_micro_bar_chart(parent, data, baseline=None, mes_label=""):
    fig = Figure(figsize=(8, 3.6), dpi=100)
    ax = fig.add_subplot(111)

    keys = list(MICRO_LABELS.keys())
    labels = [MICRO_LABELS[k] for k in keys]
    x = range(len(keys))
    width = 0.38

    base_vals = [baseline.get(k, 0) if baseline else 0 for k in keys]
    month_vals = [data.get(k, 0) or 0 for k in keys]
    colors = [COLORS.get(k, "#1565c0") for k in keys]

    bars1 = ax.bar([i - width / 2 for i in x], base_vals, width,
                   label="Punto de partida (siembra)", color=COLORS["baseline"], edgecolor="#64748b", linewidth=0.6)
    bars2 = ax.bar([i + width / 2 for i in x], month_vals, width,
                   label=f"Resultado {mes_label}", color=colors, edgecolor="#0f172a", linewidth=0.4)

    for bar in bars1:
        h = bar.get_height()
        ax.annotate(f"{int(h)}", xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=7, color="#64748b")
    for bar in bars2:
        h = bar.get_height()
        ax.annotate(f"{int(h)}", xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=7, fontweight="600", color="#1e293b")

    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("ufc/gr", fontsize=9)
    ax.legend(fontsize=8, loc="upper right", framealpha=0.9)
    _style_ax(ax, f"Microbiología · Siembra vs {mes_label}" if mes_label else "Microbiología")
    fig.tight_layout(pad=1.2)

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    widget = canvas.get_tk_widget()
    return widget, canvas, fig


def create_fisico_bar_chart(parent, data, fields, baseline=None, mes_label=""):
    fig = Figure(figsize=(8, 3.6), dpi=100)
    ax = fig.add_subplot(111)

    labels = [FISICO_LABELS.get(k, k) for k in fields]
    x = range(len(fields))
    width = 0.38

    base_vals = []
    month_vals = []
    for k in fields:
        bv = baseline.get(k) if baseline else None
        base_vals.append(float(bv) if bv is not None else 0)
        mv = data.get(k)
        month_vals.append(float(mv) if mv is not None else 0)

    colors = [COLORS.get(k, "#1565c0") for k in fields]

    bars1 = ax.bar([i - width / 2 for i in x], base_vals, width,
                   label="Punto de partida", color=COLORS["baseline"], edgecolor="#64748b", linewidth=0.6)
    bars2 = ax.bar([i + width / 2 for i in x], month_vals, width,
                   label=f"Resultado {mes_label}", color=colors, edgecolor="#0f172a", linewidth=0.4)

    for bar in bars1:
        h = bar.get_height()
        ax.annotate(f"{h:.2f}", xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=7, color="#64748b")
    for bar in bars2:
        h = bar.get_height()
        ax.annotate(f"{h:.2f}", xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=7, fontweight="600", color="#1e293b")

    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=8)
    ax.legend(fontsize=8, loc="upper right", framealpha=0.9)
    _style_ax(ax, f"Físicoquímico · Siembra vs {mes_label}" if mes_label else "Físicoquímico")
    fig.tight_layout(pad=1.2)

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    widget = canvas.get_tk_widget()
    return widget, canvas, fig


def create_trend_chart(parent, rows, key, label, color, baseline_value=None, y_label=""):
    fig = Figure(figsize=(8, 2.8), dpi=100)
    ax = fig.add_subplot(111)

    if not rows:
        ax.text(0.5, 0.5, "Sin datos de tendencia", ha="center", va="center",
                transform=ax.transAxes, color="#94a3b8", fontsize=11)
        _style_ax(ax, f"Tendencia · {label}")
        fig.tight_layout(pad=1.0)
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        return canvas.get_tk_widget(), canvas, fig

    months = [r["Mes"] for r in rows]
    values = []
    for r in rows:
        v = r.get(key)
        try:
            values.append(float(v) if v is not None else None)
        except (TypeError, ValueError):
            values.append(None)

    x_labels = [MONTH_NAMES_SHORT.get(m, str(m)) for m in months]
    x = range(len(months))

    if baseline_value is not None:
        try:
            bv = float(baseline_value)
            ax.axhline(y=bv, color="#94a3b8", linestyle="--", linewidth=1.5,
                       label=f"Punto partida ({bv})", zorder=1)
        except (TypeError, ValueError):
            pass

    ax.plot(list(x), values, color=color, linewidth=2.4, marker="o",
            markersize=6, markerfacecolor=color, markeredgecolor="white",
            markeredgewidth=1.5, label=label, zorder=2)
    ax.fill_between(list(x), values, alpha=0.12, color=color)

    for i, v in enumerate(values):
        if v is not None:
            ax.annotate(f"{v:.1f}" if isinstance(v, float) and v != int(v) else f"{int(v)}",
                        xy=(i, v), xytext=(0, 8), textcoords="offset points",
                        ha="center", fontsize=7, color="#334155")

    ax.set_xticks(list(x))
    ax.set_xticklabels(x_labels, fontsize=8)
    if y_label:
        ax.set_ylabel(y_label, fontsize=9)
    ax.legend(fontsize=8, loc="best", framealpha=0.9)
    _style_ax(ax, f"Tendencia · {label}")
    fig.tight_layout(pad=1.0)

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    widget = canvas.get_tk_widget()
    return widget, canvas, fig


def destroy_chart(canvas, fig):
    try:
        if canvas:
            canvas.get_tk_widget().destroy()
        if fig:
            plt.close(fig)
    except Exception:
        pass
