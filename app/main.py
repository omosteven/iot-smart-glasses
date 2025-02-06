import time
import asyncio
import pyttsx3
from concurrent.futures import ThreadPoolExecutor
from utils.camera import capture_frame_picamera2, save_frame_as_jpg
from utils.api_client import send_image_to_api

# Initialize pyttsx3 engine once
engine = pyttsx3.init()
engine.setProperty('rate', 130)  # Adjust for clarity
engine.setProperty('volume', 1.0)  # Ensure max volume

# Select a clear voice
voices = engine.getProperty('voices')
if voices:
    engine.setProperty('voice', voices[0].id)

# ThreadPoolExecutor for handling blocking calls
executor = ThreadPoolExecutor()

def speak_text(text: str):
    """ Speak text in a separate thread without blocking the main loop """
    if not text.strip():
        return  # Skip empty text
    
    def run_tts():
        engine.say(text)
        engine.runAndWait()

    future = executor.submit(run_tts)
    return future  # Return future to track completion

async def process_frame():
    """ Capture image, send to API, and process detections """
    try:
        # Capture frame and send to API asynchronously
        loop = asyncio.get_running_loop()
        frame = await loop.run_in_executor(executor, capture_frame_picamera2)
        image_path = await loop.run_in_executor(executor, save_frame_as_jpg, frame)
        response = await loop.run_in_executor(executor, send_image_to_api, image_path)

        # Validate response structure
        if not isinstance(response, dict) or "data" not in response:
            print("Error: Unexpected response format")
            return "Error in processing"

        data = response.get("data", {})
        detections = data.get("detections", [])
        text = data.get("text", "").strip()

        # Process detections
        detected_objects = [d["object"] for d in detections if isinstance(d, dict) and "object" in d]

        # Build speech text
        spoken_text = "I found " + (", ".join(detected_objects) if detected_objects else "nothing")
        spoken_text += f" and the text in front is {text}" if text else " and no text"

        return spoken_text

    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred"

async def main():
    """ Main loop to capture, process, and speak text asynchronously """
    print("Starting real-time text extraction...")

    while True:
        try:
            speech_future = None  # Track active speech

            # Capture, process frame, and get response text
            spoken_text = await process_frame()
            print(f"Speaking: {spoken_text}")

            # Speak the response asynchronously
            speech_future = speak_text(spoken_text)

            # Wait for speech to finish before the next cycle
            if speech_future:
                while engine.isBusy():  # Detect when speech is done
                    time.sleep(0.1)

            await asyncio.sleep(1)  # Avoid overwhelming the system

        except Exception as e:
            print(f"Main loop error: {e}")
            break

if __name__ == "__main__":
    asyncio.run(main())
