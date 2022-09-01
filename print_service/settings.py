import string
from functools import lru_cache
from typing import List, Optional

from pydantic import BaseSettings
from pydantic.networks import HttpUrl, PostgresDsn


class Settings(BaseSettings):
    ROOT: Optional[HttpUrl] = None
    DB_DSN: PostgresDsn = 'postgresql://postgres@localhost:5432/postgres'

    CONTENT_TYPES: List[str] = ['application/pdf']
    MAX_SIZE: int = 5000000  # Максимальный размер файла в байтах
    STORAGE_TIME: int = 7 * 24  # Время хранения файла в часах
    STATIC_FOLDER: str = './static'

    PIN_SYMBOLS: str = string.ascii_uppercase + string.digits
    PIN_LENGTH: int = 6

    CORS_ALLOW_ORIGINS: list[str] = ['*']
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ['*']
    CORS_ALLOW_HEADERS: list[str] = ['*']


@lru_cache()
def get_settings() -> Settings:
    return Settings()
