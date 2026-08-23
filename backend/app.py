from flask import Flask, request
import requests
import sqlite3

app = Flask(__name__)

DATABASE = "uptimehub.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


@app.route("/health")
def health():
    return {"status": "ok"}


@app.route("/monitors", methods=["POST"])
def add_monitor():
    data = request.get_json()

    url = data.get("url")

    if not url:
        return {"error": "URL is required"}, 400

    try:
        response = requests.get(url, timeout=5)
        status = "UP" if response.ok else "DOWN"
        status_code = response.status_code

    except requests.RequestException:
        status = "DOWN"
        status_code = None

    connection = get_db_connection()

    cursor = connection.execute(
        """
        INSERT INTO monitors (url, status, status_code)
        VALUES (?, ?, ?)
        """,
        (url, status, status_code)
    )

    connection.commit()

    monitor_id = cursor.lastrowid

    connection.close()

    return {
        "id": monitor_id,
        "url": url,
        "status": status,
        "status_code": status_code
    }, 201


@app.route("/monitors", methods=["GET"])
def get_monitors():
    connection = get_db_connection()

    monitors = connection.execute(
        "SELECT * FROM monitors"
    ).fetchall()

    connection.close()

    return {
        "monitors": [dict(monitor) for monitor in monitors]
    }

@app.route("/monitors/<int:monitor_id>", methods=["GET"])
def get_monitor(monitor_id):
    connection = get_db_connection()

    monitor = connection.execute(
        "SELECT * FROM monitors WHERE id = ?",
        (monitor_id,)
    ).fetchone()

    connection.close()

    if monitor is None:
        return {"error": "Monitor not found"}, 404

    return dict(monitor)

@app.route("/monitors/<int:monitor_id>", methods=["DELETE"])
def delete_monitor(monitor_id):
    connection = get_db_connection()

    cursor = connection.execute(
        "DELETE FROM monitors WHERE id = ?",
        (monitor_id,)
    )

    connection.commit()
    connection.close()

    if cursor.rowcount == 0:
        return {"error": "Monitor not found"}, 404

    return {"message": "Monitor deleted successfully"}

@app.route("/monitors/<int:monitor_id>/history", methods=["GET"])
def get_monitor_history(monitor_id):
    connection = get_db_connection()

    monitor = connection.execute(
        "SELECT id FROM monitors WHERE id = ?",
        (monitor_id,)
    ).fetchone()

    if monitor is None:
        connection.close()
        return {"error": "Monitor not found"}, 404

    history = connection.execute(
        """
        SELECT id, status, status_code, checked_at
        FROM monitor_history
        WHERE monitor_id = ?
        ORDER BY checked_at DESC
        """,
        (monitor_id,)
    ).fetchall()

    connection.close()

    return {
        "monitor_id": monitor_id,
        "history": [dict(record) for record in history]
    }

@app.route("/monitors/<int:monitor_id>/uptime", methods=["GET"])
def get_monitor_uptime(monitor_id):
    connection = get_db_connection()

    history = connection.execute(
        """
        SELECT status
        FROM monitor_history
        WHERE monitor_id = ?
        """,
        (monitor_id,)
    ).fetchall()

    connection.close()

    if not history:
        return {
            "monitor_id": monitor_id,
            "uptime_percentage": 0,
            "total_checks": 0
        }

    total_checks = len(history)
    successful_checks = sum(
        1 for record in history
        if record["status"] == "UP"
    )

    uptime_percentage = (
        successful_checks / total_checks
    ) * 100

    return {
        "monitor_id": monitor_id,
        "uptime_percentage": round(uptime_percentage, 2),
        "total_checks": total_checks,
        "up_checks": successful_checks
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

