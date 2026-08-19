import cv2
import easyocr


class NumberPlateReader:

    def __init__(self):
        self.reader = easyocr.Reader(['en'])

    def read_plate(self, plate_image):

        # Convert image to grayscale
        gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)

        # Improve the image
        gray = cv2.resize(gray, None, fx=2, fy=2)

        # Read text from number plate
        results = self.reader.readtext(gray)

        if results:
            text = results[0][1]

            # Remove unwanted spaces
            text = text.replace(" ", "").upper()

            return text

        return None