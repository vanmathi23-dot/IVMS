from ultralytics import YOLO
import cv2
import easyocr
import re
import sqlite3
from openpyxl import Workbook

from database import (
    create_database,
    record_entry,
    record_exit,
    vehicle_inside,
    get_all_records
)


# ==========================================
# EXCEL EXPORT
# ==========================================

def export_to_excel():

    connection = sqlite3.connect("vehicles.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, vehicle_number, entry_time, exit_time
        FROM vehicles
        ORDER BY id
    """)

    records = cursor.fetchall()
    connection.close()

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Vehicle Records"

    sheet.append([
        "S.No",
        "Vehicle Number",
        "Entry Time",
        "Exit Time"
    ])

    for record in records:
        sheet.append(record)

    workbook.save("vehicle_records.xlsx")

    print("\nExcel report updated successfully!")
    print(f"Total records: {len(records)}")


# ==========================================
# CHECK WHETHER TEXT LOOKS LIKE A PLATE
# ==========================================

def is_valid_plate(text):

    text = re.sub(r"[^A-Z0-9]", "", text.upper())

    rejected_words = [
        "TRANSPORT",
        "NONTRANSPORT",
        "ETCHER",
        "MER",
        "NONTRANS"
    ]

    for word in rejected_words:
        if word in text:
            return False

    # Indian registration number pattern
    pattern = r"^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{1,4}$"

    return re.match(pattern, text) is not None


# ==========================================
# CLEAN OCR TEXT
# ==========================================

def clean_plate(text):

    text = text.upper()

    text = re.sub(r"[^A-Z0-9]", "", text)

    return text


# ==========================================
# MAIN SYSTEM
# ==========================================

def main():

    print("========================================")
    print("     CCTV VEHICLE TRACKING SYSTEM")
    print("========================================")

    create_database()

    print("\nDatabase connected successfully.")

    # ======================================
    # LOAD YOLO
    # ======================================

    print("\nLoading YOLO...")

    model = YOLO("yolo11n.pt")

    # ======================================
    # LOAD OCR
    # ======================================

    print("Loading EasyOCR...")

    reader = easyocr.Reader(['en'])

    # ======================================
    # OPEN CCTV VIDEO
    # ======================================

    cap = cv2.VideoCapture("videos/traffic.mp4")

    if not cap.isOpened():

        print("ERROR: Could not open traffic.mp4")

        return

    print("\nCCTV VIDEO + NUMBER PLATE OCR STARTED")
    print("Press Q to stop.")

    # ======================================
    # PLATE TRACKING
    # ======================================

    processed_plates = set()

    # Count repeated OCR readings
    plate_votes = {}

    # ======================================
    # PROCESS VIDEO
    # ======================================

    while True:

        success, frame = cap.read()

        if not success:
            break

        # ==================================
        # VEHICLE DETECTION
        # ==================================

        results = model.track(
            frame,
            persist=True,
            classes=[2, 3, 5, 7]
        )

        annotated_frame = frame.copy()

        # ==================================
        # PROCESS EACH VEHICLE
        # ==================================

        for box in results[0].boxes:

            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0]
            )

            # Keep coordinates inside image
            x1 = max(0, x1)
            y1 = max(0, y1)

            x2 = min(
                frame.shape[1],
                x2
            )

            y2 = min(
                frame.shape[0],
                y2
            )

            vehicle = frame[
                y1:y2,
                x1:x2
            ]

            if vehicle.size == 0:
                continue

            # ==================================
            # SELECT LOWER PART OF VEHICLE
            # ==================================

            height = vehicle.shape[0]

            plate_area = vehicle[
                int(height * 0.50):height,
                :
            ]

            # ==================================
            # OCR
            # ==================================

            ocr_results = reader.readtext(
                plate_area,
                allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
                detail=1
            )

            detected_text = ""

            for result in ocr_results:

                text = result[1]

                confidence = result[2]

                cleaned = clean_plate(text)

                print(
                    f"OCR: {cleaned} | "
                    f"Confidence: {confidence:.2f}"
                )

                # ==================================
                # CONFIDENCE FILTER
                # ==================================

                if confidence >= 0.55 and len(cleaned) >= 8:

                    if is_valid_plate(cleaned):

                        detected_text = cleaned

                        break

            # ==================================
            # DRAW VEHICLE BOX
            # ==================================

            cv2.rectangle(
                annotated_frame,
                (x1, y1),
                (x2, y2),
                (255, 255, 0),
                2
            )

            # ==================================
            # VALID PLATE FOUND
            # ==================================

            if detected_text:

                cv2.putText(
                    annotated_frame,
                    detected_text,
                    (
                        x1,
                        max(30, y1 - 10)
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2
                )

                # ==================================
                # COUNT PLATE VOTES
                # ==================================

                plate_votes[detected_text] = (
                    plate_votes.get(
                        detected_text,
                        0
                    ) + 1
                )

                print(
                    f"PLATE VOTE: {detected_text} "
                    f"({plate_votes[detected_text]}/3)"
                )

                # ==================================
                # ACCEPT AFTER 3 READINGS
                # ==================================

                if (
                    plate_votes[detected_text] >= 3
                    and
                    detected_text not in processed_plates
                ):

                    processed_plates.add(
                        detected_text
                    )

                    print(
                        "\n================================"
                    )

                    print(
                        "CONFIRMED VEHICLE PLATE:",
                        detected_text
                    )

                    print(
                        "================================"
                    )

                    # ==================================
                    # ENTRY / EXIT
                    # ==================================

                    if not vehicle_inside(
                        detected_text
                    ):

                        record_entry(
                            detected_text
                        )

                        print(
                            f"{detected_text} "
                            "ENTERED THE PREMISES."
                        )

                    else:

                        record_exit(
                            detected_text
                        )

                        print(
                            f"{detected_text} "
                            "EXITED THE PREMISES."
                        )

        # ==================================
        # SHOW CCTV WINDOW
        # ==================================

        cv2.imshow(
            "CCTV - Vehicle + Number Plate",
            annotated_frame
        )

        # Press Q to stop
        if cv2.waitKey(1) & 0xFF == ord("q"):

            break

    # ======================================
    # CLOSE VIDEO
    # ======================================

    cap.release()

    cv2.destroyAllWindows()

    # ======================================
    # DISPLAY DATABASE RECORDS
    # ======================================

    print("\n========================================")
    print("           VEHICLE RECORDS")
    print("========================================")

    records = get_all_records()

    for record in records:

        print(record)

    # ======================================
    # EXPORT TO EXCEL
    # ======================================

    export_to_excel()

    # ======================================
    # FINISHED
    # ======================================

    print("\n========================================")
    print("       CCTV PROCESSING FINISHED")
    print("========================================")


# ==========================================
# START PROGRAM
# ==========================================

if __name__ == "__main__":

    main()