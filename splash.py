"""
splash.py
Animated splash screen displayed at application startup.
"""

import tkinter as tk
from tkinter import ttk
import os

from constants import (
    APP_TITLE, APP_SUBTITLE, APP_VERSION, COURSE_TITLE, SDG_NOTE,
    PRIMARY_BLUE, SECONDARY_BLUE, WHITE, ACCENT_BLUE, FONT_FAMILY,
    SPLASH_W, SPLASH_H, ASSETS_DIR
)


class SplashScreen:
    """
    Animated splash screen that displays for ~3 seconds then invokes
    the on_complete callback.
    """

    def __init__(self, root, on_complete):
        """
        Args:
            root        (tk.Tk):    The root Tk window.
            on_complete (callable): Zero-arg callback called when splash ends.
        """
        self.root        = root
        self.on_complete = on_complete
        self._progress   = 0

        self.win = tk.Toplevel(root)
        self.win.overrideredirect(True)
        self._center_window(SPLASH_W, SPLASH_H)
        self.win.configure(bg=PRIMARY_BLUE)
        self.win.lift()
        self.win.focus_force()

        self._build_ui()
        self._animate()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_ui(self):
        """Build all widgets on the splash window."""
        outer = tk.Frame(self.win, bg=PRIMARY_BLUE)
        outer.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        inner = tk.Frame(outer, bg=WHITE, relief=tk.FLAT)
        inner.pack(fill=tk.BOTH, expand=True)

        # Top accent strip
        accent = tk.Frame(inner, bg=SECONDARY_BLUE, height=6)
        accent.pack(fill=tk.X)

        # Logo area
        logo_frame = tk.Frame(inner, bg=WHITE, pady=20)
        logo_frame.pack(fill=tk.X)

        self._try_load_logo(logo_frame)

        # Title
        tk.Label(
            inner,
            text=APP_TITLE,
            font=(FONT_FAMILY, 14, "bold"),
            bg=WHITE, fg=PRIMARY_BLUE,
            wraplength=460,
            justify=tk.CENTER,
        ).pack(padx=20, pady=(0, 4))

        # Subtitle
        tk.Label(
            inner,
            text=APP_SUBTITLE,
            font=(FONT_FAMILY, 10),
            bg=WHITE, fg=SECONDARY_BLUE,
        ).pack()

        # Course
        tk.Label(
            inner,
            text=COURSE_TITLE,
            font=(FONT_FAMILY, 9),
            bg=WHITE, fg="#616161",
        ).pack(pady=(6, 0))

        # SDG note
        tk.Label(
            inner,
            text=SDG_NOTE,
            font=(FONT_FAMILY, 9, "italic"),
            bg=WHITE, fg="#388E3C",
        ).pack(pady=(2, 16))

        # Progress bar
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Splash.Horizontal.TProgressbar",
            troughcolor="#E3F2FD",
            background=ACCENT_BLUE,
            thickness=8,
        )
        self.progress_bar = ttk.Progressbar(
            inner,
            style="Splash.Horizontal.TProgressbar",
            orient=tk.HORIZONTAL,
            length=380,
            mode="determinate",
            maximum=100,
        )
        self.progress_bar.pack(pady=(0, 8))

        # Status label
        self.status_label = tk.Label(
            inner,
            text="Initialising...",
            font=(FONT_FAMILY, 9),
            bg=WHITE, fg="#9E9E9E",
        )
        self.status_label.pack()

        # Version footer
        footer = tk.Frame(inner, bg="#F5F5F5", height=30)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Label(
            footer,
            text=f"Version {APP_VERSION}",
            font=(FONT_FAMILY, 8),
            bg="#F5F5F5", fg="#9E9E9E",
        ).pack(side=tk.RIGHT, padx=12, pady=6)

    def _try_load_logo(self, parent):
        """Attempt to load the clinic logo; fall back to a text badge."""
        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        try:
            from PIL import Image, ImageTk
            img = Image.open(logo_path).resize((80, 80), Image.LANCZOS)
            self._logo_img = ImageTk.PhotoImage(img)
            tk.Label(parent, image=self._logo_img, bg=WHITE).pack()
        except Exception:
            # Fallback text badge when logo file or Pillow is absent
            badge = tk.Frame(parent, bg=PRIMARY_BLUE, width=80, height=80)
            badge.pack()
            badge.pack_propagate(False)
            tk.Label(
                badge,
                text="+",
                font=(FONT_FAMILY, 36, "bold"),
                bg=PRIMARY_BLUE, fg=WHITE,
            ).place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    # ------------------------------------------------------------------
    # Animation
    # ------------------------------------------------------------------

    _STEPS = [
        (10,  "Loading database..."),
        (25,  "Preparing interface..."),
        (45,  "Loading modules..."),
        (65,  "Connecting to database..."),
        (80,  "Applying settings..."),
        (95,  "Almost ready..."),
        (100, "Welcome!"),
    ]

    def _animate(self):
        """Drive the progress bar through predefined steps."""
        self._step_index = 0
        self._advance()

    def _advance(self):
        """Move to the next animation step."""
        if self._step_index >= len(self._STEPS):
            self.win.after(400, self._finish)
            return

        target_pct, message = self._STEPS[self._step_index]
        self._step_index += 1
        self._fill_to(target_pct, message)

    def _fill_to(self, target, message, current=None):
        """Smoothly increment the progress bar to target percent."""
        if current is None:
            current = self._progress

        if current < target:
            current += 1
            self.progress_bar["value"] = current
            self._progress = current
            self.win.after(18, lambda: self._fill_to(target, message, current))
        else:
            self.status_label.config(text=message)
            self.win.after(220, self._advance)

    def _finish(self):
        """Destroy the splash window and call the completion callback."""
        self.win.destroy()
        self.on_complete()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _center_window(self, width, height):
        """Position the splash window in the centre of the screen."""
        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()
        x  = (sw - width)  // 2
        y  = (sh - height) // 2
        self.win.geometry(f"{width}x{height}+{x}+{y}")
