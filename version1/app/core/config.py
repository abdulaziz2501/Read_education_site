"""
Configuration management using Pydantic settings
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator
import secrets


class Settings(BaseSettings):
    # Project info
    PROJECT_NAME: str = "School Management System"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    # POSTGRES_SERVER: str = "localhost"
    # POSTGRES_USER: str = "postgres"
    # POSTGRES_PASSWORD: str = "postgres"
    # POSTGRES_DB: str = "school_db"
    # SQLite uchun DATABASE_URL
    DATABASE_URL: Optional[str] = None

    @validator("DATABASE_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> str:
        if isinstance(v, str):
            return v
        # SQLite uchun
        return f"sqlite+aiosqlite:///./school.db"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    @validator("ALLOWED_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = "noreply@school.uz"
    EMAILS_FROM_NAME: str = PROJECT_NAME

    # Admin
    FIRST_SUPERUSER_EMAIL: str = "admin@school.uz"
    FIRST_SUPERUSER_PASSWORD: str = "admin123"

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds

    # File upload
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    UPLOAD_PATH: str = "uploads"

    # Certificate
    CERTIFICATE_EXPIRY_DAYS: int = 365  # Optional expiry for certificates
    BASE_URL: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()