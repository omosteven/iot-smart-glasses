import cv2
import pytesseract
from picamera.array import PiRGBArray
from picamera import PiCamera
import time


class RealTimeOCR:
    def __init__(self, resolution=(640, 480), framerate=30, tesseract_config="--oem 3 --psm 6"):
        """
        Initialize the OCR pipeline.

        Args:
            resolution: Resolution of the PiCamera capture.
            framerate: Frame rate of the camera.
            tesseract_config: Configuration for Tesseract OCR.
        """
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.raw_capture = PiRGBArray(self.camera, size=resolution)
        self.tesseract_config = tesseract_config

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
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
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
        print("Starting real-time OCR. Press Ctrl+C to stop.")
        try:
            for frame in self.camera.capture_continuous(self.raw_capture, format="bgr", use_video_port=True):
                image = frame.array
                processed_image = self.preprocess_image(image)
                text = self.extract_text(processed_image)

                # Display the image and extracted text
                cv2.imshow("Frame", processed_image)
                print("Extracted Text:", text)

                # Clear the stream for the next frame
                self.raw_capture.truncate(0)

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
        cv2.destroyAllWindows()
        self.camera.close()


# Example usage
if __name__ == "__main__":
    ocr = RealTimeOCR()
    ocr.run()
