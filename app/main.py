import time
import asyncio
import pyttsx3
import cv2
from concurrent.futures import ThreadPoolExecutor
from picamera2 import Picamera2
from utils.api_client import send_image_to_api

# Global queues for speech and frames
speech_queue = asyncio.Queue(maxsize=5)  # Prevent excessive memory usage
frame_queue = asyncio.Queue(maxsize=1)   # Only process one frame at a time

# Initialize pyttsx3 once
engine = pyttsx3.init()
engine.setProperty('rate', 130)
engine.setProperty('volume', 1.0)
voices = engine.getProperty('voices')
if voices:
    engine.setProperty('voice', voices[0].id)

# ThreadPoolExecutor for blocking tasks
executor = ThreadPoolExecutor(max_workers=3)

# Keep camera initialized
picam2 = Picamera2()
camera_config = picam2.create_still_configuration({"size": (4608, 2592)})  # Max res for Camera 3
picam2.configure(camera_config)
# picam2.configure(picam2.create_still_configuration({"size": (640, 640)}))  # Reduce resolution
picam2.set_controls({
    "AfMode": 1,          # Enable continuous autofocus
    "ExposureTime": 5000,  # 5ms exposure
    "AnalogueGain": 1.5   # Adjust gain
})

picam2.start()
time.sleep(2)  # Allow warm-up

def capture_frame():
    """ Capture a frame and save it without re-initializing the camera """
    try:
        image_path = "/tmp/frame.jpg"  # Use tmp directory to reduce disk writes
        picam2.set_controls({"AfTrigger": 0})  # Start autofocus
        time.sleep(0.5)  # Allow focus to adjust
        picam2.set_controls({"AfTrigger": 1})  # Lock focus
        
        # Capture image
        picam2.capture_file(image_path)
        return image_path
    except Exception as e:
        print(f"Camera error: {e}")
        return None

def speak_text(text: str):
    """ Speak text using pyttsx3 (blocking task) """
    if text.strip():
        engine.say(text)
        engine.runAndWait()

async def speech_worker():
    """ Background task for speaking text from queue """
    while True:
        text = await speech_queue.get()
        await asyncio.get_running_loop().run_in_executor(executor, speak_text, text)
        speech_queue.task_done()

async def capture_worker():
    """ Continuously capture frames and store them in the queue """
    while True:
        if frame_queue.full():  
            await asyncio.sleep(1)  # Avoid overloading queue
            continue
        
        frame_path = await asyncio.get_running_loop().run_in_executor(executor, capture_frame)
        if frame_path:
            await frame_queue.put(frame_path)
        await asyncio.sleep(1)  # Limit capture rate

async def process_worker():
    """ Process frames from queue: send to API, process response, queue speech """
    while True:
        frame_path = await frame_queue.get()
        loop = asyncio.get_running_loop()

        # Send image to API asynchronously
        response = await loop.run_in_executor(executor, send_image_to_api, frame_path)

        # Validate response
        if not isinstance(response, dict) or "data" not in response:
            print("Error: Unexpected response format")
            frame_queue.task_done()
            continue

        data = response.get("data", {})
        detections = data.get("detections", [])
        text = data.get("text", "").strip()
        print('resp:', response, 'data:',data)

        detected_objects = [d["object"] for d in detections if isinstance(d, dict) and "object" in d]
        spoken_text = "I found " + (", ".join(detected_objects) if detected_objects else "nothing")
        spoken_text += f" and the text in front is {text}" if text else " and no text"
        print('speaking:', spoken_text)
        if not speech_queue.full():  # Prevent overloading speech queue
            await speech_queue.put(spoken_text)

        frame_queue.task_done()

async def main():
    """ Main async function to start all background tasks """
    print("Starting optimized real-time processing...")

    # Start workers
    # asyncio.create_task(speech_worker())
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
