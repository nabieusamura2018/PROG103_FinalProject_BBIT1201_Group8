"""
charts.py
Data visualisation module — embeds Matplotlib charts into Tkinter frames.
"""

import tkinter as tk
from tkinter import messagebox
import logging

import database
from constants import (
    PRIMARY_BLUE, SECONDARY_BLUE, ACCENT_BLUE, WHITE, LIGHT_GRAY,
    FONT_FAMILY
)

try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _check_matplotlib(parent):
    """Show a message and return False if matplotlib is not installed."""
    if not MATPLOTLIB_AVAILABLE:
        messagebox.showerror(
            "Missing Library",
            "matplotlib is not installed.\n\nRun:  pip install matplotlib",
            parent=parent,
        )
        return False
    return True


def _clear_frame(frame):
    """Destroy all child widgets of a frame."""
    for widget in frame.winfo_children():
        widget.destroy()


def _embed_figure(fig, parent_frame):
    """Embed a Matplotlib figure into a Tkinter frame."""
    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    return canvas


# ---------------------------------------------------------------------------
# Chart: Gender Distribution (Pie)
# ---------------------------------------------------------------------------

def render_gender_pie_chart(parent_frame, conn):
    """
    Render a pie chart of patient gender distribution into parent_frame.

    Args:
        parent_frame (tk.Frame):    Target container widget.
        conn         (Connection):  Active database connection.
    """
    if not _check_matplotlib(parent_frame):
        return

    _clear_frame(parent_frame)

    data = database.get_gender_distribution(conn)
    if not data:
        _show_no_data(parent_frame, "No patient data available for gender chart.")
        return

    labels = [r[0] for r in data]
    sizes  = [r[1] for r in data]
    colors = [PRIMARY_BLUE, "#E91E63", "#4CAF50", "#FF9800"][:len(labels)]

    fig, ax = plt.subplots(figsize=(5, 4), facecolor=WHITE)
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct="%1.1f%%",
        startangle=90,
        wedgeprops={"edgecolor": WHITE, "linewidth": 2},
    )
    for t in texts:
        t.set_fontsize(10)
    for at in autotexts:
        at.set_fontsize(9)
        at.set_color(WHITE)
        at.set_fontweight("bold")

    ax.set_title("Patient Gender Distribution", fontsize=13, fontweight="bold",
                 color="#212121", pad=14)
    fig.tight_layout()

    _embed_figure(fig, parent_frame)
    logging.info("Gender pie chart rendered.")


# ---------------------------------------------------------------------------
# Chart: Common Illnesses (Horizontal Bar)
# ---------------------------------------------------------------------------

def render_illness_bar_chart(parent_frame, conn):
    """
    Render a horizontal bar chart of the top 10 illnesses.

    Args:
        parent_frame (tk.Frame):    Target container widget.
        conn         (Connection):  Active database connection.
    """
    if not _check_matplotlib(parent_frame):
        return

    _clear_frame(parent_frame)

    data = database.get_illness_distribution(conn, limit=10)
    if not data:
        _show_no_data(parent_frame, "No patient data available for illness chart.")
        return

    illnesses = [r[0] for r in data]
    counts    = [r[1] for r in data]

    fig, ax = plt.subplots(figsize=(6, 4), facecolor=WHITE)
    bars = ax.barh(illnesses, counts, color=ACCENT_BLUE, edgecolor=WHITE, height=0.6)

    # Gradient-style shading: darker = more frequent
    max_c = max(counts) if counts else 1
    for bar, count in zip(bars, counts):
        intensity = 0.4 + 0.6 * (count / max_c)
        bar.set_facecolor((21/255 * intensity, 101/255, 192/255 * intensity))

    ax.set_xlabel("Number of Patients", fontsize=9, color="#616161")
    ax.set_title("Top 10 Common Illnesses", fontsize=13, fontweight="bold",
                 color="#212121", pad=12)
    ax.invert_yaxis()
    ax.tick_params(axis="y", labelsize=9)
    ax.set_facecolor("#F5F9FF")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()

    _embed_figure(fig, parent_frame)
    logging.info("Illness bar chart rendered.")


# ---------------------------------------------------------------------------
# Chart: Daily Registrations (Line)
# ---------------------------------------------------------------------------

def render_daily_line_chart(parent_frame, conn):
    """
    Render a line chart of daily patient registrations for the past 30 days.

    Args:
        parent_frame (tk.Frame):    Target container widget.
        conn         (Connection):  Active database connection.
    """
    if not _check_matplotlib(parent_frame):
        return

    _clear_frame(parent_frame)

    data = database.get_daily_registrations(conn, days=30)
    if not data:
        _show_no_data(parent_frame, "No registration history available for line chart.")
        return

    dates  = [r[0] for r in data]
    counts = [r[1] for r in data]

    short_dates = [d[5:] for d in dates]  # "MM-DD" portion

    fig, ax = plt.subplots(figsize=(6, 4), facecolor=WHITE)
    ax.plot(short_dates, counts, color=PRIMARY_BLUE, linewidth=2.5,
            marker="o", markersize=5, markerfacecolor=WHITE,
            markeredgecolor=PRIMARY_BLUE, markeredgewidth=2)
    ax.fill_between(range(len(counts)), counts,
                    alpha=0.12, color=PRIMARY_BLUE)

    ax.set_xlabel("Date", fontsize=9, color="#616161")
    ax.set_ylabel("Patients Registered", fontsize=9, color="#616161")
    ax.set_title("Daily Patient Registrations (Last 30 Days)",
                 fontsize=13, fontweight="bold", color="#212121", pad=12)
    ax.set_xticks(range(len(short_dates)))
    ax.set_xticklabels(short_dates, rotation=45, ha="right", fontsize=7)
    ax.set_facecolor("#F5F9FF")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()

    _embed_figure(fig, parent_frame)
    logging.info("Daily line chart rendered.")


# ---------------------------------------------------------------------------
# No-data placeholder
# ---------------------------------------------------------------------------

def _show_no_data(parent_frame, message):
    """Display a placeholder label when there is no data to chart."""
    tk.Label(
        parent_frame,
        text=message,
        font=(FONT_FAMILY, 11),
        bg=WHITE, fg="#9E9E9E",
    ).place(relx=0.5, rely=0.5, anchor=tk.CENTER)
