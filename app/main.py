from fastapi import FastAPI
from starlette.middleware.trustedhost import TrustedHostMiddleware
from app.routes import routes  # Import routes
from app.constants.constants import API_VERSION

app = FastAPI()

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

class MaxSizeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        max_size = 500 * 1024 * 1024  # 10 MB
        if request.headers.get('content-length') and int(request.headers['content-length']) > max_size:
            return Response("Request entity too large", status_code=413)
        return await call_next(request)

app.add_middleware(MaxSizeMiddleware)

# Include routes
app.include_router(routes.router, prefix=API_VERSION)


@app.get(f"{API_VERSION}")
async def welcome_root():
    return {"message": "Welcome to Steven IoT AI API!"}

# Root endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to FastAPI!"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)