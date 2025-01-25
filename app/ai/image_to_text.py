from typing import Union
from fastapi import UploadFile
from PIL import Image
import pytesseract
import io

def image_to_text(image_file: UploadFile) -> Union[str, None]:
    """
    Extract text from an uploaded image file using Tesseract OCR.

    Args:
        image_file (UploadFile): The uploaded image file.

    Returns:
        str: The extracted text, or None if extraction fails.
    """
    try:
        # Read the uploaded file as an image
        # image = Image.open(image_file.file)
        image = Image.open(io.BytesIO(image_file.file.read()))
        
        # Perform OCR using Tesseract
        extracted_text = pytesseract.image_to_string(image)
        
        if not extracted_text:
            raise ValueError("No text found in the image.")
        
        return extracted_text.strip()
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None
