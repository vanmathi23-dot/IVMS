import sqlite3
from datetime import datetime


def create_database():
    connection = sqlite3.connect("vehicles.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_number TEXT NOT NULL,
            entry_time TEXT,
            exit_time TEXT
        )
    """)

    connection.commit()
    connection.close()


def vehicle_inside(vehicle_number):
    connection = sqlite3.connect("vehicles.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM vehicles
        WHERE vehicle_number = ?
        AND exit_time IS NULL
    """, (vehicle_number,))

    record = cursor.fetchone()

    connection.close()

    return record is not None


def record_entry(vehicle_number):
    connection = sqlite3.connect("vehicles.db")
    cursor = connection.cursor()

    entry_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO vehicles (vehicle_number, entry_time)
        VALUES (?, ?)
    """, (vehicle_number, entry_time))

    connection.commit()
    connection.close()

    print(f"ENTRY: {vehicle_number} at {entry_time}")


def record_exit(vehicle_number):
    connection = sqlite3.connect("vehicles.db")
    cursor = connection.cursor()

    exit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        UPDATE vehicles
        SET exit_time = ?
        WHERE vehicle_number = ?
        AND exit_time IS NULL
    """, (exit_time, vehicle_number))

    connection.commit()
    connection.close()

    print(f"EXIT: {vehicle_number} at {exit_time}")


def get_all_records():
    connection = sqlite3.connect("vehicles.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM vehicles
        ORDER BY id DESC
    """)

    records = cursor.fetchall()

    connection.close()

    return records