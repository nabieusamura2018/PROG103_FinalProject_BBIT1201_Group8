"""
constants.py
Application-wide constants for the Community Health Clinic Queue Management System.
No hardcoded values should appear in any other module.
"""

# ---------------------------------------------------------------------------
# Application Identity
# ---------------------------------------------------------------------------
APP_TITLE    = "Community Health Clinic Queue Management System"
APP_SUBTITLE = "Serving Health, Saving Lives"
APP_VERSION  = "1.0.0"
COURSE_TITLE = "Principles of Structured Programming"
DEVELOPER    = "Group Project — 2026"
SDG_NOTE     = "Aligned with SDG 3: Good Health and Well-being"

# ---------------------------------------------------------------------------
# Authentication (single-admin phase)
# ---------------------------------------------------------------------------
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin123"

# ---------------------------------------------------------------------------
# File Paths
# ---------------------------------------------------------------------------
DB_DIR      = "database"
DB_PATH     = "database/clinic.db"
EXPORTS_DIR = "exports"
ASSETS_DIR  = "assets"
LOG_FILE    = "clinic_system.log"
SETTINGS_FILE = "settings.json"

# ---------------------------------------------------------------------------
# Colour Palette — Light Theme
# ---------------------------------------------------------------------------
PRIMARY_BLUE    = "#1565C0"
SECONDARY_BLUE  = "#1976D2"
ACCENT_BLUE     = "#42A5F5"
LIGHT_BLUE_BG   = "#E3F2FD"
WHITE           = "#FFFFFF"
LIGHT_GRAY      = "#F5F5F5"
MID_GRAY        = "#E0E0E0"
CARD_BG         = "#FFFFFF"
SUCCESS_GREEN   = "#2E7D32"
SUCCESS_LIGHT   = "#E8F5E9"
WARNING_AMBER   = "#F57F17"
WARNING_LIGHT   = "#FFF8E1"
ERROR_RED       = "#C62828"
ERROR_LIGHT     = "#FFEBEE"
TEXT_DARK       = "#212121"
TEXT_MEDIUM     = "#616161"
TEXT_LIGHT      = "#9E9E9E"
SIDEBAR_BG      = "#1565C0"
SIDEBAR_HOVER   = "#1976D2"
SIDEBAR_ACTIVE  = "#0D47A1"
HEADER_BG       = "#1565C0"
HEADER_FG       = "#FFFFFF"
STATUS_BG       = "#E3F2FD"
STATUS_FG       = "#1565C0"
TREEVIEW_ODD    = "#FFFFFF"
TREEVIEW_EVEN   = "#EEF4FB"
TREEVIEW_SELECT = "#BBDEFB"

# ---------------------------------------------------------------------------
# Colour Palette — Dark Theme
# ---------------------------------------------------------------------------
DARK_BG         = "#1E1E1E"
DARK_CARD       = "#2D2D2D"
DARK_SIDEBAR    = "#0D1117"
DARK_HEADER     = "#0D1117"
DARK_TEXT       = "#E0E0E0"
DARK_TEXT_MED   = "#9E9E9E"
DARK_BORDER     = "#3A3A3A"
DARK_INPUT      = "#3A3A3A"
DARK_ODD        = "#2D2D2D"
DARK_EVEN       = "#252525"
DARK_SELECT     = "#1A3A5C"

# ---------------------------------------------------------------------------
# Typography
# ---------------------------------------------------------------------------
FONT_FAMILY        = "Segoe UI"
FONT_SIZE_SMALL    = 9
FONT_SIZE_NORMAL   = 11
FONT_SIZE_MEDIUM   = 12
FONT_SIZE_LARGE    = 14
FONT_SIZE_TITLE    = 18
FONT_SIZE_HEADER   = 22

FONT_NORMAL  = (FONT_FAMILY, FONT_SIZE_NORMAL)
FONT_BOLD    = (FONT_FAMILY, FONT_SIZE_NORMAL, "bold")
FONT_MEDIUM  = (FONT_FAMILY, FONT_SIZE_MEDIUM)
FONT_MEDIUM_BOLD = (FONT_FAMILY, FONT_SIZE_MEDIUM, "bold")
FONT_LARGE   = (FONT_FAMILY, FONT_SIZE_LARGE)
FONT_LARGE_BOLD  = (FONT_FAMILY, FONT_SIZE_LARGE, "bold")
FONT_TITLE   = (FONT_FAMILY, FONT_SIZE_TITLE, "bold")
FONT_HEADER  = (FONT_FAMILY, FONT_SIZE_HEADER, "bold")
FONT_SMALL   = (FONT_FAMILY, FONT_SIZE_SMALL)

# ---------------------------------------------------------------------------
# Patient Form Options
# ---------------------------------------------------------------------------
GENDER_OPTIONS = ["Male", "Female", "Other"]
BLOOD_GROUPS   = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"]

ILLNESS_SUGGESTIONS = [
    "Malaria", "Typhoid", "Fever", "Cough", "Diarrhoea", "Hypertension",
    "Diabetes", "Anaemia", "Pneumonia", "Tuberculosis", "Cholera",
    "Measles", "Hepatitis", "HIV/AIDS", "Skin Infection", "Eye Infection",
    "Ear Infection", "Stomach Pain", "Headache", "Injury/Trauma", "Other"
]

# ---------------------------------------------------------------------------
# Treeview Columns for Patient Records
# ---------------------------------------------------------------------------
TREE_COLUMNS = (
    "patient_id", "full_name", "age", "gender",
    "phone", "blood_group", "illness", "queue_number", "registration_date"
)
TREE_HEADINGS = (
    "ID", "Full Name", "Age", "Gender",
    "Phone", "Blood Group", "Illness", "Queue #", "Date"
)
TREE_WIDTHS = (55, 180, 45, 70, 110, 85, 180, 65, 100)
TREE_ANCHORS = ("center", "w", "center", "center", "w", "center", "w", "center", "center")

# ---------------------------------------------------------------------------
# Status Messages
# ---------------------------------------------------------------------------
STATUS_READY      = "Ready"
STATUS_CONNECTED  = "Connected to clinic.db"
STATUS_REGISTERED = "Patient registered successfully."
STATUS_UPDATED    = "Patient record updated successfully."
STATUS_DELETED    = "Patient record deleted."
STATUS_EXPORTED   = "Export complete."
STATUS_BACKUP     = "Database backup complete."
STATUS_RESTORED   = "Database restored successfully."
STATUS_SEARCHING  = "Searching..."
STATUS_NO_RESULTS = "No matching records found."

# ---------------------------------------------------------------------------
# Window Dimensions
# ---------------------------------------------------------------------------
SPLASH_W   = 520
SPLASH_H   = 380
LOGIN_W    = 460
LOGIN_H    = 560
MAIN_W     = 1200
MAIN_H     = 720
SIDEBAR_W  = 200
