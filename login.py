"""
login.py
Professional login screen with live clock, show/hide password toggle,
and authentication against constants.
"""

import tkinter as tk
from tkinter import messagebox
import datetime
import os

import validation
from constants import (
    APP_TITLE, APP_SUBTITLE, APP_VERSION,
    DEFAULT_USERNAME, DEFAULT_PASSWORD,
    PRIMARY_BLUE, SECONDARY_BLUE, WHITE, LIGHT_GRAY, MID_GRAY,
    TEXT_DARK, TEXT_MEDIUM, ERROR_RED,
    FONT_FAMILY, LOGIN_W, LOGIN_H, ASSETS_DIR
)


class LoginScreen:
    """
    Centered login window.  Calls on_success(username) when authentication
    succeeds, or destroys root on exit.
    """

    def __init__(self, root, on_success):
        """
        Args:
            root       (tk.Tk):     Root window (hidden).
            on_success (callable):  Called with the username string on success.
        """
        self.root       = root
        self.on_success = on_success

        self.win = tk.Toplevel(root)
        self.win.title("Login — " + APP_TITLE)
        self.win.resizable(False, False)
        self.win.configure(bg=WHITE)
        self.win.protocol("WM_DELETE_WINDOW", self._on_exit)
        self._set_icon()
        self._center_window(LOGIN_W, LOGIN_H)
        self._build_ui()
        self._start_clock()
        self.win.grab_set()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        """Assemble the login window layout."""
        # ---- Header ----
        header = tk.Frame(self.win, bg=PRIMARY_BLUE, height=160)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        self._try_load_logo(header)

        tk.Label(
            header,
            text=APP_TITLE,
            font=(FONT_FAMILY, 12, "bold"),
            bg=PRIMARY_BLUE, fg=WHITE,
            wraplength=380,
            justify=tk.CENTER,
        ).pack(pady=(4, 0))

        tk.Label(
            header,
            text=APP_SUBTITLE,
            font=(FONT_FAMILY, 9),
            bg=PRIMARY_BLUE, fg="#BBDEFB",
        ).pack()

        # ---- Clock / Date strip ----
        info_strip = tk.Frame(self.win, bg=SECONDARY_BLUE, height=32)
        info_strip.pack(fill=tk.X)
        info_strip.pack_propagate(False)

        self.date_label = tk.Label(
            info_strip,
            font=(FONT_FAMILY, 9),
            bg=SECONDARY_BLUE, fg=WHITE,
        )
        self.date_label.pack(side=tk.LEFT, padx=12, pady=6)

        self.clock_label = tk.Label(
            info_strip,
            font=(FONT_FAMILY, 9, "bold"),
            bg=SECONDARY_BLUE, fg=WHITE,
        )
        self.clock_label.pack(side=tk.RIGHT, padx=12, pady=6)

        # ---- Form card ----
        card = tk.Frame(self.win, bg=WHITE, padx=40, pady=28)
        card.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            card,
            text="Sign In",
            font=(FONT_FAMILY, 16, "bold"),
            bg=WHITE, fg=TEXT_DARK,
        ).pack(anchor=tk.W, pady=(0, 18))

        # Username
        tk.Label(card, text="Username", font=(FONT_FAMILY, 10), bg=WHITE, fg=TEXT_MEDIUM).pack(anchor=tk.W)
        self.username_var = tk.StringVar()
        username_entry = tk.Entry(
            card,
            textvariable=self.username_var,
            font=(FONT_FAMILY, 11),
            relief=tk.FLAT,
            bd=0,
            highlightthickness=1,
            highlightbackground=MID_GRAY,
            highlightcolor=PRIMARY_BLUE,
        )
        username_entry.pack(fill=tk.X, ipady=8, pady=(2, 14))
        username_entry.bind("<Return>", lambda e: self.password_entry.focus())

        # Password
        tk.Label(card, text="Password", font=(FONT_FAMILY, 10), bg=WHITE, fg=TEXT_MEDIUM).pack(anchor=tk.W)

        pw_row = tk.Frame(card, bg=WHITE, highlightthickness=1,
                          highlightbackground=MID_GRAY, highlightcolor=PRIMARY_BLUE)
        pw_row.pack(fill=tk.X, pady=(2, 4))

        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(
            pw_row,
            textvariable=self.password_var,
            show="•",
            font=(FONT_FAMILY, 11),
            relief=tk.FLAT,
            bd=0,
        )
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(6, 0))
        self.password_entry.bind("<Return>", lambda e: self._attempt_login())

        self._show_pw = False
        toggle_btn = tk.Button(
            pw_row,
            text="Show",
            font=(FONT_FAMILY, 8),
            bg=WHITE, fg=TEXT_MEDIUM,
            relief=tk.FLAT, bd=0, cursor="hand2",
            command=self._toggle_password,
        )
        toggle_btn.pack(side=tk.RIGHT, padx=6)
        self._toggle_btn = toggle_btn

        # Forgot password (placeholder)
        tk.Label(
            card,
            text="Forgot password?",
            font=(FONT_FAMILY, 9),
            bg=WHITE, fg=SECONDARY_BLUE,
            cursor="hand2",
        ).pack(anchor=tk.E, pady=(0, 18))

        # Error label
        self.error_label = tk.Label(
            card,
            text="",
            font=(FONT_FAMILY, 9),
            bg=WHITE, fg=ERROR_RED,
        )
        self.error_label.pack(pady=(0, 8))

        # Login button
        login_btn = tk.Button(
            card,
            text="LOGIN",
            font=(FONT_FAMILY, 11, "bold"),
            bg=PRIMARY_BLUE, fg=WHITE,
            activebackground=SECONDARY_BLUE, activeforeground=WHITE,
            relief=tk.FLAT, bd=0, cursor="hand2",
            padx=20, pady=10,
            command=self._attempt_login,
        )
        login_btn.pack(fill=tk.X, pady=(0, 8))
        login_btn.bind("<Enter>", lambda e: login_btn.config(bg=SECONDARY_BLUE))
        login_btn.bind("<Leave>", lambda e: login_btn.config(bg=PRIMARY_BLUE))

        # Exit button
        exit_btn = tk.Button(
            card,
            text="EXIT",
            font=(FONT_FAMILY, 11),
            bg=LIGHT_GRAY, fg=TEXT_MEDIUM,
            activebackground=MID_GRAY,
            relief=tk.FLAT, bd=0, cursor="hand2",
            padx=20, pady=10,
            command=self._on_exit,
        )
        exit_btn.pack(fill=tk.X)

        # Version footer
        tk.Label(
            self.win,
            text=f"Version {APP_VERSION}",
            font=(FONT_FAMILY, 8),
            bg=WHITE, fg="#BDBDBD",
        ).pack(side=tk.BOTTOM, pady=6)

        username_entry.focus()

    def _try_load_logo(self, parent):
        """Load logo image or show a compact text badge."""
        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        try:
            from PIL import Image, ImageTk
            img = Image.open(logo_path).resize((54, 54), Image.LANCZOS)
            self._logo_img = ImageTk.PhotoImage(img)
            tk.Label(parent, image=self._logo_img, bg=PRIMARY_BLUE).pack(pady=(14, 2))
        except Exception:
            badge = tk.Frame(parent, bg=WHITE, width=50, height=50)
            badge.pack(pady=(14, 2))
            badge.pack_propagate(False)
            tk.Label(badge, text="+", font=(FONT_FAMILY, 22, "bold"),
                     bg=WHITE, fg=PRIMARY_BLUE).place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    # ------------------------------------------------------------------
    # Clock
    # ------------------------------------------------------------------

    def _start_clock(self):
        """Start the live clock ticker."""
        def tick():
            now = datetime.datetime.now()
            self.clock_label.config(text=now.strftime("%H:%M:%S"))
            self.date_label.config(text=now.strftime("%A, %d %B %Y"))
            self.clock_label.after(1000, tick)
        tick()

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _toggle_password(self):
        """Toggle password field between masked and visible."""
        self._show_pw = not self._show_pw
        self.password_entry.config(show="" if self._show_pw else "•")
        self._toggle_btn.config(text="Hide" if self._show_pw else "Show")

    def _attempt_login(self):
        """Validate credentials and either open dashboard or show error."""
        import logging  # <--- MOVED HERE (Now both IF and ELSE can see it!)
        
        username = self.username_var.get()
        password = self.password_var.get()

        is_valid, error = validation.validate_login(username, password)
        if not is_valid:
            self._show_error(error)
            return

        if username == DEFAULT_USERNAME and password == DEFAULT_PASSWORD:
            logging.info("User '%s' authenticated successfully.", username)
            self.win.destroy()
            self.on_success(username)
        else:
            self._show_error("Invalid username or password.")
            logging.warning("Failed login attempt for username '%s'.", username)
            
    def _show_error(self, message):
        """Display an inline error message on the form."""
        self.error_label.config(text=message)
        self.win.after(4000, lambda: self.error_label.config(text=""))

    def _on_exit(self):
        """Confirm and close the entire application."""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.destroy()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _center_window(self, width, height):
        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()
        x  = (sw - width)  // 2
        y  = (sh - height) // 2
        self.win.geometry(f"{width}x{height}+{x}+{y}")

    def _set_icon(self):
        icon_path = os.path.join(ASSETS_DIR, "hospital.ico")
        if os.path.isfile(icon_path):
            try:
                self.win.iconbitmap(icon_path)
            except Exception:
                pass
