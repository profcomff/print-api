import io
import math
import random
import re
from datetime import date, datetime, timedelta
from os.path import abspath, exists

from fastapi import File
from fastapi.exceptions import HTTPException
from PyPDF4 import PdfFileReader
from sqlalchemy import func
from sqlalchemy.orm.session import Session

from print_service.exceptions import (
    FileNotFound,
    InvalidPageRequest,
    IsNotUpload,
    UnprocessableFileInstance,
)
from print_service.models import File
from print_service.models import File as FileModel
from print_service.models import PrintFact
from print_service.routes import exc_handlers
from print_service.settings import Settings, get_settings


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
    ext_list = re.findall(r'\w+', original_filename.split('.')[-1])
    if not ext_list:
        raise UnprocessableFileInstance()
    ext = ext_list[0]
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
        raise FileNotFound(len(pin) - len(files))

    result = []
    for f in files:
        path = abspath(settings.STATIC_FOLDER) + '/' + f.file
        if not exists(path):
            raise IsNotUpload()

        result.append(
            {
                'filename': f.file,
                'options': {
                    'pages': f.option_pages or '',
                    'copies': f.option_copies or 1,
                    'two_sided': f.option_two_sided or False,
                },
            }
        )
        _, number_of_pages = checking_for_pdf(f)
        if f.flatten_pages:
            if number_of_pages > max(f.flatten_pages):
                raise InvalidPageRequest()
        file_model = PrintFact(file_id=f.id, owner_id=f.owner_id, sheets_used=f.sheets_count)
        dbsession.add(file_model)
        dbsession.commit()
    return result


def checking_for_pdf(f: bytes) -> tuple[bool, int]:
    """_summary_

    Args:
        f (bytes): file to check

    Returns:
        tuple[bool, int]: The first argument returns whether the file is a valid pdf.
        The second argument returns the number of pages in the pdf document (0- if the check failed)
    """
    try:
        pdf_file = PdfFileReader(io.BytesIO(f))
        return True, pdf_file.getNumPages()
    except Exception:
        return False, 0
