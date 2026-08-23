import sqlite3

connection = sqlite3.connect("uptimehub.db")

connection.execute("""
CREATE TABLE IF NOT EXISTS monitors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    status TEXT,
    status_code INTEGER
)
""")

connection.commit()
connection.close()

print("Database initialized successfully.")
