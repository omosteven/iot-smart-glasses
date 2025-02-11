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
import time
from ultralytics import YOLO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load YOLO model
yolo8n_model = YOLO('yolov8n.pt', task='detect').to("cpu")

# yolo8_model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
# yolo5n_model = torch.hub.load('ultralytics/yolo11', 'yolo11n')
# yolo5s_model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
# Model dictionary

thread_pool = ThreadPoolExecutor(max_workers=2)

CLASSES_CONTRAINTS ={
    "0": "person",
    "1": "bicycle",
    "2": "car",
    "3": "motorcycle",
    "4": "airplane",
    "5": "bus",
    "6": "train",
    "7": "truck",
    "8": "boat",
    "10": "fire hydrant",
    "13": "bench",
    "25": "umbrella",
    "26": "handbag",
    "28": "suitcase",
    "39": "bottle",
    "40": "wine glass",
    "41": "cup",
    "42": "fork",
    "43": "knife",
    "44": "spoon",
    "55": "cake",
    "56": "chair",
    "57": "couch",
    "58": "potted plant",
    "59": "bed",
    "60": "dining table",
    "62": "tv",
    "63": "laptop",
    "64": "mouse",
    "66": "keyboard",
    "67": "cell phone",
    "68": "microwave",
    "69": "oven",
    "70": "toaster",
    "72": "refrigerator",
    "73": "book",
    "74": "clock",
    "77": "teddy bear",
}

models = {'yolo8n': yolo8n_model}

def compress_image(image: Image.Image, quality=50):
    """Compress image only if larger than 500KB and convert RGBA to RGB if needed."""
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")  # Save as PNG to check size
    size_kb = len(buffer.getvalue()) / 1024  # Convert bytes to KB
    
    if size_kb > 500:  # Compress only if > 500KB
        logger.info(f"Compressing image (Original: {size_kb:.2f} KB)")
        if image.mode == "RGBA":
            image = image.convert("RGB")  # Convert RGBA to RGB
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=quality)
        buffer.seek(0)
        image = Image.open(buffer)
        logger.info(f"Compressed size: {len(buffer.getvalue()) / 1024:.2f} KB")
    
    return image

def preprocess_for_yolo(image: Image.Image, target_size=(640, 640)):
    """Resize image before running YOLO to speed up detection."""
    start_time = time.time()
    
    img_array = np.array(image)
    img_array = cv2.resize(img_array, target_size)  # Resize before detection
    
    # Normalize pixel values (YOLO expects 0-1 range)
    img_array = img_array / 255.0

    elapsed = time.time() - start_time
    print(f"YOLO Resize took: {elapsed:.2f} sec")
    return img_array


def enhance_image(image: Image.Image):
    img = np.array(image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # Apply histogram equalization
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l = cv2.equalizeHist(l)
    lab = cv2.merge((l, a, b))
    enhanced_img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    return Image.fromarray(cv2.cvtColor(enhanced_img, cv2.COLOR_BGR2RGB))


def detect_with_yolo(img_array, model_name='yolo8n'):
    """Run object detection with YOLO model."""

    start_time = time.time()
    model = models.get(model_name)
    if not model:
        logger.error(f"Model {model_name} not found")
        return []
    
    results = model(img_array, iou=0.5)

    # detections = [
    #     {
    #         "object": r.names[int(box.cls)],
    #         "confidence": float(box.conf),
    #     }
    #     for r in results for box in r.boxes
    # ]
    CONFIDENCE_THRESHOLD = 0.25  # Adjust this based on testing

    detections = [
        {
            "object": r.names[int(box.cls)],
            "confidence": float(box.conf),
        }
        for r in results for box in r.boxes if float(box.conf) > CONFIDENCE_THRESHOLD
        if str(int(box.cls)) in CLASSES_CONTRAINTS 
    ]


    elapsed = time.time() - start_time
    logger.info(f"YOLO Detection took: {elapsed:.2f} sec")
    print(f"Detection took: {elapsed:.2f} sec")

    return detections

def clean_text(text: str):
    # print('actual text:', text)
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
    start_time = time.time()
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

    sharped_img = Image.fromarray(sharpened)
    elapsed = time.time() - start_time
    print(f"Text Preprocess took: {elapsed:.2f} sec")
    return sharped_img

def resize_for_ocr(image: Image.Image, max_width=1000):
    """Resize image to improve Tesseract speed while maintaining accuracy."""
    if image.width > max_width:
        aspect_ratio = image.height / image.width
        new_height = int(max_width * aspect_ratio)
        image = image.resize((max_width, new_height), Image.LANCZOS)
    return image


def extract_text_with_tesseract(image: Image.Image):
    """Extract text using Tesseract OCR with optimized preprocessing."""
    # processed_img = preprocess_image(image)
    start_time = time.time()
    # image = enhance_image(image)

    if np.array(image.convert("L")).std() < 30:  # If contrast is low
        logger.info("Applying preprocessing due to low contrast.")
        image = preprocess_image(image)

    # OCR config to improve text recognition
    custom_config = "--oem 3 --psm 4 -c preserve_interword_spaces=1"
    # custom_config = "--oem 3 --psm 6 -c preserve_interword_spaces=1"

    extracted_text = pytesseract.image_to_string(image, config=custom_config)

    # logger.info(f"Extracted Text:\n{extracted_text.strip()}")
    elapsed = time.time() - start_time
    print(f"Text Extraction took: {elapsed:.2f} sec")
    return clean_text(extracted_text)

def detect_with_yolo_batch(images, model_name="yolo8n"):
    model = models.get(model_name)
    if not model:
        logger.error(f"Model {model_name} not found")
        return []

    results = model(images)  # YOLO processes all images in one call

    detections = []
    for i, r in enumerate(results):
        detections.append([
            {
                "object": r.names[int(box.cls)],
                "confidence": float(box.conf),
            }
            for box in r.boxes if str(int(box.cls)) in CLASSES_CONTRAINTS
        ])
    
    return detections


async def image_to_detection(image_file: UploadFile):
    """Process image for object detection and text extraction concurrently."""
    try:
        logger.info("Starting image processing.")

        # Read image file asynchronously
        contents = await image_file.read()
        image = Image.open(io.BytesIO(contents))
        image = compress_image(image)

        # Convert PNG with transparency (RGBA) to RGB
        if image.mode == "RGBA":
            image = image.convert("RGB")

        # img_array = preprocess_for_yolo(image)
        img_array = np.array(image)
        # Run YOLO detection and Tesseract OCR concurrently
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor(max_workers=2) as pool:
            start_time = time.time()
            yolo_task = loop.run_in_executor(pool, detect_with_yolo, img_array, 'yolo8n')
            ocr_task = loop.run_in_executor(pool, extract_text_with_tesseract, image)

            detections, detected_texts = await asyncio.gather(yolo_task, ocr_task)
            elapsed = time.time() - start_time
            print(f"Overal Time taken: {elapsed:.2f} sec")
        return {"detections": detections, "texts": detected_texts}

    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return {"error": str(e)}
