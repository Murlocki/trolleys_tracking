import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
load_dotenv(verbose=True)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=os.path.join(BASE_DIR, "classification_service/.env"))
    classification_yolo_11_model_path: str = "classification_service/weights/yolo11.pt"
    classification_yolo_11_img_sz: int = 640

    @property
    def full_model_path(self) -> str:
        return os.path.join(BASE_DIR, self.classification_yolo_11_model_path)


classification_settings = Settings()
print(classification_settings)