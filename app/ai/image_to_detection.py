
from fastapi import UploadFile
import torch
import numpy as np
import easyocr
from PIL import Image
import io
import logging
import pytesseract
from ultralytics import YOLO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


yolo8_model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
yolo5n_model = torch.hub.load('ultralytics/yolov5', 'yolov5n')
yolo5s_model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
yolo8n_model = YOLO('yolov8n.pt')  
yolo8s_model = YOLO('yolov8s.pt')

reader = easyocr.Reader(["en"]) 

models = {
    'yolo8n': yolo8n_model,
    'yolo8s': yolo8s_model,
    'yolo5n': yolo5n_model,
    'yolo5s': yolo5s_model
}

def detect_with_yolo(img_array, model_name='yolo5s'):
    model = models.get(model_name)
    
    if not model:
        logger.error(f"Model {model_name} not found")
        return []

    results = model(img_array)

    if model_name in {'yolo5s', 'yolo5n'}:
        return results.pandas().xyxy[0].to_dict(orient="records")

    return [
        {
            "object": r.names[int(box.cls)],  # Ensure it's a Python `int`
            "confidence": float(box.conf),  # Convert NumPy float to Python `float`
            # "bbox": [float(coord) for coord in box.xyxy.tolist()]  # Convert all bbox values to Python `float`
        }
        for r in results for box in r.boxes
    ]


def extract_text_with_easyocr(img_array):
    text_results = reader.readtext(img_array)
    
    # Concatenate all the detected text into a single string
    concatenated_text = " ".join([text for _, text, _ in text_results])
    
    return concatenated_text

     
async def image_to_detection(image_file: UploadFile):
    try:
        logger.info("Starting text extraction process.")
        contents = await image_file.read()
        image = Image.open(io.BytesIO(contents))
        if image.mode == "RGBA":
            image = image.convert("RGB")

        img_resized = image.resize((1280, 1280)) 
        img_array = np.array(img_resized)  

        detections = detect_with_yolo(img_array, 'yolo8n')
        detected_texts = pytesseract.image_to_string(image)
        # detected_texts = extract_text_with_easyocr(img_array)
        return {"detections": detections, "texts": detected_texts}
    except Exception as e:
        logger.error(f"Error extracting text: {e}")
        return None