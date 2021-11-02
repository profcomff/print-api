import random
import re
from datetime import date

from print_service.settings import Settings, get_settings


settings: Settings = get_settings()


def generate_pin():
    return ''.join(random.choice(settings.PIN_SYMBOLS) for i in range(settings.PIN_LENGTH))


def generate_filename(original_filename: str):
    datestr = date.today().isoformat()
    salt = ''.join(random.choice(settings.PIN_SYMBOLS) for i in range(128))
    ext = re.findall(r'\w+', original_filename.split('.')[-1])[0]
    return f'{datestr}-{salt}.{ext}'
