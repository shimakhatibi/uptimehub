import sqlite3

connection = sqlite3.connect("uptimehub.db")

connection.execute("""
CREATE TABLE IF NOT EXISTS monitor_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    monitor_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    status_code INTEGER,
    checked_at TEXT NOT NULL,
    FOREIGN KEY (monitor_id) REFERENCES monitors(id)
)
""")

connection.commit()
connection.close()

print("History table created successfully.")
