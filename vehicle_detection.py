from ultralytics import YOLO
import cv2


class VehicleDetector:

    def __init__(self):
        self.model = YOLO("yolo11n.pt")

    def process_video(self, video_path):

        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print("ERROR: Could not open video.")
            return

        while True:

            success, frame = cap.read()

            if not success:
                break

            results = self.model.track(
                frame,
                persist=True,
                classes=[2, 3, 5, 7]
            )

            annotated_frame = results[0].plot()

            cv2.imshow(
                "CCTV Vehicle Detection",
                annotated_frame
            )

            # Press Q to stop
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()