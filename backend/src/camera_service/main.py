from fastapi import FastAPI

from src.shared.logger_setup import setup_logger
from src.camera_service.router import camera_router

logger = setup_logger(__name__)

app = FastAPI()
app.include_router(camera_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
