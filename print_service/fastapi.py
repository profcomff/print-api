from logging import getLogger
from os.path import abspath, exists
from typing import Any, Dict

import aiofiles
from fastapi import APIRouter, FastAPI, File, UploadFile
from fastapi.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi_sqlalchemy import DBSessionMiddleware, db
from sqlalchemy import func

from print_service import __version__
from print_service.models import File as FileModel
from print_service.models import UnionMember
from print_service.settings import Settings, get_settings
from print_service.utils import generate_filename, generate_pin


settings: Settings = get_settings()
logger = getLogger(__name__)

app = FastAPI(
    title='Print service',
    description='Service to send print docs and recieve them from terminal',
    version=__version__,
    root_path=settings.ROOT,
)
app.add_middleware(DBSessionMiddleware, db_url=settings.DB_DSN)

print_router = APIRouter()


@print_router.post('/file', responses={403: {'detail': 'User error'}})
async def send(surname: str, number: str, filename: str):
    user = (
        db.session.query(UnionMember)
        .filter(
            func.upper(UnionMember.number) == number.upper(),
            func.upper(UnionMember.surname) == surname.upper(),
        )
        .one_or_none()
    )
    if not user:
        raise HTTPException(403, 'User not found in trade union list')

    pin = generate_pin()
    filename = generate_filename(filename)

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
async def upload_file(pin: str, file: UploadFile = File(None)):
    file_model = (
        db.session.query(FileModel).filter(func.upper(FileModel.pin) == pin.upper()).one_or_none()
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
    file_model = (
        db.session.query(FileModel).filter(func.upper(FileModel.pin) == pin.upper()).one_or_none()
    )
    if not file_model:
        raise HTTPException(404, f'Pin {pin} not found')

    path = abspath(settings.STATIC_FOLDER) + '/' + file_model.file
    if not exists(path):
        raise HTTPException(415, 'File already uploaded')

    return {'filename': file_model.file}


app.include_router(print_router, prefix='')
app.mount('/static', StaticFiles(directory='static'), 'static')
