from app.ai import image_to_text
from fastapi import File, UploadFile, HTTPException

DEVICE_STATE = 0

def process_data(data):
    return {"processed_data": data.upper()}

def set_device_connectivity(data):
    DEVICE_STATE= 1
    return {
        "message": "Connection Set"
    }

def get_device_connectivity(data):
    return {
        "message": (DEVICE_STATE==0) if  "Device Connected" else ""
    }

def get_text_from_image(file: UploadFile = File(...)):
    """
    Endpoint to extract text from an uploaded image file.

    Args:
        file (UploadFile): The uploaded image file.

    Returns:
        dict: The extracted text.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
    
    extracted_text = image_to_text(file)
    
    if extracted_text is None:
        raise HTTPException(status_code=500, detail="Failed to extract text from the image.")
    
    return {"extracted_text": extracted_text}