import string
from functools import lru_cache
from typing import List

from pydantic import BaseSettings
from pydantic.networks import HttpUrl, PostgresDsn


class Settings(BaseSettings):
    ROOT: HttpUrl | None = None
    DB_DSN: PostgresDsn = 'postgresql://postgres@localhost:5432/postgres'

    CONTENT_TYPES: List[str] = ['application/pdf']
    MAX_SIZE: int = 5000000  # Максимальный размер файла в байтах
    STORAGE_TIME: int = 7 * 24  # Время хранения файла в часах
    STATIC_FOLDER: str = './static'

    PIN_SYMBOLS: str = string.ascii_uppercase + string.digits
    PIN_LENGTH: int = 6


@lru_cache()
def get_settings() -> Settings:
    return Settings()
