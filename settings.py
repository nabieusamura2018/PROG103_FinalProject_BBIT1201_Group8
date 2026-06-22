"""
settings.py
Application settings panel — theme switching, font size, about info.
"""

import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
import logging

from constants import (
    APP_TITLE, APP_VERSION, COURSE_TITLE, SDG_NOTE, DEVELOPER,
    PRIMARY_BLUE, SECONDARY_BLUE, WHITE, LIGHT_GRAY, MID_GRAY,
    TEXT_DARK, TEXT_MEDIUM, FONT_FAMILY,
    DARK_BG, DARK_CARD, DARK_SIDEBAR, DARK_TEXT, DARK_TEXT_MED,
    SETTINGS_FILE
)

# Default settings
_DEFAULTS = {
    "theme":     "light",
    "font_size": "medium",
}

# Font size map
_FONT_SIZES = {
    "small":  {"normal": 9,  "medium": 10, "large": 12, "title": 15},
    "medium": {"normal": 11, "medium": 12, "large": 14, "title": 18},
    "large":  {"normal": 13, "medium": 14, "large": 16, "title": 21},
}


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

def load_settings():
    """Load settings from JSON file, falling back to defaults."""
    if not os.path.isfile(SETTINGS_FILE):
        return dict(_DEFAULTS)
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Merge with defaults to handle missing keys
        merged = dict(_DEFAULTS)
        merged.update(data)
        return merged
    except Exception as exc:
        logging.warning("Could not read settings file: %s", exc)
        return dict(_DEFAULTS)


def save_settings(settings):
    """Persist the settings dict to JSON."""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception as exc:
        logging.error("Could not save settings: %s", exc)


# ---------------------------------------------------------------------------
# Theme Application
# ---------------------------------------------------------------------------

def apply_theme(theme_name, style):
    """
    Apply the chosen theme to all ttk widget styles.

    Args:
        theme_name (str):       'light' or 'dark'
        style      (ttk.Style): Application-wide style object.
    """
    style.theme_use("clam")
    if theme_name == "dark":
        _apply_dark(style)
    else:
        _apply_light(style)


def _apply_light(style):
    """Configure all ttk styles for the light theme."""
    bg  = WHITE
    fg  = TEXT_DARK
    sel = PRIMARY_BLUE

    style.configure("TFrame",       background=LIGHT_GRAY)
    style.configure("Card.TFrame",  background=WHITE)
    style.configure("TLabel",       background=LIGHT_GRAY, foreground=fg,
                    font=(FONT_FAMILY, 11))
    style.configure("Card.TLabel",  background=WHITE,      foreground=fg)
    style.configure("TEntry",       fieldbackground=WHITE, foreground=fg)
    style.configure("TCombobox",    fieldbackground=WHITE, foreground=fg)
    style.configure("TButton",      background=PRIMARY_BLUE, foreground=WHITE,
                    font=(FONT_FAMILY, 10, "bold"), relief="flat")
    style.map("TButton",
              background=[("active", SECONDARY_BLUE)],
              foreground=[("active", WHITE)])
    style.configure("Treeview",
                    background=WHITE, fieldbackground=WHITE, foreground=fg,
                    rowheight=26, font=(FONT_FAMILY, 10))
    style.configure("Treeview.Heading",
                    background=PRIMARY_BLUE, foreground=WHITE,
                    font=(FONT_FAMILY, 10, "bold"), relief="flat")
    style.map("Treeview", background=[("selected", "#BBDEFB")])


def _apply_dark(style):
    """Configure all ttk styles for the dark theme."""
    bg  = DARK_BG
    fg  = DARK_TEXT
    sel = "#1A3A5C"

    style.configure("TFrame",       background=DARK_BG)
    style.configure("Card.TFrame",  background=DARK_CARD)
    style.configure("TLabel",       background=DARK_BG,   foreground=fg,
                    font=(FONT_FAMILY, 11))
    style.configure("Card.TLabel",  background=DARK_CARD, foreground=fg)
    style.configure("TEntry",       fieldbackground="#3A3A3A", foreground=fg)
    style.configure("TCombobox",    fieldbackground="#3A3A3A", foreground=fg)
    style.configure("TButton",      background="#1A3A5C", foreground=DARK_TEXT,
                    font=(FONT_FAMILY, 10, "bold"), relief="flat")
    style.map("TButton",
              background=[("active", "#1E4A70")],
              foreground=[("active", DARK_TEXT)])
    style.configure("Treeview",
                    background=DARK_CARD, fieldbackground=DARK_CARD,
                    foreground=fg, rowheight=26, font=(FONT_FAMILY, 10))
    style.configure("Treeview.Heading",
                    background=DARK_SIDEBAR, foreground=fg,
                    font=(FONT_FAMILY, 10, "bold"), relief="flat")
    style.map("Treeview", background=[("selected", sel)])


# ---------------------------------------------------------------------------
# Settings Panel UI
# ---------------------------------------------------------------------------

class SettingsPanel:
    """
    Settings panel rendered into a parent frame.
    Calls apply_callback(theme, font_size) when settings are saved.
    """

    def __init__(self, parent_frame, current_settings, apply_callback):
        """
        Args:
            parent_frame     (tk.Frame):  Container to render into.
            current_settings (dict):      Current {theme, font_size} values.
            apply_callback   (callable):  Called with (theme_str, font_size_str).
        """
        self.parent   = parent_frame
        self.settings = current_settings
        self.apply_cb = apply_callback
        self._build()

    def _build(self):
        for w in self.parent.winfo_children():
            w.destroy()

        outer = tk.Frame(self.parent, bg=LIGHT_GRAY)
        outer.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)

        # Section title
        tk.Label(outer, text="Application Settings",
                 font=(FONT_FAMILY, 15, "bold"),
                 bg=LIGHT_GRAY, fg=TEXT_DARK).pack(anchor=tk.W, pady=(0, 16))

        # ---- Theme card ----
        card1 = tk.LabelFrame(outer, text=" Theme ",
                               font=(FONT_FAMILY, 10, "bold"),
                               bg=WHITE, fg=PRIMARY_BLUE,
                               padx=16, pady=12, relief=tk.GROOVE, bd=1)
        card1.pack(fill=tk.X, pady=(0, 12))

        self._theme_var = tk.StringVar(value=self.settings.get("theme", "light"))
        for value, label in (("light", "Light Mode"), ("dark", "Dark Mode")):
            tk.Radiobutton(
                card1, text=label,
                variable=self._theme_var, value=value,
                font=(FONT_FAMILY, 10),
                bg=WHITE, fg=TEXT_DARK,
                activebackground=WHITE,
                selectcolor="#E3F2FD",
            ).pack(anchor=tk.W, pady=2)

        # ---- Font size card ----
        card2 = tk.LabelFrame(outer, text=" Font Size ",
                               font=(FONT_FAMILY, 10, "bold"),
                               bg=WHITE, fg=PRIMARY_BLUE,
                               padx=16, pady=12, relief=tk.GROOVE, bd=1)
        card2.pack(fill=tk.X, pady=(0, 12))

        self._font_var = tk.StringVar(value=self.settings.get("font_size", "medium"))
        for value, label in (("small", "Small"), ("medium", "Medium (Default)"), ("large", "Large")):
            tk.Radiobutton(
                card2, text=label,
                variable=self._font_var, value=value,
                font=(FONT_FAMILY, 10),
                bg=WHITE, fg=TEXT_DARK,
                activebackground=WHITE,
                selectcolor="#E3F2FD",
            ).pack(anchor=tk.W, pady=2)

        # Apply button
        tk.Button(
            outer, text="Apply Settings",
            font=(FONT_FAMILY, 11, "bold"),
            bg=PRIMARY_BLUE, fg=WHITE,
            activebackground=SECONDARY_BLUE, activeforeground=WHITE,
            relief=tk.FLAT, cursor="hand2",
            padx=20, pady=8,
            command=self._apply,
        ).pack(anchor=tk.W, pady=(4, 20))

        # ---- About card ----
        about = tk.LabelFrame(outer, text=" About System ",
                               font=(FONT_FAMILY, 10, "bold"),
                               bg=WHITE, fg=PRIMARY_BLUE,
                               padx=16, pady=12, relief=tk.GROOVE, bd=1)
        about.pack(fill=tk.X)

        info_lines = [
            ("Application",  APP_TITLE),
            ("Version",      APP_VERSION),
            ("Course",       COURSE_TITLE),
            ("SDG Focus",    SDG_NOTE),
            ("Developed by", DEVELOPER),
        ]
        for label, value in info_lines:
            row = tk.Frame(about, bg=WHITE)
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=f"{label}:", font=(FONT_FAMILY, 9, "bold"),
                     bg=WHITE, fg=TEXT_MEDIUM, width=14, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(row, text=value, font=(FONT_FAMILY, 9),
                     bg=WHITE, fg=TEXT_DARK, wraplength=380, justify=tk.LEFT).pack(side=tk.LEFT, fill=tk.X)

    def _apply(self):
        """Read widget values and call the apply callback."""
        theme     = self._theme_var.get()
        font_size = self._font_var.get()
        self.settings["theme"]     = theme
        self.settings["font_size"] = font_size
        save_settings(self.settings)
        self.apply_cb(theme, font_size)
        messagebox.showinfo("Settings", "Settings applied successfully.")
