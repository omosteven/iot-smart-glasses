import numpy as np
from typing import Union
from fastapi import UploadFile
from PIL import Image
import io
import easyocr
import logging
import cv2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize EasyOCR reader (with GPU enabled if available)
reader = easyocr.Reader(["en"])

def preprocess_image(image: Image.Image) -> np.ndarray:
    """Preprocess image to reduce complexity and enhance OCR accuracy."""
    # Convert image to grayscale
    gray = np.array(image.convert("L"))

    # Resize image to reduce processing time
    resized_image = cv2.resize(gray, (1280, 720))  # Resize for quicker processing

    # Apply binary thresholding for better contrast
    _, thresholded_image = cv2.threshold(resized_image, 150, 255, cv2.THRESH_BINARY)

    # Optional: Sharpen image to enhance text contrast (if needed)
    sharpened = cv2.GaussianBlur(thresholded_image, (5, 5), 2)
    sharpened = cv2.addWeighted(thresholded_image, 1.5, sharpened, -0.5, 0)

    return sharpened

async def image_to_text(image_file: UploadFile) -> Union[str, None]:
    """
    Extract text from an uploaded image file using EasyOCR with optimizations.

    Args:
        image_file (UploadFile): The uploaded image file.

    Returns:
        str: The extracted text, or None if extraction fails.
    """
    try:
        logger.info("Starting text extraction process.")

        # Read the uploaded file as an image
        content = await image_file.read()
        image = Image.open(io.BytesIO(content))
        logger.info("Image successfully loaded.")

        # Preprocess the image for optimal OCR performance
        processed_image = preprocess_image(image)

        # Perform OCR using EasyOCR
        text_results = reader.readtext(processed_image)

        # Extract just the text part from the result
        extracted_text = [text for _, text, _ in text_results]

        if not extracted_text:
            raise ValueError("No text found in the image.")

        logger.info(f"Extracted text: {extracted_text}")

        # Join the text into a single string if needed
        return " ".join(extracted_text)

    except Exception as e:
        logger.error(f"Error extracting text: {e}")
        return None
