"""
gui.py
Main Dashboard Application — sidebar navigation, content area,
patient registration form, records treeview, and all sub-views.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import os
import logging

import database
import functions
import reports
import charts
import settings as settings_module
from constants import (
    APP_TITLE, APP_SUBTITLE, APP_VERSION,
    PRIMARY_BLUE, SECONDARY_BLUE, ACCENT_BLUE, LIGHT_BLUE_BG,
    WHITE, LIGHT_GRAY, MID_GRAY, CARD_BG,
    SUCCESS_GREEN, SUCCESS_LIGHT, WARNING_AMBER, ERROR_RED, ERROR_LIGHT,
    TEXT_DARK, TEXT_MEDIUM, TEXT_LIGHT,
    SIDEBAR_BG, SIDEBAR_HOVER, SIDEBAR_ACTIVE,
    HEADER_BG, HEADER_FG, STATUS_BG, STATUS_FG,
    FONT_FAMILY, FONT_NORMAL, FONT_BOLD, FONT_MEDIUM, FONT_MEDIUM_BOLD,
    FONT_LARGE, FONT_LARGE_BOLD, FONT_TITLE, FONT_SMALL,
    GENDER_OPTIONS, BLOOD_GROUPS, ILLNESS_SUGGESTIONS,
    TREE_COLUMNS, TREE_HEADINGS, TREE_WIDTHS, TREE_ANCHORS,
    STATUS_READY, STATUS_CONNECTED,
    MAIN_W, MAIN_H, SIDEBAR_W,
    ASSETS_DIR,
)


class DashboardApp:
    """
    Main application window.  Contains the header, sidebar, content area,
    and status bar.  Renders different sub-views in the content area based
    on the active navigation item.
    """

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def __init__(self, root, conn, username):
        """
        Args:
            root     (tk.Tk):      Root Tk window.
            conn     (Connection): Active database connection.
            username (str):        Authenticated user's name.
        """
        self.root     = root
        self.conn     = conn
        self.username = username

        self._current_patient_id = None
        self._app_settings       = settings_module.load_settings()

        self.root.deiconify()
        self.root.title(APP_TITLE)
        self._set_icon()
        self._center_window(MAIN_W, MAIN_H)
        self.root.resizable(True, True)
        self.root.minsize(960, 600)

        self._style = ttk.Style()
        settings_module.apply_theme(self._app_settings.get("theme", "light"), self._style)

        self._build_menu()
        self._build_header()
        self._build_main_area()
        self._build_status_bar()
        self._start_clock()

        self.show_dashboard()
        self._set_status(STATUS_CONNECTED)

    # ------------------------------------------------------------------
    # Window helpers
    # ------------------------------------------------------------------

    def _center_window(self, w, h):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x  = (sw - w) // 2
        y  = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _set_icon(self):
        path = os.path.join(ASSETS_DIR, "hospital.ico")
        if os.path.isfile(path):
            try:
                self.root.iconbitmap(path)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Menu Bar
    # ------------------------------------------------------------------

    def _build_menu(self):
        """Build the top application menu bar."""
        menubar = tk.Menu(self.root)

        # File
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Registration", command=self.show_register)
        file_menu.add_command(label="Export All Records (CSV)",
                              command=lambda: reports.export_all_to_csv(self.conn, self._set_status))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_logout)
        menubar.add_cascade(label="File", menu=file_menu)

        # Patients
        pat_menu = tk.Menu(menubar, tearoff=0)
        pat_menu.add_command(label="Register Patient", command=self.show_register)
        pat_menu.add_command(label="Patient Records",  command=self.show_records)
        menubar.add_cascade(label="Patients", menu=pat_menu)

        # Reports
        rep_menu = tk.Menu(menubar, tearoff=0)
        rep_menu.add_command(label="Export All Records",
                             command=lambda: reports.export_all_to_csv(self.conn, self._set_status))
        rep_menu.add_command(label="Daily Report",
                             command=lambda: reports.export_daily_report(self.conn, self._set_status))
        rep_menu.add_command(label="Print Preview",
                             command=lambda: reports.show_print_preview(self.conn, self.root))
        menubar.add_cascade(label="Reports", menu=rep_menu)

        # Statistics
        stat_menu = tk.Menu(menubar, tearoff=0)
        stat_menu.add_command(label="View Statistics", command=self.show_statistics)
        stat_menu.add_command(label="View Charts",     command=self.show_charts)
        menubar.add_cascade(label="Statistics", menu=stat_menu)

        # Settings
        set_menu = tk.Menu(menubar, tearoff=0)
        set_menu.add_command(label="Preferences", command=self.show_settings)
        set_menu.add_separator()
        set_menu.add_command(label="Backup Database",  command=self._backup)
        set_menu.add_command(label="Restore Database", command=self._restore)
        menubar.add_cascade(label="Settings", menu=set_menu)

        # Help
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About",        command=self._show_about)
        help_menu.add_command(label="User Guide",   command=self._show_user_guide)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------

    def _build_header(self):
        """Build the top header bar."""
        self._header = tk.Frame(self.root, bg=HEADER_BG, height=64)
        self._header.pack(fill=tk.X)
        self._header.pack_propagate(False)

        # Logo
        self._try_load_logo(self._header)

        # Title block
        title_block = tk.Frame(self._header, bg=HEADER_BG)
        title_block.pack(side=tk.LEFT, padx=(8, 0), pady=4)
        tk.Label(title_block, text=APP_TITLE, font=(FONT_FAMILY, 13, "bold"),
                 bg=HEADER_BG, fg=WHITE).pack(anchor=tk.W)
        tk.Label(title_block, text=APP_SUBTITLE, font=(FONT_FAMILY, 9),
                 bg=HEADER_BG, fg="#BBDEFB").pack(anchor=tk.W)

        # Right — user + clock
        right = tk.Frame(self._header, bg=HEADER_BG)
        right.pack(side=tk.RIGHT, padx=16)

        self._clock_lbl = tk.Label(right, font=(FONT_FAMILY, 14, "bold"),
                                    bg=HEADER_BG, fg=WHITE)
        self._clock_lbl.pack(anchor=tk.E)

        self._date_lbl = tk.Label(right, font=(FONT_FAMILY, 9),
                                   bg=HEADER_BG, fg="#BBDEFB")
        self._date_lbl.pack(anchor=tk.E)

        tk.Label(right, text=f"User: {self.username}",
                 font=(FONT_FAMILY, 9, "bold"),
                 bg=HEADER_BG, fg="#E3F2FD").pack(anchor=tk.E)

    def _try_load_logo(self, parent):
        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        try:
            from PIL import Image, ImageTk
            img = Image.open(logo_path).resize((46, 46), Image.LANCZOS)
            self._header_logo = ImageTk.PhotoImage(img)
            tk.Label(parent, image=self._header_logo,
                     bg=HEADER_BG).pack(side=tk.LEFT, padx=(14, 0), pady=8)
        except Exception:
            badge = tk.Frame(parent, bg=WHITE, width=44, height=44)
            badge.pack(side=tk.LEFT, padx=(14, 0), pady=10)
            badge.pack_propagate(False)
            tk.Label(badge, text="+", font=(FONT_FAMILY, 18, "bold"),
                     bg=WHITE, fg=PRIMARY_BLUE).place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def _start_clock(self):
        def tick():
            now = datetime.datetime.now()
            self._clock_lbl.config(text=now.strftime("%H:%M:%S"))
            self._date_lbl.config(text=now.strftime("%A, %d %B %Y"))
            self.root.after(1000, tick)
        tick()

    # ------------------------------------------------------------------
    # Main Area: Sidebar + Content
    # ------------------------------------------------------------------

    def _build_main_area(self):
        """Build the sidebar and content area side by side."""
        self._main_frame = tk.Frame(self.root, bg=LIGHT_GRAY)
        self._main_frame.pack(fill=tk.BOTH, expand=True)

        self._build_sidebar(self._main_frame)

        self._content = tk.Frame(self._main_frame, bg=LIGHT_GRAY)
        self._content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # ------------------------------------------------------------------
    # Sidebar
    # ------------------------------------------------------------------

    _NAV_ITEMS = [
        ("Dashboard",        "show_dashboard"),
        ("Register Patient", "show_register"),
        ("Patient Records",  "show_records"),
        ("Reports",          "show_reports"),
        ("Statistics",       "show_statistics"),
        ("Charts",           "show_charts"),
        ("Settings",         "show_settings"),
        ("Backup / Restore", "show_backup"),
    ]

    def _build_sidebar(self, parent):
        """Build the left navigation sidebar."""
        self._sidebar = tk.Frame(parent, bg=SIDEBAR_BG, width=SIDEBAR_W)
        self._sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self._sidebar.pack_propagate(False)

        # Clinic badge at top
        badge = tk.Frame(self._sidebar, bg="#0D47A1", height=50)
        badge.pack(fill=tk.X)
        badge.pack_propagate(False)
        tk.Label(badge, text="CLINIC  SYSTEM",
                 font=(FONT_FAMILY, 10, "bold"),
                 bg="#0D47A1", fg=WHITE).place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self._nav_buttons = {}
        for label, method in self._NAV_ITEMS:
            btn = tk.Button(
                self._sidebar,
                text=f"  {label}",
                font=(FONT_FAMILY, 10),
                bg=SIDEBAR_BG, fg=WHITE,
                activebackground=SIDEBAR_HOVER, activeforeground=WHITE,
                relief=tk.FLAT, bd=0, cursor="hand2",
                anchor=tk.W, padx=10, pady=9,
                command=lambda m=method: getattr(self, m)(),
            )
            btn.pack(fill=tk.X)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=SIDEBAR_HOVER))
            btn.bind("<Leave>", lambda e, b=btn: self._restore_btn_color(b))
            self._nav_buttons[label] = btn

        # Spacer
        tk.Frame(self._sidebar, bg=SIDEBAR_BG).pack(fill=tk.BOTH, expand=True)

        # Logout
        tk.Button(
            self._sidebar,
            text="  Logout",
            font=(FONT_FAMILY, 10, "bold"),
            bg="#C62828", fg=WHITE,
            activebackground="#B71C1C", activeforeground=WHITE,
            relief=tk.FLAT, bd=0, cursor="hand2",
            anchor=tk.W, padx=10, pady=10,
            command=self._on_logout,
        ).pack(fill=tk.X, side=tk.BOTTOM)

        tk.Label(
            self._sidebar,
            text=f"v{APP_VERSION}",
            font=(FONT_FAMILY, 8),
            bg=SIDEBAR_BG, fg="#78909C",
        ).pack(side=tk.BOTTOM, pady=4)

    def _set_active_nav(self, label):
        """Highlight the active sidebar button."""
        for name, btn in self._nav_buttons.items():
            btn.config(bg=SIDEBAR_ACTIVE if name == label else SIDEBAR_BG)

    def _restore_btn_color(self, btn):
        """Restore hover button to its correct resting colour."""
        for name, b in self._nav_buttons.items():
            if b is btn:
                text = name.strip()
                for lbl, _ in self._NAV_ITEMS:
                    if lbl == text:
                        is_active = (btn.cget("bg") == SIDEBAR_ACTIVE)
                        btn.config(bg=SIDEBAR_ACTIVE if is_active else SIDEBAR_BG)
                        return

    # ------------------------------------------------------------------
    # Status Bar
    # ------------------------------------------------------------------

    def _build_status_bar(self):
        """Build the bottom status bar."""
        bar = tk.Frame(self.root, bg=STATUS_BG, height=28)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)

        # DB indicator
        tk.Label(bar, text="●", font=(FONT_FAMILY, 10),
                 bg=STATUS_BG, fg=SUCCESS_GREEN).pack(side=tk.LEFT, padx=(10, 2), pady=4)
        tk.Label(bar, text=STATUS_CONNECTED, font=(FONT_FAMILY, 9),
                 bg=STATUS_BG, fg=TEXT_MEDIUM).pack(side=tk.LEFT, pady=4)

        tk.Frame(bar, bg=MID_GRAY, width=1).pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=4)

        self._status_var = tk.StringVar(value=STATUS_READY)
        tk.Label(bar, textvariable=self._status_var, font=(FONT_FAMILY, 9),
                 bg=STATUS_BG, fg=STATUS_FG).pack(side=tk.LEFT)

    def _set_status(self, message):
        """Update the status bar text."""
        self._status_var.set(message)

    # ------------------------------------------------------------------
    # Content Area helpers
    # ------------------------------------------------------------------

    def _clear_content(self):
        """Remove all widgets from the content area."""
        for w in self._content.winfo_children():
            w.destroy()

    def _page_header(self, title, subtitle=""):
        """Render a standard page title bar at the top of the content area."""
        bar = tk.Frame(self._content, bg=WHITE, padx=20, pady=12)
        bar.pack(fill=tk.X)
        tk.Label(bar, text=title, font=(FONT_FAMILY, 15, "bold"),
                 bg=WHITE, fg=TEXT_DARK).pack(anchor=tk.W)
        if subtitle:
            tk.Label(bar, text=subtitle, font=(FONT_FAMILY, 10),
                     bg=WHITE, fg=TEXT_MEDIUM).pack(anchor=tk.W)
        ttk.Separator(self._content, orient=tk.HORIZONTAL).pack(fill=tk.X)

    # ------------------------------------------------------------------
    # VIEW: Dashboard
    # ------------------------------------------------------------------

    def show_dashboard(self):
        """Render the dashboard statistics card view."""
        self._clear_content()
        self._set_active_nav("Dashboard")
        self._page_header("Dashboard", "Overview of clinic activity today")

        stats = functions.get_dashboard_stats(self.conn)

        cards_data = [
            ("Total Patients",   stats["total"],      PRIMARY_BLUE,   WHITE),
            ("Today's Patients", stats["today"],      SECONDARY_BLUE, WHITE),
            ("Waiting Queue",    stats["waiting"],    "#00897B",      WHITE),
            ("Next Queue #",     stats["next_queue"], "#6D4C41",      WHITE),
            ("Male Patients",    stats["male"],       "#1565C0",      WHITE),
            ("Female Patients",  stats["female"],     "#AD1457",      WHITE),
        ]

        # Two rows of three cards
        scroll = tk.Frame(self._content, bg=LIGHT_GRAY)
        scroll.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

        for i, (label, value, bg, fg) in enumerate(cards_data):
            row, col = divmod(i, 3)
            card = tk.Frame(scroll, bg=bg, padx=20, pady=16,
                            relief=tk.FLAT, bd=0)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            tk.Label(card, text=str(value),
                     font=(FONT_FAMILY, 32, "bold"),
                     bg=bg, fg=fg).pack()
            tk.Label(card, text=label,
                     font=(FONT_FAMILY, 10),
                     bg=bg, fg=fg).pack()
            scroll.columnconfigure(col, weight=1)
            scroll.rowconfigure(row, weight=0)

        # Average age row
        avg_frame = tk.Frame(scroll, bg=WHITE, padx=20, pady=12)
        avg_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="ew")
        tk.Label(avg_frame, text=f"Average Patient Age:  {stats['avg_age']} years",
                 font=(FONT_FAMILY, 11), bg=WHITE, fg=TEXT_DARK).pack(side=tk.LEFT)

        self._set_status(STATUS_READY)

    # ------------------------------------------------------------------
    # VIEW: Register Patient
    # ------------------------------------------------------------------

    def show_register(self):
        """Render the patient registration/edit form."""
        self._clear_content()
        self._set_active_nav("Register Patient")
        self._page_header("Register / Edit Patient", "Complete all required fields (*)")
        self._current_patient_id = None

        outer = tk.Frame(self._content, bg=LIGHT_GRAY)
        outer.pack(fill=tk.BOTH, expand=True, padx=20, pady=14)

        form_card = tk.Frame(outer, bg=WHITE, padx=24, pady=20)
        form_card.pack(fill=tk.BOTH, expand=True)

        # Grid form
        fields_left = [
            ("Full Name *",         "full_name",         "entry"),
            ("Age *",               "age",               "entry"),
            ("Gender *",            "gender",            "combo", GENDER_OPTIONS),
            ("Phone Number *",      "phone",             "entry"),
            ("Address *",           "address",           "entry"),
        ]
        fields_right = [
            ("Blood Group",         "blood_group",       "combo", BLOOD_GROUPS),
            ("Emergency Contact",   "emergency_contact", "entry"),
            ("Illness / Complaint *","illness",          "combo", ILLNESS_SUGGESTIONS),
            ("Queue Number",        "queue_number",      "readonly"),
            ("Registration Date",   "registration_date", "readonly"),
        ]

        self._form_vars = {}
        left_frame  = tk.Frame(form_card, bg=WHITE)
        right_frame = tk.Frame(form_card, bg=WHITE)
        left_frame.grid(row=0, column=0, sticky="nw", padx=(0, 20))
        right_frame.grid(row=0, column=1, sticky="nw")
        form_card.columnconfigure(0, weight=1)
        form_card.columnconfigure(1, weight=1)

        self._render_form_fields(left_frame,  fields_left)
        self._render_form_fields(right_frame, fields_right)

        # Auto-fill read-only fields
        next_q = database.get_next_queue_number(self.conn)
        self._form_vars["queue_number"].set(str(next_q))
        self._form_vars["registration_date"].set(datetime.date.today().isoformat())

        # Buttons
        btn_frame = tk.Frame(form_card, bg=WHITE)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=(16, 0), sticky="w")

        buttons = [
            ("Register",  self._do_register, PRIMARY_BLUE,  WHITE),
            ("Update",    self._do_update,   "#00897B",     WHITE),
            ("Delete",    self._do_delete,   ERROR_RED,     WHITE),
            ("Clear",     self._do_clear,    LIGHT_GRAY,    TEXT_DARK),
            ("Refresh",   self._do_refresh,  SECONDARY_BLUE, WHITE),
        ]
        for text, cmd, bg, fg in buttons:
            b = tk.Button(btn_frame, text=text,
                          font=(FONT_FAMILY, 10, "bold"),
                          bg=bg, fg=fg,
                          activebackground=bg, activeforeground=fg,
                          relief=tk.FLAT, cursor="hand2",
                          padx=14, pady=7,
                          command=cmd)
            b.pack(side=tk.LEFT, padx=(0, 8))

        # Records table below form
        ttk.Separator(self._content, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=20)
        self._build_records_section(self._content, compact=True)

    def _render_form_fields(self, parent, field_defs):
        """Render a column of labelled form fields into parent."""
        for row_idx, field_def in enumerate(field_defs):
            label_text = field_def[0]
            key        = field_def[1]
            ftype      = field_def[2]
            options    = field_def[3] if len(field_def) > 3 else []

            tk.Label(parent, text=label_text, font=(FONT_FAMILY, 9),
                     bg=WHITE, fg=TEXT_MEDIUM).grid(
                row=row_idx * 2, column=0, sticky="w", pady=(6, 0))

            var = tk.StringVar()
            self._form_vars[key] = var

            if ftype == "entry":
                widget = tk.Entry(parent, textvariable=var,
                                  font=(FONT_FAMILY, 10), relief=tk.FLAT,
                                  highlightthickness=1,
                                  highlightbackground=MID_GRAY,
                                  highlightcolor=PRIMARY_BLUE)
                widget.grid(row=row_idx * 2 + 1, column=0, sticky="ew", ipady=6, pady=(0, 2))
            elif ftype == "combo":
                widget = ttk.Combobox(parent, textvariable=var,
                                      values=options,
                                      font=(FONT_FAMILY, 10), state="normal")
                widget.grid(row=row_idx * 2 + 1, column=0, sticky="ew", ipady=3, pady=(0, 2))
            elif ftype == "readonly":
                widget = tk.Entry(parent, textvariable=var,
                                  font=(FONT_FAMILY, 10), relief=tk.FLAT,
                                  state="readonly",
                                  readonlybackground=LIGHT_GRAY,
                                  highlightthickness=1,
                                  highlightbackground=MID_GRAY)
                widget.grid(row=row_idx * 2 + 1, column=0, sticky="ew", ipady=6, pady=(0, 2))

            parent.columnconfigure(0, weight=1)

    # ------------------------------------------------------------------
    # VIEW: Patient Records (standalone)
    # ------------------------------------------------------------------

    def show_records(self):
        """Render the standalone patient records view with search."""
        self._clear_content()
        self._set_active_nav("Patient Records")
        self._page_header("Patient Records", "All registered patients")
        self._build_records_section(self._content, compact=False)

    def _build_records_section(self, parent, compact=False):
        """
        Build the search bar + treeview section.

        Args:
            parent  (tk.Frame): Container widget.
            compact (bool):     Reduce row height for embedded use in register view.
        """
        # Search bar
        search_bar = tk.Frame(parent, bg=WHITE, padx=14, pady=8)
        search_bar.pack(fill=tk.X)

        tk.Label(search_bar, text="Search by:", font=(FONT_FAMILY, 9),
                 bg=WHITE, fg=TEXT_MEDIUM).pack(side=tk.LEFT)

        self._search_field_var = tk.StringVar(value="full_name")
        field_map = {
            "Full Name":    "full_name",
            "Patient ID":   "patient_id",
            "Phone":        "phone",
            "Illness":      "illness",
            "Queue #":      "queue_number",
        }
        self._field_map = field_map

        field_combo = ttk.Combobox(
            search_bar,
            textvariable=self._search_field_var,
            values=list(field_map.keys()),
            font=(FONT_FAMILY, 9),
            state="readonly",
            width=12,
        )
        field_combo.set("Full Name")
        field_combo.pack(side=tk.LEFT, padx=(4, 8))

        self._search_var = tk.StringVar()
        self._search_var.trace("w", lambda *a: self._live_search())
        search_entry = tk.Entry(search_bar, textvariable=self._search_var,
                                font=(FONT_FAMILY, 10), relief=tk.FLAT,
                                highlightthickness=1,
                                highlightbackground=MID_GRAY,
                                highlightcolor=PRIMARY_BLUE,
                                width=28)
        search_entry.pack(side=tk.LEFT, ipady=5)

        tk.Button(search_bar, text="Clear",
                  font=(FONT_FAMILY, 9),
                  bg=LIGHT_GRAY, fg=TEXT_MEDIUM,
                  relief=tk.FLAT, cursor="hand2",
                  padx=8, pady=3,
                  command=lambda: self._search_var.set("")).pack(side=tk.LEFT, padx=6)

        # Treeview
        tree_frame = tk.Frame(parent, bg=LIGHT_GRAY)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 8))

        self._tree = ttk.Treeview(
            tree_frame,
            columns=TREE_COLUMNS,
            show="headings",
            selectmode="browse",
            height=8 if compact else 18,
        )
        for col, heading, width, anchor in zip(
                TREE_COLUMNS, TREE_HEADINGS, TREE_WIDTHS, TREE_ANCHORS):
            self._tree.heading(col, text=heading,
                               command=lambda c=col: self._sort_tree(c))
            self._tree.column(col, width=width, anchor=anchor, minwidth=40)

        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL,   command=self._tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self._tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        # Bindings
        self._tree.bind("<Double-1>",  self._on_tree_double_click)
        self._tree.bind("<Button-3>",  self._on_tree_right_click)

        # Context menu
        self._context_menu = tk.Menu(self.root, tearoff=0)
        self._context_menu.add_command(label="View Details", command=self._view_details)
        self._context_menu.add_command(label="Edit",         command=self._load_to_form)
        self._context_menu.add_separator()
        self._context_menu.add_command(label="Delete",       command=self._do_delete)

        # Load all records
        self._refresh_tree()

    def _refresh_tree(self):
        """Reload all patients into the treeview."""
        records = database.get_all_patients(self.conn)
        functions.populate_treeview(self._tree, records)
        self._set_status(f"{len(records)} patient record(s) loaded.")

    def _live_search(self):
        """Called on every keystroke in the search box."""
        term  = self._search_var.get()
        label = self._search_field_var.get()
        field = self._field_map.get(label, "full_name")
        functions.search_patients(field, term, self.conn, self._tree, self._set_status)

    def _sort_tree(self, col):
        """Sort the treeview by the clicked column header."""
        rows = [(self._tree.set(item, col), item) for item in self._tree.get_children("")]
        try:
            rows.sort(key=lambda x: int(x[0]))
        except ValueError:
            rows.sort(key=lambda x: x[0].lower())
        for index, (_, item) in enumerate(rows):
            self._tree.move(item, "", index)
            tag = "evenrow" if index % 2 == 0 else "oddrow"
            self._tree.item(item, tags=(tag,))

    # ------------------------------------------------------------------
    # Treeview events
    # ------------------------------------------------------------------

    def _get_selected_row(self):
        """Return the selected treeview row values, or None."""
        sel = self._tree.selection()
        if not sel:
            return None
        return self._tree.item(sel[0], "values")

    def _on_tree_double_click(self, event):
        self._load_to_form()

    def _on_tree_right_click(self, event):
        row = self._tree.identify_row(event.y)
        if row:
            self._tree.selection_set(row)
            self._context_menu.post(event.x_root, event.y_root)

    def _load_to_form(self):
        """Populate the registration form with the selected record for editing."""
        row = self._get_selected_row()
        if not row:
            return
        # row: (patient_id, full_name, age, gender, phone, blood_group,
        #        illness, queue_number, registration_date)
        record = database.get_patient_by_id(self.conn, int(row[0]))
        if not record:
            return

        self._current_patient_id = record["patient_id"]

        if not hasattr(self, "_form_vars") or not self._form_vars:
            self.show_register()
            self.root.after(100, lambda: self._load_to_form())
            return

        mapping = {
            "full_name":         record["full_name"],
            "age":               str(record["age"]),
            "gender":            record["gender"],
            "phone":             record["phone"],
            "address":           record["address"],
            "blood_group":       record.get("blood_group", ""),
            "emergency_contact": record.get("emergency_contact", ""),
            "illness":           record["illness"],
            "queue_number":      str(record["queue_number"]),
            "registration_date": record["registration_date"],
        }
        for key, value in mapping.items():
            if key in self._form_vars:
                self._form_vars[key].set(value)

        self._set_status(f"Editing patient ID {self._current_patient_id}.")

    def _view_details(self):
        """Show a details popup for the selected patient."""
        row = self._get_selected_row()
        if not row:
            return
        record = database.get_patient_by_id(self.conn, int(row[0]))
        if not record:
            return

        win = tk.Toplevel(self.root)
        win.title(f"Patient Details — {record['full_name']}")
        win.geometry("420x360")
        win.configure(bg=WHITE)
        win.resizable(False, False)

        hdr = tk.Frame(win, bg=PRIMARY_BLUE, height=40)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="Patient Details", font=(FONT_FAMILY, 11, "bold"),
                 bg=PRIMARY_BLUE, fg=WHITE).place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        body = tk.Frame(win, bg=WHITE, padx=24, pady=16)
        body.pack(fill=tk.BOTH, expand=True)

        fields = [
            ("Patient ID",       record["patient_id"]),
            ("Full Name",        record["full_name"]),
            ("Age",              record["age"]),
            ("Gender",           record["gender"]),
            ("Phone",            record["phone"]),
            ("Address",          record["address"]),
            ("Blood Group",      record.get("blood_group", "—")),
            ("Emergency Contact",record.get("emergency_contact", "—")),
            ("Illness",          record["illness"]),
            ("Queue Number",     record["queue_number"]),
            ("Registered",       record["registration_date"]),
        ]
        for lbl, val in fields:
            row_f = tk.Frame(body, bg=WHITE)
            row_f.pack(fill=tk.X, pady=2)
            tk.Label(row_f, text=f"{lbl}:", font=(FONT_FAMILY, 9, "bold"),
                     bg=WHITE, fg=TEXT_MEDIUM, width=18, anchor=tk.W).pack(side=tk.LEFT)
            tk.Label(row_f, text=str(val), font=(FONT_FAMILY, 9),
                     bg=WHITE, fg=TEXT_DARK).pack(side=tk.LEFT)

        tk.Button(win, text="Close", font=(FONT_FAMILY, 10),
                  bg=PRIMARY_BLUE, fg=WHITE, relief=tk.FLAT,
                  cursor="hand2", padx=16, pady=6,
                  command=win.destroy).pack(pady=8)

    # ------------------------------------------------------------------
    # Form actions
    # ------------------------------------------------------------------

    def _collect_form_data(self):
        """Build a dict from the current form field StringVar values."""
        return {k: v.get() for k, v in self._form_vars.items()}

    def _do_register(self):
        data = self._collect_form_data()
        functions.register_patient(
            data, self.conn, self._refresh_tree, self._set_status
        )
        if hasattr(self, "_form_vars"):
            self._do_clear()

    def _do_update(self):
        data = self._collect_form_data()
        functions.update_patient(
            self._current_patient_id, data,
            self.conn, self._refresh_tree, self._set_status
        )

    def _do_delete(self):
        row = self._get_selected_row()
        if not row:
            messagebox.showwarning("No Selection", "Please select a patient to delete.")
            return
        pid   = int(row[0])
        pname = row[1]
        functions.delete_patient(
            pid, pname, self.conn, self._refresh_tree, self._set_status
        )
        self._current_patient_id = None

    def _do_clear(self):
        """Clear all form fields and reset to defaults."""
        for key, var in self._form_vars.items():
            var.set("")
        self._current_patient_id = None
        next_q = database.get_next_queue_number(self.conn)
        self._form_vars["queue_number"].set(str(next_q))
        self._form_vars["registration_date"].set(datetime.date.today().isoformat())

    def _do_refresh(self):
        self._refresh_tree()

    # ------------------------------------------------------------------
    # VIEW: Reports
    # ------------------------------------------------------------------

    def show_reports(self):
        """Render the reports action panel."""
        self._clear_content()
        self._set_active_nav("Reports")
        self._page_header("Reports", "Generate and export patient data reports")

        outer = tk.Frame(self._content, bg=LIGHT_GRAY, padx=24, pady=20)
        outer.pack(fill=tk.BOTH, expand=True)

        report_buttons = [
            ("Export All Records (CSV)",
             "Export every patient record to a CSV file.",
             lambda: reports.export_all_to_csv(self.conn, self._set_status)),
            ("Daily Report",
             f"Export today's patients to exports/daily_report_{datetime.date.today()}.csv",
             lambda: reports.export_daily_report(self.conn, self._set_status)),
            ("Print Preview",
             "View a formatted report of today's patients in a print-ready window.",
             lambda: reports.show_print_preview(self.conn, self.root)),
        ]

        for title, desc, cmd in report_buttons:
            card = tk.Frame(outer, bg=WHITE, padx=20, pady=16, relief=tk.FLAT)
            card.pack(fill=tk.X, pady=8)
            tk.Label(card, text=title, font=(FONT_FAMILY, 12, "bold"),
                     bg=WHITE, fg=TEXT_DARK).pack(anchor=tk.W)
            tk.Label(card, text=desc, font=(FONT_FAMILY, 9),
                     bg=WHITE, fg=TEXT_MEDIUM).pack(anchor=tk.W, pady=(2, 8))
            tk.Button(card, text="Generate", font=(FONT_FAMILY, 10, "bold"),
                      bg=PRIMARY_BLUE, fg=WHITE, relief=tk.FLAT, cursor="hand2",
                      padx=14, pady=6, command=cmd).pack(anchor=tk.W)

    # ------------------------------------------------------------------
    # VIEW: Statistics
    # ------------------------------------------------------------------

    def show_statistics(self):
        """Render the statistics card panel."""
        self._clear_content()
        self._set_active_nav("Statistics")
        self._page_header("Statistics", "Key metrics for the clinic")

        stats = functions.get_dashboard_stats(self.conn)

        outer = tk.Frame(self._content, bg=LIGHT_GRAY, padx=20, pady=16)
        outer.pack(fill=tk.BOTH, expand=True)

        items = [
            ("Total Patients Registered", stats["total"],      PRIMARY_BLUE),
            ("Patients Registered Today", stats["today"],      SECONDARY_BLUE),
            ("Male Patients",             stats["male"],       "#1565C0"),
            ("Female Patients",           stats["female"],     "#AD1457"),
            ("Other / Unspecified",       stats["other"],      "#616161"),
            ("Average Patient Age",       f"{stats['avg_age']} yrs", "#00897B"),
            ("Next Queue Number",         stats["next_queue"], "#6D4C41"),
        ]

        for i, (label, value, colour) in enumerate(items):
            card = tk.Frame(outer, bg=WHITE, padx=16, pady=12)
            card.grid(row=i // 2, column=i % 2, padx=8, pady=8, sticky="ew")
            outer.columnconfigure(i % 2, weight=1)

            indicator = tk.Frame(card, bg=colour, width=5)
            indicator.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))

            info = tk.Frame(card, bg=WHITE)
            info.pack(side=tk.LEFT, fill=tk.X, expand=True)
            tk.Label(info, text=str(value), font=(FONT_FAMILY, 22, "bold"),
                     bg=WHITE, fg=colour).pack(anchor=tk.W)
            tk.Label(info, text=label, font=(FONT_FAMILY, 9),
                     bg=WHITE, fg=TEXT_MEDIUM).pack(anchor=tk.W)

    # ------------------------------------------------------------------
    # VIEW: Charts
    # ------------------------------------------------------------------

    def show_charts(self):
        """Render the three embedded Matplotlib charts."""
        self._clear_content()
        self._set_active_nav("Charts")
        self._page_header("Charts", "Visual analytics")

        nb = ttk.Notebook(self._content)
        nb.pack(fill=tk.BOTH, expand=True, padx=14, pady=10)

        # Tab 1 — Gender Pie
        t1 = tk.Frame(nb, bg=WHITE)
        nb.add(t1, text="  Gender Distribution  ")
        charts.render_gender_pie_chart(t1, self.conn)

        # Tab 2 — Illness Bar
        t2 = tk.Frame(nb, bg=WHITE)
        nb.add(t2, text="  Common Illnesses  ")
        charts.render_illness_bar_chart(t2, self.conn)

        # Tab 3 — Daily Line
        t3 = tk.Frame(nb, bg=WHITE)
        nb.add(t3, text="  Daily Registrations  ")
        charts.render_daily_line_chart(t3, self.conn)

    # ------------------------------------------------------------------
    # VIEW: Settings
    # ------------------------------------------------------------------

    def show_settings(self):
        """Render the settings panel."""
        self._clear_content()
        self._set_active_nav("Settings")
        self._page_header("Settings", "Customise application preferences")
        settings_module.SettingsPanel(
            self._content, self._app_settings, self._apply_settings
        )

    def _apply_settings(self, theme, font_size):
        """Apply new theme and font_size selections."""
        self._app_settings["theme"]     = theme
        self._app_settings["font_size"] = font_size
        settings_module.apply_theme(theme, self._style)
        logging.info("Settings applied: theme=%s  font_size=%s", theme, font_size)

    # ------------------------------------------------------------------
    # VIEW: Backup / Restore
    # ------------------------------------------------------------------

    def show_backup(self):
        """Render the backup and restore panel."""
        self._clear_content()
        self._set_active_nav("Backup / Restore")
        self._page_header("Backup & Restore", "Protect your clinic data")

        outer = tk.Frame(self._content, bg=LIGHT_GRAY, padx=24, pady=20)
        outer.pack(fill=tk.BOTH, expand=True)

        for title, desc, cmd in [
            ("Backup Database",
             "Create a timestamped copy of the clinic database in the database/ folder.",
             self._backup),
            ("Restore Database",
             "Replace the current database with a selected backup file.\n"
             "Warning: this will overwrite all current data.",
             self._restore),
        ]:
            card = tk.Frame(outer, bg=WHITE, padx=20, pady=16)
            card.pack(fill=tk.X, pady=8)
            tk.Label(card, text=title, font=(FONT_FAMILY, 12, "bold"),
                     bg=WHITE, fg=TEXT_DARK).pack(anchor=tk.W)
            tk.Label(card, text=desc, font=(FONT_FAMILY, 9),
                     bg=WHITE, fg=TEXT_MEDIUM, wraplength=600, justify=tk.LEFT).pack(
                anchor=tk.W, pady=(2, 8))
            tk.Button(card, text=title, font=(FONT_FAMILY, 10, "bold"),
                      bg=PRIMARY_BLUE, fg=WHITE, relief=tk.FLAT, cursor="hand2",
                      padx=14, pady=6, command=cmd).pack(anchor=tk.W)

    def _backup(self):
        """Run the database backup procedure."""
        import shutil, os
        from constants import DB_PATH, DB_DIR
        os.makedirs(DB_DIR, exist_ok=True)
        ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = os.path.join(DB_DIR, f"backup_clinic_{ts}.db")
        try:
            shutil.copy2(DB_PATH, dest)
            self._set_status("Database backup complete.")
            messagebox.showinfo("Backup Complete", f"Database backed up to:\n{dest}")
            logging.info("Database backed up to %s", dest)
        except Exception as exc:
            messagebox.showerror("Backup Failed", str(exc))
            logging.error("Backup failed: %s", exc)

    def _restore(self):
        """Run the database restore procedure."""
        import shutil
        from tkinter import filedialog
        from constants import DB_PATH, DB_DIR

        filepath = filedialog.askopenfilename(
            initialdir=DB_DIR,
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")],
            title="Select Backup File to Restore",
        )
        if not filepath:
            return
        if not messagebox.askyesno(
            "Confirm Restore",
            "This will overwrite the current database with the selected backup.\n\n"
            "All unsaved changes will be lost.  Continue?"
        ):
            return
        try:
            self.conn.close()
            shutil.copy2(filepath, DB_PATH)
            self.conn = database.get_connection()
            self._set_status("Database restored successfully.")
            messagebox.showinfo("Restore Complete", "Database restored successfully.")
            logging.info("Database restored from %s", filepath)
            self.show_dashboard()
        except Exception as exc:
            messagebox.showerror("Restore Failed", str(exc))
            logging.error("Restore failed: %s", exc)
            self.conn = database.get_connection()

    # ------------------------------------------------------------------
    # Logout
    # ------------------------------------------------------------------

    def _on_logout(self):
        """Log out and return to the login screen."""
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            logging.info("User '%s' logged out.", self.username)
            self.conn.close()
            self.root.withdraw()
            from login import LoginScreen
            LoginScreen(self.root, on_success=self._on_relogin)

    def _on_relogin(self, username):
        """Re-open the dashboard after re-authentication."""
        self.username = username
        self.conn     = database.get_connection()
        self.root.deiconify()
        self._clear_content()
        self.show_dashboard()

    # ------------------------------------------------------------------
    # Help dialogs
    # ------------------------------------------------------------------

    def _show_about(self):
        messagebox.showinfo(
            "About",
            f"{APP_TITLE}\n\n"
            f"Version: {APP_VERSION}\n"
            f"Course:  {__import__('constants').COURSE_TITLE}\n\n"
            f"{__import__('constants').SDG_NOTE}\n\n"
            f"Developed by: {__import__('constants').DEVELOPER}"
        )

    def _show_user_guide(self):
        win = tk.Toplevel(self.root)
        win.title("User Guide")
        win.geometry("560x440")
        win.configure(bg=WHITE)

        hdr = tk.Frame(win, bg=PRIMARY_BLUE, height=40)
        hdr.pack(fill=tk.X)
        hdr.pack_propagate(False)
        tk.Label(hdr, text="User Guide", font=(FONT_FAMILY, 11, "bold"),
                 bg=PRIMARY_BLUE, fg=WHITE).place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        from tkinter import scrolledtext as st
        txt = st.ScrolledText(win, font=(FONT_FAMILY, 10), bg=WHITE,
                              fg=TEXT_DARK, relief=tk.FLAT, padx=16, pady=12)
        txt.pack(fill=tk.BOTH, expand=True)

        guide = """
COMMUNITY HEALTH CLINIC QUEUE MANAGEMENT SYSTEM — USER GUIDE

1. LOGGING IN
   • Enter username: admin  and  password: admin123
   • Click LOGIN or press Enter.

2. DASHBOARD
   • View live statistics: total patients, today's count, queue depth.

3. REGISTERING A PATIENT
   • Click "Register Patient" in the sidebar.
   • Fill in all fields marked with *.
   • Queue Number and Date are assigned automatically.
   • Click REGISTER to save.

4. VIEWING / SEARCHING RECORDS
   • Click "Patient Records".
   • Type in the search box to filter by name, phone, illness, etc.
   • Double-click any row to load it into the form for editing.

5. UPDATING A RECORD
   • Load a patient record (double-click a row).
   • Modify any field.
   • Click UPDATE.

6. DELETING A RECORD
   • Select a row in the table.
   • Click DELETE and confirm.

7. REPORTS
   • Export All Records → CSV file of all patients.
   • Daily Report      → CSV of today's patients.
   • Print Preview     → Formatted on-screen preview.

8. CHARTS
   • Gender Pie, Illness Bar, and Daily Line charts.
   • Requires matplotlib installed (pip install matplotlib).

9. BACKUP / RESTORE
   • Backup  → Saves a copy of clinic.db with a timestamp.
   • Restore → Overwrites clinic.db with a selected backup.

10. SETTINGS
    • Switch between Light and Dark themes.
    • Adjust font size for accessibility.
"""
        txt.insert(tk.END, guide)
        txt.config(state=tk.DISABLED)

        tk.Button(win, text="Close", font=(FONT_FAMILY, 10),
                  bg=PRIMARY_BLUE, fg=WHITE, relief=tk.FLAT,
                  cursor="hand2", padx=16, pady=6,
                  command=win.destroy).pack(pady=8)
