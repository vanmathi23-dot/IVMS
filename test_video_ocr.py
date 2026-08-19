from ultralytics import YOLO
import cv2
import easyocr
import re

# Load YOLO
model = YOLO("yolo11n.pt")

# Load OCR
reader = easyocr.Reader(['en'])

# Open CCTV video
cap = cv2.VideoCapture("videos/traffic.mp4")

if not cap.isOpened():
    print("ERROR: Could not open traffic.mp4")
    exit()

print("CCTV VIDEO + NUMBER PLATE OCR STARTED")
print("Press Q to stop.")

while True:

    success, frame = cap.read()

    if not success:
        break

    # Detect vehicles
    results = model.track(
        frame,
        persist=True,
        classes=[2, 3, 5, 7]
    )

    annotated_frame = frame.copy()

    for box in results[0].boxes:

        x1, y1, x2, y2 = map(int, box.xyxy[0])

        # Make sure coordinates are valid
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(frame.shape[1], x2)
        y2 = min(frame.shape[0], y2)

        vehicle = frame[y1:y2, x1:x2]

        if vehicle.size == 0:
            continue

        # Number plates are usually in the lower part
        height = vehicle.shape[0]

        plate_area = vehicle[int(height * 0.50):height, :]

        # OCR
        ocr_results = reader.readtext(
            plate_area,
            allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
            detail=1
        )

        detected_text = ""

        for result in ocr_results:

            text = result[1].upper()
            confidence = result[2]

            # Remove spaces and symbols
            cleaned = re.sub(r'[^A-Z0-9]', '', text)

            if confidence >= 0.40 and len(cleaned) >= 6:
                detected_text = cleaned
                break

        # Draw vehicle box
        cv2.rectangle(
            annotated_frame,
            (x1, y1),
            (x2, y2),
            (255, 255, 0),
            2
        )

        # Display detected number
        if detected_text:

            cv2.putText(
                annotated_frame,
                detected_text,
                (x1, max(30, y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            print("PLATE:", detected_text)

    cv2.imshow(
        "CCTV - Vehicle + Number Plate",
        annotated_frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

print("CCTV PROCESSING FINISHED")