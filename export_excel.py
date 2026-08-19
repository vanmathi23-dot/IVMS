import sqlite3
from openpyxl import Workbook

# Connect to database
connection = sqlite3.connect("vehicles.db")
cursor = connection.cursor()

# Get all vehicle records
cursor.execute("""
    SELECT id, vehicle_number, entry_time, exit_time
    FROM vehicles
    ORDER BY id
""")

records = cursor.fetchall()

connection.close()

# Create Excel workbook
workbook = Workbook()
sheet = workbook.active
sheet.title = "Vehicle Records"

# Headers
sheet.append([
    "S.No",
    "Vehicle Number",
    "Entry Time",
    "Exit Time"
])

# Add records
for record in records:
    sheet.append(record)

# Save Excel file
workbook.save("vehicle_records.xlsx")

print("================================")
print("EXCEL FILE CREATED SUCCESSFULLY")
print("================================")
print(f"Total records exported: {len(records)}")
print("File: vehicle_records.xlsx")