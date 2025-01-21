from picamera2 import Picamera2
import cv2
import easyocr
import numpy as np
import time

class RealTimeOCREasyOCR:
    def __init__(self, resolution=(320, 240), langs=['en']):
        """
        Initialize the EasyOCR-based real-time OCR pipeline.
        
        Args:
            resolution: Resolution of the Picamera2 capture.
            langs: List of languages for EasyOCR (default is English).
        """
        self.camera = Picamera2()
        self.reader = easyocr.Reader(langs, gpu=False)  # Disable GPU for Raspberry Pi
        self.resolution = resolution

        # Configure camera
        camera_config = self.camera.create_preview_configuration(
            main={"size": resolution, "format": "RGB888"}
        )
        self.camera.configure(camera_config)
        self.camera.start()

        # Allow the camera to warm up
        time.sleep(2)

    def preprocess_image(self, image):
        """
        Preprocess the image for better OCR accuracy.
        
        Args:
            image: Input image from the camera.
            
        Returns:
            Preprocessed image (grayscale and optionally thresholded).
        """
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        # Apply adaptive threshold for better OCR performance
        processed_image = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        return processed_image

    def extract_text(self, image):
        """
        Extract text from an image using EasyOCR.
        
        Args:
            image: Input preprocessed image.
            
        Returns:
            Extracted text as a string.
        """
        results = self.reader.readtext(image)
        extracted_text = " ".join([result[1] for result in results])  # Concatenate detected text
        return extracted_text

    def run(self):
        """
        Run the real-time OCR pipeline.
        """
        print("Starting real-time OCR with EasyOCR. Press 'q' to quit.")
        try:
            while True:
                # Capture a frame
                frame = self.camera.capture_array()
                processed_image = self.preprocess_image(frame)
                text = self.extract_text(processed_image)
                
                # Display the processed image and extracted text
                cv2.imshow("Processed Frame", processed_image)
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
    ocr = RealTimeOCREasyOCR()
    ocr.run()
