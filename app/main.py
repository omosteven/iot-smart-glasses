import time
from utils.camera import capture_frame, capture_frame_picamera2, save_frame_as_jpg
from utils.api_client import send_image_to_api
from utils.sound import speak_text

texts = ["Hello", "Hi Steven", "This thing must work", "Hello, this is a test on Raspberry Pi."]
def main():
    print("Starting real-time text extraction...")
    
    # for tt in texts:
    #     speak_text(tt)
    # return
    while True:
        try:
            # frame = capture_frame()
            frame = capture_frame_picamera2()
            image_path = save_frame_as_jpg(frame)
            response = send_image_to_api(image_path)
            print(f"Response: {response}")
                        # Validate response structure
            if not isinstance(response, dict) or "data" not in response:
                print("Error: Unexpected response format")
                continue

            data = response.get("data", {})
            detections = data.get("detections", [])
            text = data.get("text", "").strip()

            # Handle detections
            texts = ""
            if isinstance(detections, list) and detections:
                print("Detections:")

                for detection in detections:
                    if isinstance(detection, dict) and "object" in detection:
                        print(f"found - {detection['object']}")
                        text+= f"{detection['object']} , "
                    else:
                        print("Error: Invalid detection format")
            else:
                print("No detections")

            # Handle text output
            if text:
                print(f"Extracted Text: {text}")
                texts+= f" and text in front is {text}"
            else:
                print("No extracted text")
                texts+= "and no text"
            if(len(texts)>1):
                speak_text(f"I found {texts} at the front")
            else:
                speak_text("Nothing was found")
            # Add logic for breaking the loop (e.g., press 'q' to exit)
            time.sleep(1)  # Delay for real-time responsiveness
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    main()
