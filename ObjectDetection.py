import cv2
import pytesseract
import numpy as np

class ObjectDetection:

    def __init__(self):
        # Initialize the camera
        self.cap = cv2.VideoCapture(0)
        self.MODELS = ['Yolov4', 'Yolov3', 'MobileNetSSD']
        self.model = self.MODELS[0]
        pytesseract.pytesseract.tesseract_cmd = "/usr/local/bin/tesseract"

    def choose_model(self):
        model = self.model
        models_list = self.MODELS
        yolov4 = models_list[0]
        yolov3 = models_list[1]
        mobileNet = models_list[2]

        if model == yolov4:
            self.net = cv2.dnn.readNet(
                'models/YoloTiny/yolov4-tiny.weights',
                'models/YoloTiny/yolov4-tiny.cfg'
            )
            with open('models/YoloTiny/coco.names', 'r') as f:
                self.CLASSES = [line.strip() for line in f.readlines()]
            # layer_names = self.net.getLayerNames()
            # self.layer_names = [layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

            self.layer_names = self.net.getUnconnectedOutLayersNames()

        elif model == yolov3:
            self.net = cv2.dnn.readNet(
                'models/Yolo3/yolov3.weights',
                'models/Yolo3/yolov3.cfg'
            )
            with open('models/Yolo3/coco.names', 'r') as f:
                self.CLASSES = [line.strip() for line in f.readlines()]
            self.layer_names = self.net.getUnconnectedOutLayersNames()

        elif model == mobileNet:
            self.net = cv2.dnn.readNetFromCaffe(
                'models/MobileNetSSD/MobileNetSSD_deploy.prototxt',
                'models/MobileNetSSD/MobileNetSSD_deploy.caffemodel'
            )
            self.CLASSES = [
                "background", "aeroplane", "bicycle", "bird", "boat",
                "bottle", "bus", "car", "cat", "chair", "cow",
                "diningtable", "dog", "horse", "motorbike", "person",
                "pottedplant", "sheep", "sofa", "train", "tvmonitor"
            ]
        else:
            print('No model chosen')
        return None

    def detect_text(self, frame):
        """Extract text from the frame using Tesseract."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray, lang='eng')
        return text.strip()

    def detect_by_yolo(self, frame):
        (h, w) = frame.shape[:2]

        # Resize the image to 416x416 as required by YOLOv3
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        self.net.setInput(blob)
        layer_outputs = self.net.forward(self.layer_names)

        # Loop over each of the layer outputs
        for output in layer_outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.4:  # Adjust confidence threshold as needed
                    # Get the bounding box coordinates
                    center_x = int(detection[0] * w)
                    center_y = int(detection[1] * h)
                    width = int(detection[2] * w)
                    height = int(detection[3] * h)

                    # Draw a rectangle around detected object
                    cv2.rectangle(frame, (center_x - width // 2, center_y - height // 2),
                                  (center_x + width // 2, center_y + height // 2), (0, 255, 0), 2)

                    label = self.CLASSES[class_id]
                    if label == "person":
                        return "human"
                    else:
                        return "object"
        return None

    def detect_by_mobileNetSSD(self, frame):
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)

        self.net.setInput(blob)
        detections = self.net.forward()

        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:
                idx = int(detections[0, 0, i, 1])
                label = self.CLASSES[idx]
                if label == "person":
                    return "human"
                else:
                    return "object"
        return None

    def detect_objects(self, frame):
        if self.model == self.MODELS[2]: #if model is MobileNetSSD
            self.detect_by_mobileNetSSD(frame)
        else:
            self.detect_by_yolo(frame)
        return None

    def run(self):
        """Run the real-time detection."""
        self.choose_model()

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            # Detect text
            text = self.detect_text(frame)
            if text:
                print("Text detected:", text)
            else:
                # Detect objects or humans
                detection = self.detect_objects(frame)
                if detection == "human":
                    print("Human detected")
                elif detection == "object":
                    print("Object detected")
                else:
                    print(detection)

            # Display the frame
            cv2.imshow('Real-Time Detector', frame)

            # Break the loop on pressing 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release resources
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    detector = ObjectDetection()
    detector.model = detector.MODELS[0]
    detector.run()
