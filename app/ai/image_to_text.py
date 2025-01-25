from typing import Union
from fastapi import UploadFile
from PIL import Image
import pytesseract
import io
import logging

def image_to_text(image_file: UploadFile) -> Union[str, None]:
    """
    Extract text from an uploaded image file using Tesseract OCR.

    Args:
        image_file (UploadFile): The uploaded image file.

    Returns:
        str: The extracted text, or None if extraction fails.
    """
    try:
        logging.info("Reading image file...")
        # Ensure file stream is properly read
        contents = image_file.file.read()
        image_file.file.seek(0)  # Reset the file pointer after reading
        
        # Load the image from bytes
        image = Image.open(io.BytesIO(contents))
        logging.info("Performing OCR...")
        # Perform OCR using Tesseract
        extracted_text = pytesseract.image_to_string(image)
        
        if not extracted_text:
            logging.warning("No text found in the image.")
            raise ValueError("No text found in the image.")
        logging.info("OCR completed successfully.")
        return extracted_text.strip()
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None
  