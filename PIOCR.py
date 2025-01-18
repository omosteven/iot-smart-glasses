import cv2
import pytesseract
from picamera2 import Picamera2
import numpy as np
import time


class RealTimeOCR:
    def __init__(self, resolution=(640, 480), tesseract_config="--oem 3 --psm 6"):
        """
        Initialize the OCR pipeline.
        
        Args:
            resolution: Resolution of the Picamera2 capture.
            tesseract_config: Configuration for Tesseract OCR.
        """
        self.camera = Picamera2()
        self.tesseract_config = tesseract_config
        
        # Configure camera
        camera_config = self.camera.create_preview_configuration(main={"size": resolution, "format": "RGB888"})
        self.camera.configure(camera_config)
        self.camera.start()
        
        # Allow the camera to warm up
        time.sleep(2)

    def preprocess_image(self, image):
        """
        Preprocess the image to improve OCR accuracy.
        
        Args:
            image: Input image from the camera.
            
        Returns:
            Preprocessed image.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        return binary

    def extract_text(self, image):
        """
        Extract text from an image using Tesseract OCR.
        
        Args:
            image: Input image for text extraction.
            
        Returns:
            Extracted text as a string.
        """
        return pytesseract.image_to_string(image, config=self.tesseract_config)

    def run(self):
        """
        Run the real-time OCR pipeline.
        """
        print("Starting real-time OCR. Press 'q' to quit.")
        try:
            while True:
                # Capture a frame
                frame = self.camera.capture_array()
                processed_image = self.preprocess_image(frame)
                text = self.extract_text(processed_image)
                
                # Display the image and extracted text
                cv2.imshow("Frame", processed_image)
                print("Extracted Text:", text)
                
                # Break the loop if 'q' is pressed
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except KeyboardInterrupt:
            print("Stopping real-time OCR.")
        finally:
            self.cleanup()

    def cleanup(self):
        """
        Cleanup resources.
        """
        self.camera.stop()
        cv2.destroyAllWindows()


# Example usage
if __name__ == "__main__":
    ocr = RealTimeOCR()
    ocr.run()
