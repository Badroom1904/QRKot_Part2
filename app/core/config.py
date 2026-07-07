import os
from typing import Optional

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Настройки приложения."""

    DATABASE_URL: str = os.getenv(
        'DATABASE_URL',
        'sqlite+aiosqlite:///./fastapi.db'
    )

    SECRET_KEY: str = os.getenv('SECRET_KEY', 'supersecretkeychangeit')

    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'

    yandex_disk_token: Optional[str] = os.getenv('YANDEX_DISK_TOKEN')
    report_format: str = os.getenv('REPORT_FORMAT', '%Y-%m-%d_%H-%M')

    class Config:
        """Конфигурация Pydantic Settings."""
        env_file = '.env'
        case_sensitive = False


settings = Settings()