from fastapi import FastAPI

from src.camera_reader_service.router import camera_reader_router
from src.shared.logger_setup import setup_logger

logger = setup_logger(__name__)

app = FastAPI()
app.include_router(camera_reader_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
