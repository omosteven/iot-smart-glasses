import time
import asyncio
import pyttsx3
import cv2
from concurrent.futures import ThreadPoolExecutor
from picamera2 import Picamera2
from utils.api_client import send_image_to_api

# Initialize global queue for speech text
speech_queue = asyncio.Queue()
frame_queue = asyncio.Queue()

# Initialize pyttsx3 engine once
engine = pyttsx3.init()
engine.setProperty('rate', 130)  # Adjust speed for better clarity
engine.setProperty('volume', 1.0)  # Ensure max volume
voices = engine.getProperty('voices')
if voices:
    engine.setProperty('voice', voices[0].id)

# ThreadPoolExecutor for blocking tasks
executor = ThreadPoolExecutor()

# Keep camera initialized
picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())
picam2.start()
time.sleep(1)  # Warm-up time

def capture_frame():
    """ Capture a frame without re-initializing the camera """
    try:
        return picam2.capture_array()
    except Exception as e:
        print(f"Camera error: {e}")
        return None

def save_frame_as_jpg(frame, file_path="frame.jpg"):
    """ Save the captured frame as a JPEG file """
    if frame is None:
        return None
    resized_frame = cv2.resize(frame, (640, 640))
    cv2.imwrite(file_path, resized_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
    return file_path

def speak_text(text: str):
    """ Speak text using pyttsx3 in a separate thread """
    if text.strip():
        engine.say(text)
        engine.runAndWait()

async def speech_worker():
    """ Background task to process speech queue """
    while True:
        text = await speech_queue.get()
        future = executor.submit(speak_text, text)
        while engine.isBusy():
            await asyncio.sleep(0.1)
        speech_queue.task_done()

async def capture_worker():
    """ Continuously capture frames and store in queue """
    while True:
        frame = await asyncio.get_running_loop().run_in_executor(executor, capture_frame)
        if frame is not None:
            await frame_queue.put(frame)
        await asyncio.sleep(0.1)  # Small delay to prevent overload

async def process_worker():
    """ Process frames from queue: save, send to API, and handle response """
    while True:
        frame = await frame_queue.get()
        loop = asyncio.get_running_loop()

        # Save frame asynchronously
        image_path = await loop.run_in_executor(executor, save_frame_as_jpg, frame)
        if not image_path:
            frame_queue.task_done()
            continue

        # Send image to API asynchronously
        response = await loop.run_in_executor(executor, send_image_to_api, image_path)

        # Validate response
        if not isinstance(response, dict) or "data" not in response:
            print("Error: Unexpected response format")
            frame_queue.task_done()
            continue

        data = response.get("data", {})
        detections = data.get("detections", [])
        text = data.get("text", "").strip()

        detected_objects = [d["object"] for d in detections if isinstance(d, dict) and "object" in d]
        spoken_text = "I found " + (", ".join(detected_objects) if detected_objects else "nothing")
        spoken_text += f" and the text in front is {text}" if text else " and no text"

        await speech_queue.put(spoken_text)
        frame_queue.task_done()

async def main():
    """ Main async function to start all background tasks """
    print("Starting real-time processing...")

    # Start workers
    asyncio.create_task(speech_worker())
    asyncio.create_task(capture_worker())
    asyncio.create_task(process_worker())

    while True:
        await asyncio.sleep(1)  # Keep loop alive

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopping...")
        picam2.stop()
