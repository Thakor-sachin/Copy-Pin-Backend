import os
import json
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Copy Pin"
    DEBUG: bool = True
    
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost", "http://localhost:5173", "http://localhost:80",
        "http://127.0.0.1", "http://127.0.0.1:5173", "http://127.0.0.1:80"
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            if isinstance(v, str):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    return [v]
            return v
        raise ValueError(v)

    # Database Settings
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/copypin"

    # Redis Settings
    REDIS_URL: str = "redis://redis:6379/0"

    # Celery Settings
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    # Storage Settings
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_UPLOAD_SIZE: int = 104857600  # 100MB in bytes

    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()
