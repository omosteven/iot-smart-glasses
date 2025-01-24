from fastapi import APIRouter, File, UploadFile
from app.services import services

router = APIRouter()

@router.get("/example")
async def get_example():
    return {"message": "This is an example endpoint."}

@router.post("/image-to-text")
async def image_to_text(file: UploadFile = File(...)):
    return services.get_text_from_image(file)

@router.get("/receive-device-connectivity")
async def receive_device_connectivity():
    return services.get_device_connectivity()

@router.get("/send-device-connectivity")
async def send_device_connectivity():
    return services.set_device_connectivity()

@router.get("/process-realtime-video")
async def process_realtime_video():
    return {"message": "This is an example endpoint."}

@router.get("/upload-video")
async def upload_video():
    return {"message": "This is an example endpoint."}

@router.get("/retrieve-video")
async def retrieve_video():
    return {"message": "This is an example endpoint."}
