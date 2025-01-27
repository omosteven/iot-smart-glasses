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
        # Initialize and configure the camera
        picam2 = Picamera2()
        camera_info = picam2.sensor_modes
        for mode in camera_info:
            print('each mode',mode)
            
        picam2.configure(picam2.create_still_configuration())
        picam2.start()
        time.sleep(1)  # Allow the camera to warm up

        # Capture the frame
        frame = picam2.capture_array()

        # Properly stop the camera after capturing
        picam2.stop()
        return frame
    except Exception as e:
        print(f"Camera error: {e}")
        raise
    finally:
        # Ensure cleanup
        if "picam2" in locals():
            try:
                picam2.close()
            except:
                pass

def save_frame_as_jpg(frame, file_path="frame.jpg"):
    # cv2.imwrite(file_path, frame)
    # return file_path
    # resized_frame = cv2.resize(frame, (1024, 576))
    # # Save as JPEG
    # cv2.imwrite(file_path, resized_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])  # Adjust quality as needed
    # return file_path
    cv2.imwrite(file_path, frame)
    return file_path
