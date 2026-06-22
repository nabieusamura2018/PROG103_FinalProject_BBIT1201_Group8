"""
functions.py
Business Logic Layer.
Orchestrates operations between the UI (gui.py) and the data layer (database.py).
"""

import datetime
import logging
import tkinter as tk
from tkinter import messagebox

import database
import validation
from constants import (
    STATUS_REGISTERED, STATUS_UPDATED, STATUS_DELETED,
    TREEVIEW_ODD, TREEVIEW_EVEN
)


# ---------------------------------------------------------------------------
# Patient Registration
# ---------------------------------------------------------------------------

def register_patient(form_data, conn, refresh_callback, status_callback):
    """
    Validate form data and insert a new patient record.

    Args:
        form_data       (dict):     Raw form field values.
        conn            (Connection): Active database connection.
        refresh_callback(callable): Called after successful insert to refresh table.
        status_callback (callable): Called with a status message string.
    """
    is_valid, error = validation.validate_patient_data(form_data)
    if not is_valid:
        messagebox.showerror("Validation Error", error)
        return False

    try:
        form_data["queue_number"]      = database.get_next_queue_number(conn)
        form_data["registration_date"] = datetime.date.today().isoformat()
        database.insert_patient(conn, form_data)
        status_callback(STATUS_REGISTERED)
        messagebox.showinfo(
            "Patient Registered",
            f"Patient registered successfully!\n\n"
            f"Name:     {form_data['full_name']}\n"
            f"Queue #:  {form_data['queue_number']}"
        )
        refresh_callback()
        return True
    except RuntimeError as exc:
        messagebox.showerror("Registration Failed", str(exc))
        logging.error("register_patient failed: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Patient Update
# ---------------------------------------------------------------------------

def update_patient(patient_id, form_data, conn, refresh_callback, status_callback):
    """
    Validate form data and update an existing patient record.

    Args:
        patient_id      (int):      ID of the patient to update.
        form_data       (dict):     Updated form field values.
        conn            (Connection): Active database connection.
        refresh_callback(callable): Called after successful update.
        status_callback (callable): Called with a status message string.
    """
    if not patient_id:
        messagebox.showwarning("No Selection", "Please select a patient to update.")
        return False

    is_valid, error = validation.validate_patient_data(form_data)
    if not is_valid:
        messagebox.showerror("Validation Error", error)
        return False

    try:
        database.update_patient(conn, patient_id, form_data)
        status_callback(STATUS_UPDATED)
        messagebox.showinfo("Updated", "Patient record updated successfully.")
        refresh_callback()
        return True
    except RuntimeError as exc:
        messagebox.showerror("Update Failed", str(exc))
        logging.error("update_patient failed: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Patient Delete
# ---------------------------------------------------------------------------

def delete_patient(patient_id, patient_name, conn, refresh_callback, status_callback):
    """
    Confirm with the user and delete a patient record.

    Args:
        patient_id      (int):      ID of the patient to delete.
        patient_name    (str):      Display name for confirmation dialog.
        conn            (Connection): Active database connection.
        refresh_callback(callable): Called after successful delete.
        status_callback (callable): Called with a status message string.
    """
    if not patient_id:
        messagebox.showwarning("No Selection", "Please select a patient to delete.")
        return False

    confirmed = messagebox.askyesno(
        "Confirm Delete",
        f"Are you sure you want to delete the record for:\n\n"
        f"  {patient_name}  (ID: {patient_id})\n\n"
        f"This action cannot be undone."
    )
    if not confirmed:
        return False

    try:
        database.delete_patient(conn, patient_id)
        status_callback(STATUS_DELETED)
        messagebox.showinfo("Deleted", "Patient record deleted successfully.")
        refresh_callback()
        return True
    except RuntimeError as exc:
        messagebox.showerror("Delete Failed", str(exc))
        logging.error("delete_patient failed: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Treeview Population
# ---------------------------------------------------------------------------

def populate_treeview(tree, records):
    """
    Clear and repopulate a ttk.Treeview with patient records.

    Args:
        tree    (ttk.Treeview): The widget to populate.
        records (list):         List of row tuples from database.
    """
    tree.delete(*tree.get_children())
    for index, record in enumerate(records):
        tag = "evenrow" if index % 2 == 0 else "oddrow"
        tree.insert("", tk.END, values=record, tags=(tag,))
    tree.tag_configure("evenrow", background=TREEVIEW_EVEN)
    tree.tag_configure("oddrow",  background=TREEVIEW_ODD)


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def search_patients(field, value, conn, tree, status_callback):
    """
    Search patients by field and repopulate the treeview with results.

    Args:
        field           (str):          Column name to search.
        value           (str):          Search term.
        conn            (Connection):   Active database connection.
        tree            (ttk.Treeview): Widget to update.
        status_callback (callable):     Status bar update function.
    """
    value = value.strip()
    if not value:
        records = database.get_all_patients(conn)
        populate_treeview(tree, records)
        status_callback(f"{len(records)} patient(s) loaded.")
        return

    try:
        records = database.search_patients(conn, field, value)
        populate_treeview(tree, records)
        if records:
            status_callback(f"{len(records)} match(es) found.")
        else:
            status_callback("No matching records found.")
    except (ValueError, Exception) as exc:
        logging.error("search_patients error: %s", exc)
        messagebox.showerror("Search Error", str(exc))


# ---------------------------------------------------------------------------
# Dashboard Statistics
# ---------------------------------------------------------------------------

def get_dashboard_stats(conn):
    """
    Fetch and return dashboard statistics dict from the database.

    Returns:
        dict with keys: total, today, male, female, other, avg_age,
                        next_queue, waiting
    """
    return database.get_statistics(conn)
