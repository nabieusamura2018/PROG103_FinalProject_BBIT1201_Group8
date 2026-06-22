# Community Health Clinic Queue Management System

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![SDG 3](https://img.shields.io/badge/SDG-3%20Good%20Health-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

A professional desktop application that digitises patient registration and
queue management for community health clinics in Sierra Leone.

Developed as a group project for the **Principles of Structured Programming** course.

---

## Features

- Animated splash screen and professional login with live clock
- Dashboard with real-time statistics cards
- Patient registration with auto-generated queue numbers
- Full CRUD — register, view, search, update, delete
- Live search across Name, Phone, Illness, Queue #, Patient ID
- CSV export and daily reports
- Print preview window
- Matplotlib charts: Gender Pie, Illness Bar, Daily Line
- Light / Dark theme toggle
- Database backup and restore
- Logging to `clinic_system.log`

## Installation

```bash
# 1. Clone or download the project
cd Community_Clinic_System

# 2. Create a virtual environment (recommended)
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python main.py
```

**Default login:** `admin` / `admin123`

## Project Structure

```
Community_Clinic_System/
├── main.py          Entry point
├── splash.py        Animated splash screen
├── login.py         Authentication
├── gui.py           Dashboard & all views
├── database.py      SQLite data access layer
├── functions.py     Business logic
├── validation.py    Input validation
├── reports.py       CSV export & print preview
├── charts.py        Matplotlib charts
├── settings.py      Theme & preferences
├── constants.py     App-wide constants
├── assets/          logo.png, hospital.ico
├── database/        clinic.db (auto-created)
├── exports/         CSV output files
├── documentation/   PROJECT_DOCUMENTATION.md
├── requirements.txt
├── LICENSE
└── README.md
```

## Requirements

- Python 3.8+
- pip packages: `tkcalendar`, `matplotlib`, `Pillow`
- All other imports are Python standard library

## SDG Alignment

This project supports **SDG 3: Good Health and Well-being** by digitising
clinic operations, reducing patient wait times, enabling data-driven health
decisions, and protecting records from physical damage.

## License

MIT — see LICENSE file.
