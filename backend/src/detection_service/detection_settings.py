import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
load_dotenv(verbose=True)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=os.path.join(BASE_DIR, "detection_service/.env"))
    detection_yolo_11_model_path: str = "detection_service/weights/yolo11.pt"
    detection_yolo_11_img_sz: int = 640
    detection_yolo_11_conf: float = 0.25
    detection_yolo_11_iou: float = 0.7

    @property
    def full_model_path(self) -> str:
        return os.path.join(BASE_DIR, self.detection_yolo_11_model_path)


detection_settings = Settings()
print(detection_settings)