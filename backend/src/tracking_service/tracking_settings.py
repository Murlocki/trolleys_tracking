import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(verbose=True)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=os.path.join(BASE_DIR, "tracking_service/.env"))
    deepsort_max_cosine_distance: float = 0.2
    deepsort_max_iou_distance: float = 0.7
    deepsort_max_age: int = 30
    deepsort_n_init: int = 3
    deepsort_nn_budget: int = 100

    tracking_process_live_seconds: int = 40
    tracking_process_live_minutes: int = 40
    tracking_process_live_hours: int = 40


tracking_settings = Settings()
print(tracking_settings)