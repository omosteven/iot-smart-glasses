import cv2
import pytesseract


class RealTimeOCR:
    def __init__(self, camera_index=0, tesseract_config="--oem 3 --psm 6"):
        """
        Initialize the OCR pipeline for testing on a laptop.

        Args:
            camera_index: Index of the webcam (default is 0 for the primary camera).
            tesseract_config: Configuration for Tesseract OCR.
        """
        self.camera = cv2.VideoCapture(camera_index)
        self.tesseract_config = tesseract_config

        if not self.camera.isOpened():
            raise Exception("Webcam could not be opened!")

    def preprocess_image(self, image):
        """
        Preprocess the image to improve OCR accuracy.

        Args:
            image: Input image from the webcam.

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
        print("Starting real-time OCR. Press 'q' to quit.")
        try:
            while True:
                ret, frame = self.camera.read()
                if not ret:
                    print("Failed to grab frame.")
                    break

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
        self.camera.release()
        cv2.destroyAllWindows()


# Example usage
if __name__ == "__main__":
    ocr = RealTimeOCR()
    ocr.run()
