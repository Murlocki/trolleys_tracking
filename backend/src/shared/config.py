import os

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(verbose=True)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=os.path.join(BASE_DIR, "shared/.env"))
    postgres_user: str = ""
    postgres_password: str = ""
    postgres_db: str = ""
    redis_host: str = ""
    redis_port: int = 6379
    redis_password: str = ""
    redis_db: str = ""
    log_dir: str = os.path.join(BASE_DIR, "logs")
    log_file: str = os.path.join(log_dir, "app.log")
    jwt_secret: str = ""
    jwt_secret_refresh: str = ""
    jwt_algorithm: str = "HS256"
    access_token_expire_seconds: int = 15
    access_token_expire_minutes: int = 0
    access_token_expire_hours: int = 0
    about_to_expire_seconds: int = 300
    refresh_token_expire_days: int = 0
    session_cleanup_seconds: int = 3600
    session_cleanup_minutes: int = 0
    session_cleanup_hours: int = 0
    session_cleanup_days: int = 0
    user_service_url: str = Field("http://127.0.0.1:8002")
    session_service_url: str = Field("http://127.0.0.1:8001")
    auth_service_url: str = Field("http://127.0.0.1:8000")
    camera_service_url: str = Field("http://127.0.0.1:8004")
    camera_reader_service_url: str = Field("http://127.0.0.1:8003")
    kafka_broker: str = Field("localhost:9093")
    api_key: str = ""
    old_access_token_record_expire_seconds: int = 0


settings = Settings()
print(settings)
