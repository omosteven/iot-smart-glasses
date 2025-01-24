import cv2
import easyocr

def preprocess_frame(frame):
    """
    Preprocess the frame for OCR:
    - Convert to grayscale (optional for EasyOCR, but improves speed slightly).
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return gray

def main():
    # Initialize the EasyOCR Reader (load only necessary languages)
    reader = easyocr.Reader(['en'], gpu=False)  # Set `gpu=True` if your system supports it

    # Initialize the camera
    camera = cv2.VideoCapture(0)  # Use 0 or 1 for your camera input
    if not camera.isOpened():
        print("Error: Could not access the camera.")
        return

    print("Press 'q' to quit the application.")

    while True:
        ret, frame = camera.read()
        if not ret:
            print("Error: Unable to capture frame.")
            break

        # Preprocess the frame
        preprocessed_frame = preprocess_frame(frame)

        # Perform OCR using EasyOCR
        results = reader.readtext(preprocessed_frame, detail=0)

        # Display the frame and detected text
        cv2.imshow("Camera View", frame)
        print("Detected Text:", results)

        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    camera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
