from vehicle_detection import VehicleDetector


video_path = "videos/traffic.mp4"

detector = VehicleDetector()

detector.process_video(video_path)