"""
database.py
Data Access Layer — all SQLite interactions are isolated here.
No other module should import sqlite3 directly.
"""

import sqlite3
import os
import logging
import datetime

from constants import DB_PATH, DB_DIR


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

def initialize_database():
    """
    Create the database directory, connect to clinic.db, and ensure the
    patients table and all indexes exist.  Returns the connection object.
    """
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    _create_tables(conn)
    _create_indexes(conn)
    logging.info("Database initialised at %s", DB_PATH)
    return conn


def get_connection():
    """Return a fresh connection to the database (row_factory set)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# Schema helpers (private)
# ---------------------------------------------------------------------------

def _create_tables(conn):
    """Create the patients table if it does not already exist."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id        INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name         TEXT    NOT NULL,
            age               INTEGER NOT NULL,
            gender            TEXT    NOT NULL,
            phone             TEXT    NOT NULL,
            address           TEXT    NOT NULL,
            blood_group       TEXT,
            emergency_contact TEXT,
            illness           TEXT    NOT NULL,
            queue_number      INTEGER NOT NULL UNIQUE,
            registration_date TEXT    NOT NULL
        )
    """)
    conn.commit()


def _create_indexes(conn):
    """Create indexes for commonly searched columns."""
    statements = [
        "CREATE INDEX IF NOT EXISTS idx_full_name  ON patients(full_name)",
        "CREATE INDEX IF NOT EXISTS idx_phone       ON patients(phone)",
        "CREATE INDEX IF NOT EXISTS idx_reg_date    ON patients(registration_date)",
        "CREATE INDEX IF NOT EXISTS idx_illness     ON patients(illness)",
        "CREATE INDEX IF NOT EXISTS idx_queue       ON patients(queue_number)",
    ]
    for stmt in statements:
        conn.execute(stmt)
    conn.commit()


# ---------------------------------------------------------------------------
# Queue Number
# ---------------------------------------------------------------------------

def get_next_queue_number(conn):
    """
    Return the next available queue number (MAX + 1).
    Returns 1 when the table is empty.
    """
    row = conn.execute("SELECT MAX(queue_number) FROM patients").fetchone()
    current_max = row[0]
    return (current_max + 1) if current_max is not None else 1


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

def insert_patient(conn, data):
    """
    Insert a new patient record.
    Raises RuntimeError on integrity or database error.

    Args:
        conn: sqlite3 connection
        data: dict with keys matching all non-id columns
    """
    try:
        conn.execute("""
            INSERT INTO patients
                (full_name, age, gender, phone, address, blood_group,
                 emergency_contact, illness, queue_number, registration_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["full_name"],
            data["age"],
            data["gender"],
            data["phone"],
            data["address"],
            data.get("blood_group", "Unknown"),
            data.get("emergency_contact", ""),
            data["illness"],
            data["queue_number"],
            data["registration_date"],
        ))
        conn.commit()
        logging.info("Inserted patient: %s  Queue #%s", data["full_name"], data["queue_number"])
    except sqlite3.IntegrityError as exc:
        logging.error("IntegrityError inserting patient: %s", exc)
        raise RuntimeError("Queue number conflict. Please try again.") from exc
    except sqlite3.DatabaseError as exc:
        logging.error("DatabaseError inserting patient: %s", exc)
        raise RuntimeError("Database error during insert. Check the log.") from exc


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

def get_all_patients(conn):
    """Return all patient rows ordered by queue_number ascending."""
    rows = conn.execute(
        "SELECT patient_id, full_name, age, gender, phone, blood_group, "
        "illness, queue_number, registration_date FROM patients "
        "ORDER BY queue_number ASC"
    ).fetchall()
    return [tuple(r) for r in rows]


def get_patient_by_id(conn, patient_id):
    """
    Return a single patient dict by primary key, or None if not found.
    """
    row = conn.execute(
        "SELECT * FROM patients WHERE patient_id = ?", (patient_id,)
    ).fetchone()
    return dict(row) if row else None


def search_patients(conn, field, value):
    """
    Search patients by a specific field.

    Args:
        conn: sqlite3 connection
        field: column name string (validated by caller before use)
        value: search value string

    Returns:
        List of tuples matching the treeview column order.
    """
    safe_fields = {
        "patient_id", "full_name", "phone", "illness", "queue_number",
        "gender", "blood_group", "registration_date"
    }
    if field not in safe_fields:
        raise ValueError(f"Search field '{field}' is not allowed.")

    if field in ("patient_id", "queue_number"):
        query = (
            f"SELECT patient_id, full_name, age, gender, phone, blood_group, "
            f"illness, queue_number, registration_date FROM patients "
            f"WHERE {field} = ? ORDER BY queue_number ASC"
        )
        rows = conn.execute(query, (value,)).fetchall()
    else:
        query = (
            f"SELECT patient_id, full_name, age, gender, phone, blood_group, "
            f"illness, queue_number, registration_date FROM patients "
            f"WHERE {field} LIKE ? ORDER BY queue_number ASC"
        )
        rows = conn.execute(query, (f"%{value}%",)).fetchall()

    return [tuple(r) for r in rows]


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

def update_patient(conn, patient_id, data):
    """
    Update an existing patient record by patient_id.
    Raises RuntimeError on failure.
    """
    try:
        conn.execute("""
            UPDATE patients SET
                full_name         = ?,
                age               = ?,
                gender            = ?,
                phone             = ?,
                address           = ?,
                blood_group       = ?,
                emergency_contact = ?,
                illness           = ?
            WHERE patient_id = ?
        """, (
            data["full_name"],
            data["age"],
            data["gender"],
            data["phone"],
            data["address"],
            data.get("blood_group", "Unknown"),
            data.get("emergency_contact", ""),
            data["illness"],
            patient_id,
        ))
        conn.commit()
        logging.info("Updated patient_id=%s", patient_id)
    except sqlite3.DatabaseError as exc:
        logging.error("DatabaseError updating patient %s: %s", patient_id, exc)
        raise RuntimeError("Database error during update. Check the log.") from exc


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

def delete_patient(conn, patient_id):
    """
    Delete a patient record by primary key.
    Raises RuntimeError on failure.
    """
    try:
        conn.execute("DELETE FROM patients WHERE patient_id = ?", (patient_id,))
        conn.commit()
        logging.info("Deleted patient_id=%s", patient_id)
    except sqlite3.DatabaseError as exc:
        logging.error("DatabaseError deleting patient %s: %s", patient_id, exc)
        raise RuntimeError("Database error during delete. Check the log.") from exc


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def get_statistics(conn):
    """
    Return a dict of aggregate statistics for the dashboard.
    Keys: total, today, male, female, other, avg_age, next_queue
    """
    today = datetime.date.today().isoformat()
    total     = conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
    today_cnt = conn.execute(
        "SELECT COUNT(*) FROM patients WHERE registration_date = ?", (today,)
    ).fetchone()[0]
    male   = conn.execute("SELECT COUNT(*) FROM patients WHERE gender='Male'").fetchone()[0]
    female = conn.execute("SELECT COUNT(*) FROM patients WHERE gender='Female'").fetchone()[0]
    other  = conn.execute("SELECT COUNT(*) FROM patients WHERE gender='Other'").fetchone()[0]
    avg_row = conn.execute("SELECT ROUND(AVG(age), 1) FROM patients").fetchone()[0]
    avg_age = avg_row if avg_row is not None else 0.0
    next_q  = get_next_queue_number(conn)

    return {
        "total":      total,
        "today":      today_cnt,
        "male":       male,
        "female":     female,
        "other":      other,
        "avg_age":    avg_age,
        "next_queue": next_q,
        "waiting":    today_cnt,
    }


# ---------------------------------------------------------------------------
# Chart Data
# ---------------------------------------------------------------------------

def get_gender_distribution(conn):
    """Return list of (gender, count) tuples for chart rendering."""
    rows = conn.execute(
        "SELECT gender, COUNT(*) as cnt FROM patients GROUP BY gender ORDER BY cnt DESC"
    ).fetchall()
    return [(r[0], r[1]) for r in rows]


def get_illness_distribution(conn, limit=10):
    """Return list of (illness, count) tuples for the top N illnesses."""
    rows = conn.execute(
        "SELECT illness, COUNT(*) as cnt FROM patients "
        "GROUP BY illness ORDER BY cnt DESC LIMIT ?", (limit,)
    ).fetchall()
    return [(r[0], r[1]) for r in rows]


def get_daily_registrations(conn, days=30):
    """Return list of (date_str, count) tuples for the past N days."""
    rows = conn.execute(
        "SELECT registration_date, COUNT(*) as cnt FROM patients "
        "GROUP BY registration_date ORDER BY registration_date DESC LIMIT ?", (days,)
    ).fetchall()
    return list(reversed([(r[0], r[1]) for r in rows]))


def get_all_patients_full(conn):
    """Return all columns of all patients — used by reports."""
    rows = conn.execute(
        "SELECT patient_id, full_name, age, gender, phone, address, "
        "blood_group, emergency_contact, illness, queue_number, registration_date "
        "FROM patients ORDER BY queue_number ASC"
    ).fetchall()
    return [tuple(r) for r in rows]


def get_today_patients_full(conn):
    """Return all columns for patients registered today — used by daily report."""
    today = datetime.date.today().isoformat()
    rows = conn.execute(
        "SELECT patient_id, full_name, age, gender, phone, address, "
        "blood_group, emergency_contact, illness, queue_number, registration_date "
        "FROM patients WHERE registration_date = ? ORDER BY queue_number ASC", (today,)
    ).fetchall()
    return [tuple(r) for r in rows]
