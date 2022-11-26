import random
import re
from datetime import date, datetime, timedelta
import PIL.Image
from sqlalchemy.orm.session import Session

from print_service.models import File
from print_service.settings import Settings, get_settings

from os import remove
import time
from io import BytesIO


settings: Settings = get_settings()


def generate_pin(session: Session):
    for i in range(15):
        pin = ''.join(random.choice(settings.PIN_SYMBOLS) for i in range(settings.PIN_LENGTH))
        cnt = (
            session.query(File)
            .filter(
                File.pin == pin,
                File.created_at + timedelta(hours=settings.STORAGE_TIME) >= datetime.utcnow(),
            )
            .count()
        )
        if cnt == 0:
            return pin
    else:
        raise RuntimeError('Can not create unique PIN')


def generate_filename(original_filename: str):
    datestr = date.today().isoformat()
    salt = ''.join(random.choice(settings.PIN_SYMBOLS) for i in range(128))
    ext = re.findall(r'\w+', original_filename.split('.')[-1])[0]
    return f'{datestr}-{salt}.{ext}'


#преобразует файл из картинки в pdf
def process_image(file,newFileName):
    image=PIL.Image.open(BytesIO(file)).convert("RGB")  
    if(image.width<image.height):
        image=image.rotate(90,expand=True)
    image.save(f"{newFileName}.pdf", "PDF", quality=100)
    #remove(filepath)# удаляем старый файл - картинку
        
