from fastapi import UploadFile
import torch
import onnxruntime as ort
import numpy as np
import easyocr
from PIL import Image
import io
import logging
from ultralytics import YOLO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load ONNX models
onnx_model_paths = {
    'yolo8n': "yolov8n.onnx",
    'yolo8s': "yolov8s.onnx", 
    'yolo5n': "yolov5nu.onnx",
    'yolo5s': "yolov5su.onnx",
}

onnx_sessions = {
    model: ort.InferenceSession(onnx_model_paths[model]) for model in onnx_model_paths
}

# Load PyTorch models
pytorch_models = {
    'yolo8n': YOLO('yolov8n.pt'),
    'yolo8s': YOLO('yolov8s.pt'),
    'yolo5n': torch.hub.load('ultralytics/yolov5', 'yolov5n'),
    'yolo5s': torch.hub.load('ultralytics/yolov5', 'yolov5s'),
}

# YOLO class labels (COCO dataset)
YOLO_CLASSES = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck",
    "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
    "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra",
    "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee",
    "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove",
    "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
    "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange",
    "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch",
    "potted plant", "bed", "dining table", "toilet", "TV", "laptop", "mouse",
    "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
    "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier",
    "toothbrush"
]

# Load EasyOCR for text detection
reader = easyocr.Reader(["en"])

def preprocess_image(image: Image.Image) -> np.ndarray:
    """ Preprocess image for YOLO ONNX model """
    img_resized = image.resize((640, 640))  # Resize to 640x640
    img_array = np.array(img_resized).astype(np.float32) / 255.0  # Normalize
    img_array = np.transpose(img_array, (2, 0, 1))  # Convert HWC to CHW
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array

def postprocess_yolo_output(output: np.ndarray, conf_threshold=0.3):
    """ Convert ONNX YOLO model output into human-readable detections """
    output = np.squeeze(output)  # Remove batch dimension
    detections = []
    
    for row in output:
        x_min, y_min, x_max, y_max, conf, class_id = row[:6]
        
        if conf > conf_threshold:  # Confidence threshold
            detections.append({
                "object": YOLO_CLASSES[int(class_id)],
                "confidence": float(conf),
                "bbox": [float(x_min), float(y_min), float(x_max), float(y_max)]
            })
    
    return detections

def detect_with_yolo(img_array, model_name='yolo8s', use_onnx=True):
    """ Perform inference using either ONNX or PyTorch YOLO model """
    if use_onnx:
        if model_name not in onnx_sessions:
            logger.error(f"ONNX model {model_name} not found")
            return []
        session = onnx_sessions[model_name]
        input_name = session.get_inputs()[0].name
        results = session.run(None, {input_name: img_array})
        return postprocess_yolo_output(results[0])
    
    else:
        if model_name not in pytorch_models:
            logger.error(f"PyTorch model {model_name} not found")
            return []
        
        model = pytorch_models[model_name]
        results = model(img_array)
        detections = []

        if "yolo5" in model_name:
            detections = results.pandas().xyxy[0].to_dict(orient="records")
        else:
            for r in results:
                for box in r.boxes:
                    detections.append({
                        "object": r.names[int(box.cls)],
                        "confidence": float(box.conf),
                        "bbox": box.xyxy.tolist()
                    })

        return detections

def extract_text_with_easyocr(img_array):
    """ Extract text from an image using EasyOCR """
    text_results = reader.readtext(img_array)
    detected_texts = [{"text": text, "bbox": bbox} for bbox, text, _ in text_results]
    return detected_texts

async def image_to_detection(image_file: UploadFile, model_name: str = 'yolo8s', use_onnx: bool = False):
    """ Process image and perform object detection and text extraction """
    try:
        logger.info(f"Processing image with model {model_name} (ONNX={use_onnx})")
        contents = await image_file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")

        # Preprocess image for YOLO ONNX
        img_array = preprocess_image(image)

        # Perform object detection (ONNX or PyTorch)
        detections = detect_with_yolo(img_array, model_name, use_onnx)

        # Perform text detection
        detected_texts = extract_text_with_easyocr(np.array(image))

        return {"detections": detections, "texts": detected_texts}
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        return None
