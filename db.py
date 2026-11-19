import sqlite3

DB_PATH = "nabz.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL, age INTEGER, sex TEXT);
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER REFERENCES patients(id),
    received_at TEXT, source TEXT, message_id TEXT,
    image_path TEXT, status TEXT, level TEXT);
CREATE TABLE IF NOT EXISTS test_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER REFERENCES reports(id),
    name TEXT, value REAL, unit TEXT,
    range_low REAL, range_high REAL, level TEXT);
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER REFERENCES reports(id), text TEXT);
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER REFERENCES reports(id), sent_at TEXT);
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY, value TEXT);
"""

# Fictional patients only
PATIENTS = [
    ("Asha Verma", 54, "F"),
    ("Ravi Menon", 67, "M"),
    ("Meera Iyer", 38, "F"),
    ("Karan Shah", 45, "M"),
    ("Fatima Khan", 72, "F"),
]

# Urgency bands: % outside the printed range, plus alert keywords
SETTINGS = {
    "watch_pct": "10",
    "urgent_pct": "30",
    "keywords": "chest pain,breathless,fainted",
}


def get_db():
    # Open the database; rows can be read like dicts
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    # Create tables if missing, then add demo data
    with get_db() as conn:
        conn.executescript(SCHEMA)
    seed()


def seed():
    # Fill patients and settings only if they are empty
    with get_db() as conn:
        if conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO patients (name, age, sex) VALUES (?, ?, ?)", PATIENTS)
        conn.executemany(
            "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
            SETTINGS.items())


def list_patients():
    with get_db() as conn:
        rows = conn.execute("SELECT id, name, age, sex FROM patients ORDER BY id")
        return [dict(r) for r in rows]
