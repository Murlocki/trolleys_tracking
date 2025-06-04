from fastapi import FastAPI
from src.shared.logger_setup import setup_logger

logger = setup_logger(__name__)

app = FastAPI()


