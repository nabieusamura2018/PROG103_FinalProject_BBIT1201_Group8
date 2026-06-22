"""
validation.py
Input validation module.  All validation logic lives here so that gui.py
and functions.py stay free of inline validation code.
"""

from constants import GENDER_OPTIONS, BLOOD_GROUPS


def validate_patient_data(data):
    """
    Validate a patient registration / update data dictionary.

    Args:
        data (dict): keys matching patient form fields.

    Returns:
        tuple: (bool is_valid, str error_message).
               Returns (True, '') when all checks pass.
    """
    # Required text fields
    required = {
        "full_name": "Full Name",
        "gender":    "Gender",
        "phone":     "Phone Number",
        "address":   "Address",
        "illness":   "Illness / Complaint",
    }
    for field, label in required.items():
        if not str(data.get(field, "")).strip():
            return False, f"{label} is required."

    # Age — required, numeric, sensible range
    age_str = str(data.get("age", "")).strip()
    if not age_str:
        return False, "Age is required."
    if not age_str.isdigit():
        return False, "Age must be a whole number (digits only)."
    age = int(age_str)
    if age < 1 or age > 150:
        return False, "Age must be between 1 and 150."

    # Gender — must be from allowed list
    if data["gender"] not in GENDER_OPTIONS:
        return False, f"Gender must be one of: {', '.join(GENDER_OPTIONS)}."

    # Phone — digits only, minimum 7 characters
    phone = str(data.get("phone", "")).strip()
    if not phone.isdigit():
        return False, "Phone number must contain digits only (no spaces or dashes)."
    if len(phone) < 7:
        return False, "Phone number must be at least 7 digits."

    # Emergency contact — optional, but must be digits if provided
    ec = str(data.get("emergency_contact", "")).strip()
    if ec and not ec.isdigit():
        return False, "Emergency contact must contain digits only."

    return True, ""


def validate_login(username, password):
    """
    Basic login field validation (non-empty check only).

    Returns:
        tuple: (bool is_valid, str error_message)
    """
    if not username.strip():
        return False, "Username is required."
    if not password.strip():
        return False, "Password is required."
    return True, ""


def sanitize_text(value):
    """Strip leading/trailing whitespace from a string value."""
    return str(value).strip()


def is_positive_integer(value):
    """Return True if value is a string representing a positive integer."""
    s = str(value).strip()
    return s.isdigit() and int(s) > 0
