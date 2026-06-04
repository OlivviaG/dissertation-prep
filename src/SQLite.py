import sqlite3
import pandas as pd

# Connect (creates the file if it doesn't exist)
conn = sqlite3.connect("test_health.db")
cursor = conn.cursor()

# Create tables
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name      TEXT NOT NULL,
        created_at TEXT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS checkins (
        checkin_id    INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id       INTEGER,
        timestamp     TEXT,
        energy_level  REAL,
        stress_level  REAL,
        heart_rate    REAL,
        mood_text     TEXT,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
""")

conn.commit()  # <-- Don't forget this. Nothing saves without it.

# Insert a user
cursor.execute(
    "INSERT INTO users (name, created_at) VALUES (?, ?)",
    ("Oliwia", "2026-06-03")  # ? placeholders = safe, no SQL injection
)
conn.commit()

# Insert a check-in
cursor.execute(
    "INSERT INTO checkins (user_id, timestamp, energy_level, stress_level, heart_rate, mood_text) VALUES (?, ?, ?, ?, ?, ?)",
    (1, "2026-06-03", 7.5, 4.0, 72.0, "Feeling okay today")
)
conn.commit()

# Read it back into a DataFrame
df = pd.read_sql_query("SELECT * FROM checkins WHERE user_id = 1", conn)
print(df)

conn.close()