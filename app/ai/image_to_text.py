from typing import Union
from fastapi import UploadFile
from PIL import Image
import pytesseract
import io
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def image_to_text(image_file: UploadFile) -> Union[str, None]:
    """
    Extract text from an uploaded image file using Tesseract OCR.

    Args:
        image_file (UploadFile): The uploaded image file.

    Returns:
        str: The extracted text, or None if extraction fails.
    """
    try:
        logger.info("Starting text extraction process.")

        # Read the uploaded file as an image
        image = Image.open(io.BytesIO(image_file.file.read()))
        logger.info("Image successfully loaded.")

        # Perform OCR using Tesseract
        extracted_text = pytesseract.image_to_string(image)
        logger.info(f"Extracted text: {extracted_text}")

        if not extracted_text:
            raise ValueError("No text found in the image.")
        
        logger.info("Text extraction successful.")
        return extracted_text.strip()
    except Exception as e:
        logger.error(f"Error extracting text: {e}")
        return None