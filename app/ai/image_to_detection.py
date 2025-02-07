import asyncio
import io
import logging
from concurrent.futures import ThreadPoolExecutor
from fastapi import UploadFile
import numpy as np
from PIL import Image
import pytesseract
from ultralytics import YOLO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load YOLO model
yolo8n_model = YOLO('yolov8n.pt')

# yolo8_model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
# yolo5n_model = torch.hub.load('ultralytics/yolo11', 'yolo11n')
# yolo5s_model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
# Model dictionary
models = {'yolo8n': yolo8n_model}

def detect_with_yolo(img_array, model_name='yolo8n'):
    """Run object detection with YOLO model."""
    model = models.get(model_name)
    if not model:
        logger.error(f"Model {model_name} not found")
        return []
    
    results = model(img_array)

    return [
        {
            "object": r.names[int(box.cls)],
            "confidence": float(box.conf),
        }
        for r in results for box in r.boxes
    ]

def extract_text_with_tesseract(image: Image.Image):
    """Extract text using Tesseract OCR."""
    return pytesseract.image_to_string(image)

async def image_to_detection(image_file: UploadFile):
    """Process image for object detection and text extraction concurrently."""
    try:
        logger.info("Starting image processing.")

        # Read image file asynchronously
        contents = await image_file.read()
        image = Image.open(io.BytesIO(contents))

        # Convert PNG with transparency (RGBA) to RGB
        if image.mode == "RGBA":
            image = image.convert("RGB")

        # Convert image to NumPy array for YOLO
        img_array = np.array(image)

        # Run YOLO detection and Tesseract OCR concurrently
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            yolo_task = loop.run_in_executor(pool, detect_with_yolo, img_array, 'yolo8n')
            ocr_task = loop.run_in_executor(pool, extract_text_with_tesseract, image)

            detections, detected_texts = await asyncio.gather(yolo_task, ocr_task)

        return {"detections": detections, "texts": detected_texts}

    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return {"error": str(e)}
