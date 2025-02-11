import cv2
import numpy as np
# import easyocr
import torch
import onnxruntime as ort

class ObjectAndTextDetection:
    def __init__(self):
        # Initialize EasyOCR reader
        # self.ocr_reader = easyocr.Reader(['en'])

        # Load the YOLOv4-tiny or YOLOv5 model in ONNX format
        self.ort_session = ort.InferenceSession("yolov5s.onnx")  # Use your path to the ONNX model

        # Set image size for YOLO model
        self.input_size = 640  # This is the typical size for YOLOv5 models

    def preprocess_image(self, image):
        """ Preprocess image for YOLO model (resize, normalize, etc.) """
        # Resize image to fit model input size
        image_resized = cv2.resize(image, (self.input_size, self.input_size))
        # Normalize image
        image_resized = image_resized.astype(np.float32) / 255.0
        # Transpose for ONNX input [B, C, H, W]
        image_resized = np.transpose(image_resized, (2, 0, 1))
        image_resized = np.expand_dims(image_resized, axis=0)
        return image_resized

    def run_yolo(self, image):
        """ Run YOLO inference on image """
        image_resized = self.preprocess_image(image)
        
        # Run the image through YOLO model
        outputs = self.ort_session.run(None, {'images': image_resized})

        # Extract bounding boxes and confidence scores
        boxes = outputs[0]
        confidences = outputs[1]
        class_ids = outputs[2]
        return boxes, confidences, class_ids

    def process_yolo_results(self, boxes, confidences, class_ids, threshold=0.5):
        """ Process YOLO results to filter and draw boxes """
        results = []
        for i, box in enumerate(boxes[0]):
            confidence = confidences[0][i]
            if confidence > threshold:
                x1, y1, x2, y2 = box
                result = {
                    'class_id': class_ids[0][i],
                    'confidence': confidence,
                    'bbox': (int(x1), int(y1), int(x2), int(y2))
                }
                results.append(result)
        return results

    # def detect_text(self, image):
    #     """ Run EasyOCR to extract text from image """
    #     result = self.ocr_reader.readtext(image)
    #     texts = [text[1] for text in result]  # Extract only the detected text
    #     return texts

    def process_frame(self, frame):
        """ Process a frame to detect objects and text """
        # Detect objects using YOLO
        boxes, confidences, class_ids = self.run_yolo(frame)
        yolo_results = self.process_yolo_results(boxes, confidences, class_ids)

        # Detect text using EasyOCR
        # texts = self.detect_text(frame)
        texts = ""

        return yolo_results, texts

    def draw_results(self, frame, yolo_results, texts):
        """ Draw bounding boxes for YOLO and display detected text """
        for result in yolo_results:
            x1, y1, x2, y2 = result['bbox']
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{result['class_id']}:{result['confidence']:.2f}", 
                        (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Display detected text
        for text in texts:
            cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        return frame

# Example usage on Raspberry Pi
if __name__ == "__main__":
    detector = ObjectAndTextDetection()

    # Initialize webcam (or use your camera)
    cap = cv2.VideoCapture(0)  # 0 for default camera

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        yolo_results, texts = detector.process_frame(frame)
        print('res', yolo_results, texts)
        # frame = detector.draw_results(frame, yolo_results, texts)

        # Show frame with results
        # cv2.imshow("Detection", frame)

        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
