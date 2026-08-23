import sqlite3

connection = sqlite3.connect("uptimehub.db")

connection.execute("""
ALTER TABLE monitors
ADD COLUMN last_checked TEXT
""")

connection.commit()
connection.close()

print("Database updated successfully.")
