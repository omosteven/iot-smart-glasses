import cv2
from picamera2 import Picamera2

def capture_frame():
    camera = cv2.VideoCapture(0)  # Use camera index 0
    ret, frame = camera.read()
    camera.release()
    if not ret:
        raise ValueError("Failed to capture image from the camera")
    return frame

def capture_frame_picamera2():
    try:
        picam2 = Picamera2()
        picam2.configure(picam2.create_still_configuration())
        picam2.start()
        frame = picam2.capture_array()
        picam2.stop()

        # Resize to reduce the image size
        resized_frame = cv2.resize(frame, (1024, 576))
        return resized_frame
    except Exception as e:
        print(f"Camera error: {e}")
        raise

def save_frame_as_jpg(frame, file_path="frame.jpg"):
    cv2.imwrite(file_path, frame)
    return file_path
