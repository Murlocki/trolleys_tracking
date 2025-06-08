from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.shared.logger_setup import setup_logger
from src.user_service.router import user_router

logger = setup_logger(__name__)

app = FastAPI()
app.include_router(user_router)

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
