import string
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import BaseConfig
from pydantic.networks import HttpUrl, PostgresDsn


class Settings(BaseConfig):
    DB_DSN: PostgresDsn = 'postgresql://postgres@localhost:5432/postgres'

    ROOT: HttpUrl = 'https://api.profcomff.com/print'
    OK_PAGE: HttpUrl = "https://api.profcomff.com/print/static/pin?pin={}"
    FAIL_PAGE: HttpUrl = "https://api.profcomff.com/print/static/fail?description={}"

    CONTENT_TYPES: List[str] = ['application/pdf']
    MAX_SIZE: int = 5000000
    STATIC_FOLDER: str = './static'

    PIN_SYMBOLS: str = string.ascii_uppercase + string.digits
    PIN_LENGTH: int = 6


@lru_cache()
def get_settings() -> Settings:
    return Settings()
