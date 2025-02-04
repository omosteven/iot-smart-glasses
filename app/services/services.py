from app.ai import image_to_text
from app.ai import image_to_detection
from fastapi import File, UploadFile, HTTPException

DEVICE_STATE = 0

def process_data(data):
    return {"processed_data": data.upper()}

def set_device_connectivity(data):
    global DEVICE_STATE
    DEVICE_STATE= 1
    return {
        "message": "Connection Set"
    }

def get_device_connectivity(data):
    return {
        "message": (DEVICE_STATE==0) if  "Device Connected" else ""
    }

async def get_text_from_image(file: UploadFile = File(...)):
    """
    Endpoint to extract text from an uploaded image file.

    Args:
        file (UploadFile): The uploaded image file.

    Returns:
        dict: The extracted text.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
    
    extracted_text = await image_to_text(file)
    if extracted_text is None:
        raise HTTPException(status_code=500, detail="2 Failed to extract text from the image.")
    
    return {"data": extracted_text, "message":"success"}


async def get_detection_from_image(file: UploadFile = File(...)):
    """
    Endpoint to extract text from an uploaded image file.

    Args:
        file (UploadFile): The uploaded image file.

    Returns:
        dict: The extracted text.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")
    
    extracted_text = await image_to_detection(file)
    if extracted_text is None:
        raise HTTPException(status_code=500, detail="2 Failed to extract text from the image.")
    
    return {"data": extracted_text, "message":"success"}