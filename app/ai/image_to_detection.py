import asyncio
import io
import logging
from concurrent.futures import ThreadPoolExecutor
from fastapi import UploadFile
import numpy as np
import cv2
from PIL import Image
import pytesseract
import re
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

def preprocess_for_yolo(image: Image.Image):
    """Preprocess image to optimize for YOLO detection."""
    img_array = np.array(image)

    # Resize image to expected input size for YOLO (640x640 is default for YOLOv8n)
    img_array = cv2.resize(img_array, (640, 640))

    # Normalize pixel values (YOLO expects values between 0-1)
    img_array = img_array / 255.0

    return img_array

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



def clean_text(text: str):
    print('actual text:', text)
    """Clean OCR extracted text by removing unwanted characters."""
    text = re.sub(r'[^a-zA-Z0-9,.:\-%\s]', '', text)  # Keep only useful characters
    text = re.sub(r'\s+', ' ', text).strip()  # Normalize spaces
    return text

def needs_preprocessing(image: Image.Image):
    """Determine if the image needs preprocessing based on contrast levels."""
    gray = np.array(image.convert("L"))
    
    # Compute the standard deviation of pixel intensities (contrast indicator)
    contrast = gray.std()

    logger.info(f"Image contrast level: {contrast}")
    print('conr:', contrast)
    # If contrast is below a threshold, apply preprocessing
    return contrast < 30  # Adjust threshold based on testing


def preprocess_image(image: Image.Image):
    """Preprocess image to enhance OCR accuracy."""
    # Convert image to grayscale
    gray = np.array(image.convert("L"))

    # Apply bilateral filtering (removes noise while keeping edges sharp)
    gray = cv2.bilateralFilter(gray, 9, 75, 75)

    # Adaptive thresholding to enhance text contrast
    processed_img = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # Sharpening using an unsharp mask
    blurred = cv2.GaussianBlur(processed_img, (0, 0), 3)
    sharpened = cv2.addWeighted(processed_img, 1.5, blurred, -0.5, 0)

    return Image.fromarray(sharpened)

def extract_text_with_tesseract(image: Image.Image):
    """Extract text using Tesseract OCR with optimized preprocessing."""
    # processed_img = preprocess_image(image)
    if needs_preprocessing(image):
        logger.info("Applying preprocessing due to low contrast.")
    image = preprocess_image(image)

    # OCR config to improve text recognition
    custom_config = "--oem 3 --psm 4 -c preserve_interword_spaces=1"
    extracted_text = pytesseract.image_to_string(image, config=custom_config)

    logger.info(f"Extracted Text:\n{extracted_text.strip()}")
    return clean_text(extracted_text.strip())

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
