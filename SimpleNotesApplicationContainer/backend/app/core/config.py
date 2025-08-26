import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOADS_DIR = BASE_DIR / "uploads" / "attachments"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    APP_NAME: str = "SimpleNotes"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:3000"

    # Security
    SECRET_KEY: str = "CHANGE_ME"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days
    JWT_ALGORITHM: str = "HS256"
    COOKIE_SECURE: bool = False
    COOKIE_DOMAIN: str = "localhost"

    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "simplenotes"
    DB_USER: str = "simplenotes"
    DB_PASSWORD: str = "changeme"

    # Email
    EMAIL_FROM: str = "noreply@simplenotes.local"
    EMAIL_FROM_NAME: str = "SimpleNotes"
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAIL_ENABLE: bool = False
    EMAIL_VERIFICATION_REDIRECT_URL: str = "http://localhost:3000/verified"
    PASSWORD_RESET_REDIRECT_URL: str = "http://localhost:3000/reset-success"

    # Analytics
    ANALYTICS_ENABLE: bool = False
    ANALYTICS_WRITE_KEY: str | None = None

    # Backups
    BACKUP_ENABLE: bool = False
    BACKUP_BUCKET: str | None = None
    BACKUP_PROVIDER: str = "s3"

    model_config = SettingsConfigDict(env_file=os.path.join(BASE_DIR, "backend", ".env"), env_file_encoding="utf-8")

    @property
    def UPLOADS_DIR(self) -> Path:
        return UPLOADS_DIR

    @property
    def SYNC_DB_URL(self) -> str:
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
