
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[3]

class Settings(BaseSettings):

    PROJECT_NAME: str = "Edumentor AI Project 2"
    API_STR: str = "/api"
    DESCRIPTION: str = """"""

    VERSION: str
    DATABASE_URL: str
    SQL_ECHO: bool

    SECRET_KEY: str
    #ENCRYPTION_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    RESET_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    UPLOAD_DIR: str = "uploads"               # tính từ thư mục backend/
    AVATAR_MAX_BYTES: int = 5 * 1024 * 1024   # 5 MB (Q8, chốt 07/11)

    # Email — để trống hoặc "smtp.example.com" thì chỉ IN link ra terminal (chế độ dev)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    FRONTEND_URL: str = "http://localhost:5173"

    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://127.0.0.1:5171",
        "http://localhost:5171",   
    ]

    model_config = SettingsConfigDict(
        env_file= BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

"""
FastAPI location	Database host	Port
Your computer	localhost	5433
Another container on the Compose network	postgres	5432

khi dockerized thì thay đổi @localhost sang @postgres. service name trong docker compose.yaml file
"""
