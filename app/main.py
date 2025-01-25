from fastapi import FastAPI
from app.routes import routes  # Import routes
from app.constants.constants import API_VERSION

app = FastAPI()

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