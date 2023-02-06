import string
from functools import lru_cache
from typing import List

from pydantic import BaseSettings, DirectoryPath, PostgresDsn, RedisDsn, AnyUrl


class Settings(BaseSettings):
    DB_DSN: PostgresDsn = 'postgresql://postgres@localhost:5432/postgres'#'postgresql://postgres:1234@localhost:5432/postgres'
    REDIS_DSN: RedisDsn = 'redis://localhost:6379/0'

    CONTENT_TYPES: List[str] = ['application/pdf']
    MAX_SIZE: int = 5000000  # Максимальный размер файла в байтах
    STORAGE_TIME: int = 7 * 24  # Время хранения файла в часах
    STATIC_FOLDER: str  = "static"
    ALLOW_STUDENT_NUMBER: bool = False

    PIN_SYMBOLS: str = string.ascii_uppercase + string.digits
    PIN_LENGTH: int = 6

    CORS_ALLOW_ORIGINS: list[str] = ['*']
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ['*']
    CORS_ALLOW_HEADERS: list[str] = ['*']

    QR_TOKEN_PREFIX: str = ""
    QR_TOKEN_SYMBOLS: str = string.ascii_uppercase + string.digits
    QR_TOKEN_LENGTH: int = 6
    QR_TOKEN_TTL: int = 30  # Show time of QR code in seconds
    QR_TOKEN_DELAY: int = 5  # How long QR code valid after hide in seconds

    AUTH_URL: AnyUrl = "https://auth.api.test.profcomff.com/"

    class Config:
        env_file = '.env'


@lru_cache()
def get_settings() -> Settings:
    return Settings()
