"""
main.py
Application entry point for the Community Health Clinic Queue Management System.
Bootstraps the database, configures logging, and launches the splash screen.ad
"""

import os
import sys
import logging
import tkinter as tk

# Ensure the project directory is on the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database
from constants import LOG_FILE, APP_TITLE, EXPORTS_DIR, DB_DIR, ASSETS_DIR


def _configure_logging():
    """Set up file and console logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def _ensure_directories():
    """Create required directories if they do not exist."""
    for directory in (DB_DIR, EXPORTS_DIR, ASSETS_DIR):
        os.makedirs(directory, exist_ok=True)


def main():
    """
    Application entry point.
    1. Configure logging.
    2. Create required directories.
    3. Initialise the SQLite database.
    4. Build the hidden root Tk window.
    5. Launch the splash screen.
    """
    _configure_logging()
    _ensure_directories()

    logging.info("=" * 60)
    logging.info("Application starting: %s", APP_TITLE)

    conn = database.initialize_database()

    root = tk.Tk()
    root.withdraw()  # Hidden until login succeeds

    # Import here to avoid circular imports at module level
    from splash import SplashScreen
    from login  import LoginScreen
    from gui    import DashboardApp

    def on_splash_done():
        """Called when splash animation completes."""
        LoginScreen(root, on_success=lambda username: open_dashboard(username))

    def open_dashboard(username):
        """Called after successful authentication."""
        DashboardApp(root, conn, username)

    SplashScreen(root, on_complete=on_splash_done)

    root.mainloop()
    logging.info("Application closed.")


if __name__ == "__main__":
    main()
