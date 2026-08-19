import cv2
import easyocr

image = cv2.imread("test_vehicle.png")

if image is None:
    print("ERROR: Could not find test_vehicle.png")
    exit()

# Crop the number plate
plate = image[315:375, 130:290]

# Save crop for checking
cv2.imwrite("plate_crop.png", plate)

reader = easyocr.Reader(['en'])

results = reader.readtext(plate)

print("\n========== NUMBER PLATE OCR ==========")

for result in results:
    text = result[1]
    confidence = result[2]

    print(f"Detected: {text}")
    print(f"Confidence: {confidence:.2f}")
    print("--------------------------------")