import random
import re
from datetime import date, datetime, timedelta
from os.path import abspath, exists

from fastapi import File
from fastapi.exceptions import HTTPException
from sqlalchemy import func
from sqlalchemy.orm.session import Session

from print_service import __version__
from print_service.models import File
from print_service.models import File as FileModel
from print_service.settings import Settings, get_settings

from PIL import Image
from io import BytesIO
from fpdf import FPDF



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

#преобразует файл из картинки в pdf
def process_image(file :str,newFileName :str):
    img=Image.open(BytesIO(file)).convert("RGB")  
    if(img.width>img.height):
        img=img.rotate(90,expand=True)
    #img.save(f"{newFileName}.pdf", "PDF", quality=100)
    pdf = FPDF()
    pdf.add_page()

    FPDF.set_left_margin(pdf,0)
    FPDF.set_right_margin(pdf,0)
    FPDF.set_top_margin(pdf,10)
    
    k=min(pdf.eph/img.height,pdf.epw/img.width)
    wid=img.width*k
    heig=img.height*k
    #print(wid,heig,pdf.epw,pdf.eph, (pdf.eph-heig)/2)
    pdf.image(img, x=(pdf.epw-wid)/2,y=(pdf.eph-heig)/2+15,h=heig, w=wid) 
    pdf.output(f"{newFileName}.pdf")
