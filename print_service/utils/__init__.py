import random
import re
from datetime import date, datetime, timedelta
from os.path import abspath, exists

from fastapi import File
from fastapi.exceptions import HTTPException
from sqlalchemy import func
from sqlalchemy.orm.session import Session

from print_service.models import File
from print_service.models import File as FileModel
from print_service.settings import Settings, get_settings
from PyPDF3 import PdfFileReader
from PyPDF3.utils import PyPdfError
import aiofiles
import io

settings: Settings = get_settings()


def generate_pin(session: Session):
    for i in range(15):
        pin = ''.join(random.choice(settings.PIN_SYMBOLS) for _ in range(settings.PIN_LENGTH))
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
    salt = ''.join(random.choice(settings.PIN_SYMBOLS) for _ in range(128))
    ext = re.findall(r'\w+', original_filename.split('.')[-1])[0]
    return f'{datestr}-{salt}.{ext}'


def get_file(dbsession, pin: str or list[str]):
    pin = [pin.upper()] if isinstance(pin, str) else tuple(p.upper() for p in pin)
    files: list[FileModel] = (
        dbsession.query(FileModel)
        .filter(func.upper(FileModel.pin).in_(pin))
        .order_by(FileModel.created_at.desc())
        .all()
    )
    if len(pin) != len(files):
        raise HTTPException(404, f'{len(pin) - len(files)} file(s) not found')

    result = []
    for f in files:
        path = abspath(settings.STATIC_FOLDER) + '/' + f.file
        if not exists(path):
            raise HTTPException(415, 'File has not uploaded yet')

        result.append({
            'filename': f.file,
            'options': {
                'pages': f.option_pages or '',
                'copies': f.option_copies or 1,
                'two_sided': f.option_two_sided or False,
            },
        })
    return result


async def check_pdf_ok(fullfile:str):
    async with aiofiles.open(fullfile, 'rb') as f:
        try:
            f = await f.read()
            pdf = PdfFileReader(io.BytesIO(f))
            info = pdf.getDocumentInfo()
            return bool(info)
        except PyPdfError:
            return False