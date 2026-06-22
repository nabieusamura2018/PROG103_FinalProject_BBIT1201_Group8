"""
reports.py
Reporting module — CSV export, daily report, and print preview.
"""

import csv
import os
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import logging

import database
from constants import (
    EXPORTS_DIR, APP_TITLE, FONT_FAMILY, PRIMARY_BLUE, WHITE,
    LIGHT_GRAY, TEXT_DARK, STATUS_EXPORTED
)

CSV_HEADERS = [
    "Patient ID", "Full Name", "Age", "Gender", "Phone", "Address",
    "Blood Group", "Emergency Contact", "Illness", "Queue Number", "Registration Date"
]


# ---------------------------------------------------------------------------
# CSV Export
# ---------------------------------------------------------------------------

def export_all_to_csv(conn, status_callback):
    """
    Export all patient records to a user-selected CSV file.

    Args:
        conn            (Connection): Active database connection.
        status_callback (callable):   Status bar update function.
    """
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    default_name = f"patients_{datetime.date.today().isoformat()}.csv"
    filepath = filedialog.asksaveasfilename(
        initialdir=EXPORTS_DIR,
        initialfile=default_name,
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
        title="Export Patient Records",
    )
    if not filepath:
        return

    try:
        records = database.get_all_patients_full(conn)
        _write_csv(filepath, records)
        status_callback(STATUS_EXPORTED)
        messagebox.showinfo("Export Complete", f"Records exported to:\n{filepath}")
        logging.info("CSV exported: %s  (%d records)", filepath, len(records))
    except Exception as exc:
        messagebox.showerror("Export Failed", str(exc))
        logging.error("CSV export failed: %s", exc)


# ---------------------------------------------------------------------------
# Daily Report
# ---------------------------------------------------------------------------

def export_daily_report(conn, status_callback):
    """
    Export today's patients to a timestamped CSV in the exports folder.

    Args:
        conn            (Connection): Active database connection.
        status_callback (callable):   Status bar update function.
    """
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    today     = datetime.date.today().isoformat()
    filepath  = os.path.join(EXPORTS_DIR, f"daily_report_{today}.csv")

    try:
        records = database.get_today_patients_full(conn)
        _write_csv(filepath, records)
        status_callback(STATUS_EXPORTED)
        messagebox.showinfo(
            "Daily Report",
            f"Daily report for {today} saved to:\n{filepath}\n\n"
            f"Total patients today: {len(records)}"
        )
        logging.info("Daily report exported: %s  (%d records)", filepath, len(records))
    except Exception as exc:
        messagebox.showerror("Daily Report Failed", str(exc))
        logging.error("Daily report failed: %s", exc)


# ---------------------------------------------------------------------------
# Print Preview
# ---------------------------------------------------------------------------

def show_print_preview(conn, parent_window):
    """
    Open a Toplevel window showing a formatted text report of today's patients.

    Args:
        conn          (Connection): Active database connection.
        parent_window (tk.Toplevel or tk.Tk): Owner window for the dialog.
    """
    today   = datetime.date.today()
    records = database.get_today_patients_full(conn)

    preview_win = tk.Toplevel(parent_window)
    preview_win.title("Print Preview — Daily Patient Report")
    preview_win.geometry("700x520")
    preview_win.configure(bg=WHITE)
    preview_win.resizable(True, True)

    # Header bar
    hdr = tk.Frame(preview_win, bg=PRIMARY_BLUE, height=40)
    hdr.pack(fill=tk.X)
    hdr.pack_propagate(False)
    tk.Label(
        hdr, text="Print Preview", font=(FONT_FAMILY, 11, "bold"),
        bg=PRIMARY_BLUE, fg=WHITE
    ).pack(side=tk.LEFT, padx=14, pady=8)
    tk.Button(
        hdr, text="Close", font=(FONT_FAMILY, 9),
        bg="#1976D2", fg=WHITE, relief=tk.FLAT, cursor="hand2",
        command=preview_win.destroy
    ).pack(side=tk.RIGHT, padx=10, pady=6)

    # Text area
    txt = scrolledtext.ScrolledText(
        preview_win,
        font=("Courier New", 10),
        bg=WHITE, fg=TEXT_DARK,
        relief=tk.FLAT,
        padx=12, pady=12,
        wrap=tk.NONE,
    )
    txt.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    # Build report string
    sep = "=" * 80
    thin = "-" * 80
    lines = [
        sep,
        f"  {APP_TITLE}",
        f"  DAILY PATIENT REPORT",
        f"  Date: {today.strftime('%A, %d %B %Y')}",
        sep,
        f"  {'#':<4} {'ID':<8} {'Name':<22} {'Age':<5} {'Gender':<8} {'Queue':<7} {'Illness'}",
        thin,
    ]
    for i, r in enumerate(records, 1):
        # r = (patient_id, full_name, age, gender, phone, address,
        #       blood_group, emergency_contact, illness, queue_number, registration_date)
        lines.append(
            f"  {i:<4} {r[0]:<8} {r[1]:<22} {r[2]:<5} {r[3]:<8} {r[9]:<7} {r[8]}"
        )

    lines += [
        thin,
        f"  Total Patients Today: {len(records)}",
        sep,
    ]

    txt.insert(tk.END, "\n".join(lines))
    txt.config(state=tk.DISABLED)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _write_csv(filepath, records):
    """Write records (full column list) to a CSV file with standard headers."""
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADERS)
        for row in records:
            writer.writerow(row)
