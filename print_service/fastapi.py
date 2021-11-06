from logging import getLogger
from os.path import abspath, exists
from typing import Any, Dict

import aiofiles
from fastapi import APIRouter, FastAPI, File, UploadFile
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_sqlalchemy import DBSessionMiddleware, db
from sqlalchemy import func

from print_service import __version__
from print_service.models import File as FileModel
from print_service.models import UnionMember
from print_service.schema import SendInput
from print_service.settings import Settings, get_settings
from print_service.utils import generate_filename, generate_pin


settings: Settings = get_settings()
logger = getLogger(__name__)

app = FastAPI(
    title='Сервис отправки заданий печати',
    description=(
        'Серверная часть сервиса отправки заданий на печать и получения ' 'файлов для печати с терминала'
    ),
    version=__version__,
    root_path=settings.ROOT,
)
app.add_middleware(DBSessionMiddleware, db_url=settings.DB_DSN)

origins = [
    "https://app.profcomff.com",
    "http://app.profcomff.com",
    "https://www.profcomff.com",
    "http://www.profcomff.com",
    "http://localhost",
    "http://localhost:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


print_router = APIRouter()


@print_router.get('/is_union_member')
async def check_union_member(surname: str, number: str):
    """
    """
    user = db.session.query(UnionMember).filter(
        func.upper(UnionMember.number) == number.upper(),
        func.upper(UnionMember.surname) == surname.upper(),
    ).one_or_none()
    return bool(user)


@print_router.post('/file', responses={403: {'detail': 'User error'}})
async def send(inp: SendInput):
    """Получить пин код для загрузки и скачивания файла.

    Полученный пин-код можно использовать в методах POST и GET `/file/{pin}`.
    """
    user = (
        db.session.query(UnionMember)
        .filter(
            func.upper(UnionMember.number) == inp.number.upper(),
            func.upper(UnionMember.surname) == inp.surname.upper(),
        )
        .one_or_none()
    )
    if not user:
        raise HTTPException(403, 'User not found in trade union list')

    try:
        pin = generate_pin(db.session)
    except RuntimeError:
        raise HTTPException(500, 'Can not generate PIN. Too many users?')
    filename = generate_filename(inp.filename)

    file = FileModel(pin=pin, file=filename)
    file.owner = user
    db.session.add(file)
    db.session.commit()

    return {'pin': pin}


@print_router.post(
    '/file/{pin:str}',
    responses={
        404: {'detail': 'Pin not found'},
        415: {'detail': 'File error'},
    },
)
async def upload_file(pin: str, file: UploadFile = File(...)):
    """Загрузить файл на сервер.

    Требует пин-код, полученный в методе POST `/file`. Файл для пин-кода можно
    загрузить лишь один раз. Файл должен быть размером до 5 000 000 байт
    (меняется в настройках сервера).
    """
    if file == ...:
        raise HTTPException(400, 'No file recieved')
    file_model = (
        db.session.query(FileModel)
        .filter(func.upper(FileModel.pin) == pin.upper())
        .order_by(FileModel.created_at.desc())
        .one_or_none()
    )
    if not file_model:
        raise HTTPException(404, f'Pin {pin} not found')

    if file.content_type not in settings.CONTENT_TYPES:
        raise HTTPException(
            415,
            f'Only {", ".join(settings.CONTENT_TYPES)} files allowed, but {file.content_type} recieved',
        )

    path = abspath(settings.STATIC_FOLDER) + '/' + file_model.file
    if exists(path):
        raise HTTPException(415, 'File already uploaded')

    async with aiofiles.open(path, 'wb') as saved_file:
        memory_file = await file.read()
        if len(memory_file) > settings.MAX_SIZE:
            raise HTTPException(415, f'File too large, {settings.MAX_SIZE} bytes allowed')
        await saved_file.write(memory_file)
    await file.close()

    return {'pin': pin}


@print_router.get('/file/{pin:str}', responses={404: {'detail': 'Pin not found'}})
async def print(pin: str):
    """Получить файл для печати.

    Требует пин-код, полученный в методе POST `/file`. Файл можно скачать
    бесконечное количество раз в течение 7 дней после загрузки (меняется в
    настройках сервера).
    """
    file_model = (
        db.session.query(FileModel)
        .filter(func.upper(FileModel.pin) == pin.upper())
        .order_by(FileModel.created_at.desc())
        .one_or_none()
    )
    if not file_model:
        raise HTTPException(404, f'Pin {pin} not found')

    path = abspath(settings.STATIC_FOLDER) + '/' + file_model.file
    if not exists(path):
        raise HTTPException(415, 'File has not uploaded yet')

    return {'filename': file_model.file}


app.include_router(print_router, prefix='')
app.mount('/static', StaticFiles(directory='static'), 'static')
