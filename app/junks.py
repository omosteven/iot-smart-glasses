
# ort_session = ort.InferenceSession("yolov8n.onnx")

# yolo8_model = YOLO("yolov8s.pt")
# import onnxruntime as ort

# def detect_with_yolo8(img_array):
#     results = yolo8_model(img_array)
#     detections = []
#     for r in results:
#             for box in r.boxes:
#                 detections.append({
#                     "object": r.names[int(box.cls)],
#                     "confidence": float(box.conf),
#                     "bbox": box.xyxy.tolist()
#                 })
#     return detections



from fastapi import UploadFile
import torch
import numpy as np
import easyocr
from PIL import Image
import io
import logging
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
    yolo5 = ['yolo5s','yolo5n']
    if not model:
        logger.error(f"Model {model_name} not found")
        return []

    # Perform object detection
    results = model(img_array)
    detections= []

    if model_name in yolo5:
        detections = results.pandas().xyxy[0].to_dict(orient="records")
    else:
        for r in results:
            for box in r.boxes:
                detections.append({
                    "object": r.names[int(box.cls)],
                    "confidence": float(box.conf),
                    "bbox": box.xyxy.tolist()
                })

    # Parse detection results
    return detections

def extract_text_with_easyocr(img_array):
    text_results = reader.readtext(img_array)
    detected_texts = [{"text": text, "bbox": bbox} for bbox, text, _ in text_results]
    return detected_texts
     
async def image_to_detection(image_file: UploadFile):
    try:
        logger.info("Starting text extraction process.")
        # contents = await image_file.read()
        contents = await image_file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        img_resized = image.resize((320, 320))  # Resize for ONNX
        img_array = np.array(img_resized)  
        # img_array = img_array.astype(np.float32) / 255.0  # Normalize
      
        # Object detection
        detections = detect_with_yolo(img_array,'yolo5s')
        detected_texts = extract_text_with_easyocr(img_array)
        print('detected', detections)
        return {"detections": detections, "texts": detected_texts}
    except Exception as e:
        print('error occurred',e)
        logger.error(f"Error extracting text: {e}")
        return None