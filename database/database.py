import os
import sqlite3

try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

DB_CONFIG = {
    "host": os.environ.get("HELMET_DB_HOST", "localhost"),
    "user": os.environ.get("HELMET_DB_USER", "root"),
    "password": os.environ.get("HELMET_DB_PASSWORD", "yourpassword"),
    "database": os.environ.get("HELMET_DB_NAME", "helmet_challan"),
}

SQLITE_PATH = os.path.join(os.path.dirname(__file__), "helmet_challan.db")

CREATE_TABLES_SQL = [
    """
    CREATE TABLE IF NOT EXISTS violations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_number TEXT,
        violation_type TEXT,
        fine_amount INTEGER,
        date_time TEXT,
        image_path TEXT,
        challan_pdf TEXT,
        status TEXT
    )
    """,
]


def init_sqlite_db():
    os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    for sql in CREATE_TABLES_SQL:
        cursor.execute(sql)
    conn.commit()
    cursor.close()
    return conn


def get_db_connection():
    if MYSQL_AVAILABLE and os.environ.get("HELMET_DB_USE_SQLITE", "false").lower() != "true":
        try:
            return mysql.connector.connect(**DB_CONFIG)
        except Exception:
            pass
    return init_sqlite_db()


def insert_violation(
    vehicle_number,
    violation_type,
    fine_amount,
    date_time,
    image_path,
    challan_pdf=None,
    status="UNPAID",
):
    db = get_db_connection()
    if isinstance(db, sqlite3.Connection):
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO violations
            (vehicle_number, violation_type, fine_amount, date_time, image_path, challan_pdf, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (vehicle_number, violation_type, fine_amount, date_time, image_path, challan_pdf, status),
        )
    else:
        cursor = db.cursor()
        cursor.execute(
            """
            INSERT INTO violations
            (vehicle_number, violation_type, fine_amount, date_time, image_path, challan_pdf, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (vehicle_number, violation_type, fine_amount, date_time, image_path, challan_pdf, status),
        )
    db.commit()
    cursor.close()
    db.close()
