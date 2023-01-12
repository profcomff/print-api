import random
from datetime import date, datetime, timedelta
from PIL import Image
from sqlalchemy.orm.session import Session

from print_service.models import File
from print_service.settings import Settings, get_settings
from os.path import  splitext
import time
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
    ext = splitext(original_filename)[1]
    ext.replace(".","")#при загрузке из тестов появляется лишняя точка
    return f'{datestr}-{salt}.{ext}'


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
    pdf.output(f"{newFileName}pdf")

        
