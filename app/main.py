import time
import asyncio
import pyttsx3
import cv2
import subprocess
from concurrent.futures import ThreadPoolExecutor
from picamera2 import Picamera2
from utils.api_client import send_image_to_api


def release_camera():
    """Check if /dev/video0 is in use and kill the process using it."""
    try:
        result = subprocess.run(["lsof", "/dev/video0"], capture_output=True, text=True)
        lines = result.stdout.strip().split("\n")

        # Ignore header line, process any remaining lines
        for line in lines[1:]:
            parts = line.split()
            if len(parts) > 1:  
                pid = parts[1]  # PID is the second column
                print(f"Killing process {pid} using /dev/video0...")
                subprocess.run(["sudo", "kill", "-9", pid])
        
        time.sleep(1)  # Give time for process cleanup

    except Exception as e:
        print(f"Error while checking camera process: {e}")

release_camera()
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
camera_config = picam2.create_still_configuration({"size": (640, 640)})  # Max res for Camera 3
# camera_config = picam2.create_still_configuration({"size": (4608, 2592)})  # Max res for Camera 3
picam2.configure(camera_config)
# picam2.configure(picam2.create_still_configuration({"size": (640, 640)}))  # Reduce resolution
picam2.set_controls({
    "AfMode": 1,          # Enable continuous autofocus
    "ExposureTime": 5000,  # 5ms exposure
    "AnalogueGain": 1.5,   # Adjust gain
})

picam2.start()
time.sleep(2)  # Allow warm-up

def rotate_frame(image, angle=45):
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, rotation_matrix, (w, h))
    return rotated


def capture_frame():
    """ Capture a frame and save it without re-initializing the camera """
    try:
        start_time = time.time()
        image_path = "/tmp/frame.jpg"  # Use tmp directory to reduce disk writes
        picam2.set_controls({"AfTrigger": 0})  # Start autofocus
        time.sleep(0.5)  # Allow focus to adjust
        picam2.set_controls({"AfTrigger": 1})  # Lock focus
        
        # Capture image
        # picam2.capture_file(image_path)
        # elapsed = time.time() - start_time
        # print(f"Capturing completed in {elapsed:.2f} sec")
        # return image_path
        image = picam2.capture_array()  # Capture as an array (not file)
        
        # Rotate the captured image
        rotated_image = rotate_frame(image, angle=-135)  # Rotate by 45 degrees (or any angle)

        # Save the rotated image
        cv2.imwrite(image_path, rotated_image)  # Save rotated image to file
        elapsed = time.time() - start_time
        print(f"Capturing and rotating completed in {elapsed:.2f} sec")
        return image_path
    except Exception as e:
        print(f"Camera error: {e}")
        return None

def speak_text(text: str):
    """ Speak text using pyttsx3 (blocking task) """
    if text.strip():
        start_time = time.time()
        engine.say(text)
        engine.runAndWait()
        elapsed = time.time() - start_time
        print(f"Speach completed in {elapsed:.2f} sec")

async def speech_worker():
    """ Background task for speaking text from queue with retry mechanism """
    while True:
        text = await speech_queue.get()
        success = False
        max_retries = 3  # Retry up to 3 times
        
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                await asyncio.get_running_loop().run_in_executor(executor, speak_text, text)
                elapsed = time.time() - start_time
                print(f"Speach processs took {elapsed:.2f} sec")
                success = True
                break  # Exit loop on success
            except Exception as e:
                print(f"Speech synthesis failed (Attempt {attempt + 1}): {e}")
                await asyncio.sleep(1)  # Small delay before retrying
        
        if not success:
            print(f"Skipping speech output after {max_retries} failed attempts: {text}")
        
        speech_queue.task_done()

async def capture_worker():
    """ Continuously capture frames and store them in the queue """
    while True:
        start_time = time.time()
        if frame_queue.full():  
            await asyncio.sleep(0.2)  # Avoid overloading queue
            continue
        
        frame_path = await asyncio.get_running_loop().run_in_executor(executor, capture_frame)
        if frame_path:
            await frame_queue.put(frame_path)
            elapsed = time.time() - start_time
            print(f"Capturing processs took {elapsed:.2f} sec")
        await asyncio.sleep(0.2)  # Limit capture rate

async def process_worker():
    """ Process frames from queue: send to API, process response, queue speech """
    while True:
        frame_path = await frame_queue.get()
        loop = asyncio.get_running_loop()
        spoken_text = ""
        try:
            total_start = time.time()
            api_start = time.time()
            # Send image to API asynchronously
            response = await loop.run_in_executor(executor, send_image_to_api, frame_path)
            api_elapsed = time.time() - api_start
            print(f"API request took {api_elapsed:.2f} sec")
            # Ensure response is a dictionary
            if not isinstance(response, dict):
                raise ValueError("Invalid API response format")

            data = response.get("data", {})

            # Extract text safely
            extracted_text = data.get("texts", "").strip()

            # Extract detections safely
            detections = data.get("detections", [])
            detected_objects = [d.get("object", "") for d in detections if isinstance(d, dict)]

            # Construct spoken message
            spoken_text = "I found " + (", ".join(detected_objects) if detected_objects else "nothing")
            spoken_text += f" and the text in front is: {extracted_text}" if extracted_text else " and no text"
            total_elapsed = time.time()- total_start
            print(f"⏳ Total processing time (Capture → API → Processing): {total_elapsed:.2f} sec")
        except Exception as e:
            print(f"API call error: {e}")
            spoken_text = "An error occurred while making API call."

        print('speaking:', spoken_text)

        if not speech_queue.full():  # Prevent overloading speech queue
            await speech_queue.put(spoken_text)

        frame_queue.task_done()

async def main():
    """ Main async function to start all background tasks """
    print("Starting optimized real-time processing...")

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
