
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

    #SECRET_KEY: str
    #ENCRYPTION_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    

    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
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