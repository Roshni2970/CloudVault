from flask import Flask, render_template, jsonify, request
import os
import glob
import time
import psycopg2
from datetime import datetime

app = Flask(__name__)

BACKUP_DIR = "/backups"


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "db"),
        user=os.getenv("POSTGRES_USER", "cloudvault"),
        password=os.getenv("POSTGRES_PASSWORD", "cloudvault123"),
        dbname=os.getenv("POSTGRES_DB", "cloudvault")
    )


def database_status():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1;")
        cursor.fetchone()
        cursor.close()
        connection.close()
        return True
    except Exception:
        return False


def get_backups():
    files = glob.glob(os.path.join(BACKUP_DIR, "*.sql.gz"))

    backups = []

    for file_path in files:
        filename = os.path.basename(file_path)

        try:
            size = os.path.getsize(file_path)
            modified = os.path.getmtime(file_path)

            backups.append({
                "filename": filename,
                "size": format_size(size),
                "timestamp": datetime.fromtimestamp(modified).strftime(
                    "%d %b %Y, %I:%M %p"
                )
            })

        except OSError:
            continue

    backups.sort(
        key=lambda x: os.path.getmtime(
            os.path.join(BACKUP_DIR, x["filename"])
        ),
        reverse=True
    )

    return backups


def format_size(size):
    if size < 1024:
        return f"{size} B"

    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"

    if size < 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"

    return f"{size / (1024 * 1024 * 1024):.2f} GB"


@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/status")
def status():
    backups = get_backups()

    return jsonify({
        "database": database_status(),
        "backup_count": len(backups),
        "backups": backups[:5]
    })


@app.route("/api/backups")
def backups():
    return jsonify(get_backups())


@app.route("/api/backup", methods=["POST"])
def create_backup():
    try:
        trigger_file = os.path.join(
            BACKUP_DIR,
            ".backup_now"
        )

        with open(trigger_file, "w") as file:
            file.write(str(time.time()))

        return jsonify({
            "success": True,
            "message": "Backup request sent to backup worker."
        })

    except Exception as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


@app.route("/api/restore", methods=["POST"])
def restore_backup():
    data = request.get_json()

    filename = data.get("filename")

    if not filename:
        return jsonify({
            "success": False,
            "message": "Backup filename is required."
        }), 400

    # Prevent path traversal
    if os.path.basename(filename) != filename:
        return jsonify({
            "success": False,
            "message": "Invalid backup filename."
        }), 400

    backup_file = os.path.join(BACKUP_DIR, filename)

    if not os.path.exists(backup_file):
        return jsonify({
            "success": False,
            "message": "Backup file not found."
        }), 404

    try:
        trigger_file = os.path.join(
            BACKUP_DIR,
            ".restore_" + filename
        )

        with open(trigger_file, "w") as file:
            file.write(str(time.time()))

        return jsonify({
            "success": True,
            "message": f"Restore request sent for {filename}."
        })

    except Exception as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


@app.route("/api/demo-data", methods=["POST"])
def create_demo_data():

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS demo_data (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                course VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cursor.execute("""
            INSERT INTO demo_data (name, course)
            VALUES (%s, %s);
        """, ("Roshni", "Computer Science"))

        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({
            "success": True,
            "message": "Demo data added successfully."
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


@app.route("/api/demo-data")
def get_demo_data():

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, name, course, created_at
            FROM demo_data
            ORDER BY id DESC;
        """)

        rows = cursor.fetchall()

        data = []

        for row in rows:
            data.append({
                "id": row[0],
                "name": row[1],
                "course": row[2],
                "created_at": row[3].strftime("%d %b %Y %I:%M %p")
            })

        cursor.close()
        connection.close()

        return jsonify(data)

    except Exception as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


@app.route("/api/delete-demo-data", methods=["POST"])
def delete_demo_data():

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("DROP TABLE IF EXISTS demo_data;")

        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({
            "success": True,
            "message": "Demo data deleted."
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )