from flask import Flask, render_template, redirect, send_file
import sqlite3
import subprocess
import os

app = Flask(__name__)

print("TEMPLATE FOLDER:", app.template_folder)
print("SERVER FILE:", os.path.abspath(__file__))

DB_FILE = "vehicles.db"
EXCEL_FILE = "vehicle_records.xlsx"


# ==========================================
# DATABASE
# ==========================================

def get_records():
    if not os.path.exists(DB_FILE):
        return []

    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, vehicle_number, entry_time, exit_time
        FROM vehicles
        ORDER BY id DESC
    """)

    records = cursor.fetchall()
    connection.close()

    return records


# ==========================================
# DASHBOARD
# ==========================================

@app.route("/")
def dashboard():

    records = get_records()

    total_vehicles = len(records)

    currently_inside = sum(
        1 for record in records
        if record[3] is None
    )

    vehicles_exited = sum(
        1 for record in records
        if record[3] is not None
    )

    return render_template(
        "dashboard.html",
        total_vehicles=total_vehicles,
        currently_inside=currently_inside,
        vehicles_exited=vehicles_exited,
        records=records
    )


# ==========================================
# START CCTV
# ==========================================

@app.route("/start", methods=["POST"])
def start_cctv():

    try:
        subprocess.Popen(
            ["python", "main.py"],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    except Exception as e:
        print("Error starting CCTV:", e)

    return redirect("/")


# ==========================================
# STOP CCTV
# ==========================================

@app.route("/stop", methods=["POST"])
def stop_cctv():

    try:
        subprocess.run(
            ["taskkill", "/F", "/IM", "python.exe"],
            capture_output=True
        )
    except Exception as e:
        print("Error stopping CCTV:", e)

    return redirect("/")


# ==========================================
# EXPORT TO EXCEL
# ==========================================

@app.route("/export")
def export_excel():

    if os.path.exists(EXCEL_FILE):
        return send_file(
            EXCEL_FILE,
            as_attachment=True
        )

    return redirect("/")


# ==========================================
# RUN SERVER
# ==========================================

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )