import os
from typing import Optional

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Настройки приложения."""

    # Настройки базы данных
    DATABASE_URL: str = os.getenv(
        'DATABASE_URL',
        'sqlite+aiosqlite:///./fastapi.db'
    )

    SECRET_KEY: str = os.getenv('SECRET_KEY', 'supersecretkeychangeit')

    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'

    YANDEX_DISK_TOKEN: Optional[str] = os.getenv('YANDEX_DISK_TOKEN')
    REPORT_FORMAT: str = os.getenv('REPORT_FORMAT', '%Y-%m-%d_%H-%M')

    class Config:
        """Конфигурация Pydantic Settings."""
        env_file = '.env'
        case_sensitive = True


settings = Settings()