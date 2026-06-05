import sqlite3
import pandas as pd
from datetime import datetime


DB_PATH = "data/health.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets you access columns by name
    return conn


def initialise_db():
    """Create tables if they don't already exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL UNIQUE,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checkins (
            checkin_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER,
            timestamp    TEXT,
            energy_level REAL,
            stress_level REAL,
            heart_rate   REAL,
            mood_text    TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)

    conn.commit()
    conn.close()


def get_or_create_user(name: str) -> int:
    """Return user_id for a name, creating the user if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM users WHERE name = ?", (name,))
    row = cursor.fetchone()

    if row:
        user_id = row["user_id"]
    else:
        cursor.execute(
            "INSERT INTO users (name, created_at) VALUES (?, ?)",
            (name, datetime.now().isoformat())
        )
        conn.commit()
        user_id = cursor.lastrowid

    conn.close()
    return user_id


def save_checkin(user_id: int, energy: float, stress: float, heart_rate: float, mood_text: str):
    """Insert a new check-in row for a user."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO checkins (user_id, timestamp, energy_level, stress_level, heart_rate, mood_text)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, datetime.now().isoformat(), energy, stress, heart_rate, mood_text))

    conn.commit()
    conn.close()


def get_checkins(user_id: int) -> pd.DataFrame:
    """Retrieve all check-ins for a user as a DataFrame."""
    conn = get_connection()

    df = pd.read_sql_query(
        "SELECT * FROM checkins WHERE user_id = ? ORDER BY timestamp",
        conn,
        params=(user_id,)
    )

    conn.close()
    return df

def get_all_users() -> list:
    """Return a list of all usernames in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM users ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return [row["name"] for row in rows]