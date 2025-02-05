import time
# from utils.camera import capture_frame, capture_frame_picamera2, save_frame_as_jpg
from utils.api_client import send_image_to_api
from utils.sound import speak_text

texts = ["Hello", "Hi Steven", "This thing must work", "Hello, this is a test on Raspberry Pi."]
def main():
    print("Starting real-time text extraction...")
    
    for tt in texts:
        speak_text(tt)
    return
    while True:
        try:
            # frame = capture_frame()
            frame = capture_frame_picamera2()
            image_path = save_frame_as_jpg(frame)
            response = send_image_to_api(image_path)
            print(f"Response: {response}")
            
            # Add logic for breaking the loop (e.g., press 'q' to exit)
            time.sleep(1)  # Delay for real-time responsiveness
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    main()
