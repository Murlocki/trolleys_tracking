from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.camera_service.router import camera_router
from src.shared.logger_setup import setup_logger

logger = setup_logger(__name__)

app = FastAPI()
app.include_router(camera_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],                # или ["*"] для всех
    allow_credentials=True,
    allow_methods=["*"],                  # GET, POST, OPTIONS, PUT, DELETE, и т.д.
    allow_headers=["*"],                  # Authorization, X-API-Key и любые другие
)

@app.get("/")
async def root():
    return {"message": "Hello World"}
