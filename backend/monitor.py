import sqlite3
import requests
import time
from datetime import datetime

DATABASE = "uptimehub.db"


def check_monitor(monitor):
    try:
        response = requests.get(monitor["url"], timeout=5)

        status = "UP" if response.ok else "DOWN"
        status_code = response.status_code

    except requests.RequestException:
        status = "DOWN"
        status_code = None

    checked_at = datetime.now().isoformat(timespec="seconds")

    connection = sqlite3.connect(DATABASE)

    connection.execute(
        """
        UPDATE monitors
        SET status = ?, status_code = ?, last_checked = ?
        WHERE id = ?
        """,
        (status, status_code, checked_at, monitor["id"])
    )

    connection.execute(
        """
        INSERT INTO monitor_history
        (monitor_id, status, status_code, checked_at)
        VALUES (?, ?, ?, ?)
        """,
        (monitor["id"], status, status_code, checked_at)
    )

    connection.commit()
    connection.close()

    print(
        f"{monitor['url']} -> {status} "
        f"({status_code}) at {checked_at}"
    )


def check_all_monitors():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    monitors = connection.execute(
        "SELECT * FROM monitors"
    ).fetchall()

    connection.close()

    for monitor in monitors:
        check_monitor(monitor)


while True:
    print("Checking monitors...")
    check_all_monitors()

    time.sleep(60)
