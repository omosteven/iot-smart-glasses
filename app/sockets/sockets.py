from fastapi import APIRouter, WebSocket
from fastapi.responses import JSONResponse
from app.sockets.events import CHECK_DEVICE

router = APIRouter()

connected_clients = {}

@router.websocket("/ws/{device_id}")
async def websocket_endpoint(websocket: WebSocket, device_id: str):
    await websocket.accept()
    connected_clients[device_id] = websocket
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except Exception as e:
        print(f"Device {device_id} disconnected: {e}")
    finally:
        del connected_clients[device_id]

@router.get(f"/{CHECK_DEVICE}")
async def check_device(device_id: str):
    if device_id in connected_clients:
        return JSONResponse({"status": "connected"})
    return JSONResponse({"status": "disconnected"})

async def broadcast_log(event: str, data: dict):
    """Send logs to all connected WebSocket clients."""
    message = {"event": event, "data": data}
    disconnected_clients = []
    
    for device_id, websocket in connected_clients.items():
        try:
            await websocket.send_json(message)
            print('sent to:', device_id, 'event:', event,'mesg:', message)
        except Exception as e:
            print(f"Failed to send to {device_id}: {e}")
            disconnected_clients.append(device_id)
    
    # Clean up disconnected clients
    for device_id in disconnected_clients:
        del connected_clients[device_id]
