import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(verbose=True)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=os.path.join(BASE_DIR, "detection_service/.env"))
    deepsort_max_cosine_distance = 0.2
    deepsort_max_iou_distance = 0.7
    deepsort_max_age = 30
    deepsort_n_init = 3
    deepsort_nn_budget = 100

    tracking_process_live_seconds = 40
    tracking_process_live_minutes = 40
    tracking_process_live_hours = 40


detection_settings = Settings()
print(detection_settings)