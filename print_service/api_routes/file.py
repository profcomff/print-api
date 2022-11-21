import logging
from os.path import abspath, exists
from os import remove

import aiofiles
from fastapi import APIRouter, File, UploadFile
from fastapi.exceptions import HTTPException
from fastapi.params import Depends
from fastapi_sqlalchemy import db
from sqlalchemy import func, or_

from print_service import __version__
from print_service.models import File as FileModel
from print_service.models import UnionMember
from print_service.schema import ReceiveOutput, SendInput, SendInputUpdate, SendOutput
from print_service.settings import Settings, get_settings
from print_service.utils import generate_filename, generate_pin
from print_service.utils import process_image

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    '',
    responses={
        403: {'detail': 'User error'},
    },
    response_model=SendOutput,
)
async def send(inp: SendInput, settings: Settings = Depends(get_settings)):
    """Получить пин код для загрузки и скачивания файла.

    Полученный пин-код можно использовать в методах POST и GET `/file/{pin}`.
    """
    user = db.session.query(UnionMember)
    if not settings.ALLOW_STUDENT_NUMBER:
        user = user.filter(UnionMember.union_number != None)
    user = (
        user.filter(
            or_(
                func.upper(UnionMember.student_number) == inp.number.upper(),
                func.upper(UnionMember.union_number) == inp.number.upper(),
            ),
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
    file_model = FileModel(pin=pin, file=filename)
    file_model.owner = user
    file_model.option_copies = inp.options.copies
    file_model.option_pages = inp.options.pages
    file_model.option_two_sided = inp.options.two_sided
    db.session.add(file_model)
    db.session.commit()

    return {
        'pin': file_model.pin,
        'options': {
            'pages': file_model.option_pages,
            'copies': file_model.option_copies,
            'two_sided': file_model.option_two_sided,
        },
    }


@router.post(
    '/{pin:str}',
    responses={
        404: {'detail': 'Pin not found'},
        415: {'detail': 'File error'},
    },
    response_model=SendOutput,
)
async def upload_file(
    pin: str, file: UploadFile = File(...), settings: Settings = Depends(get_settings)
):
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
    #надо конвертировать картинку. Нельзя отправлять ответ что все готово до завершения этого, а то клиент может попросить распечатать еще не готовый файл
    #проверка на то, чтобы не конвертировать pdf в pdf
    fileFormat="pdf"
    if(file.content_type=="image/png"):
        fileFormat="png"
    if(file.content_type=="image/jpeg"):
        fileFormat="jpg"
    if(fileFormat!="pdf"):
        process_image(path,path.replace(fileFormat,"pdf"))
        remove(path)# удаляем старый файл - картинку


    return {
        'pin': pin,
        'options': {
            'pages': file_model.option_pages,
            'copies': file_model.option_copies,
            'two_sided': file_model.option_two_sided,
        },
    }


@router.patch(
    '/{pin:str}',
    responses={
        404: {'detail': 'Pin not found'},
    },
    response_model=SendOutput,
)
async def update_file_options(
    pin: str, inp: SendInputUpdate, settings: Settings = Depends(get_settings)
):
    """Обновляет настройки печати.

    Требует пин-код, полученный в методе POST `/file`. Обновлять настройки
    можно бесконечное количество раз. Можно изменять настройки по одной."""
    options = inp.options.dict(exclude_unset=True)
    file_model = (
        db.session.query(FileModel)
        .filter(func.upper(FileModel.pin) == pin.upper())
        .order_by(FileModel.created_at.desc())
        .one_or_none()
    )
    print(options)
    if not file_model:
        raise HTTPException(404, f'Pin {pin} not found')
    file_model.option_pages = options.get('pages') or file_model.option_pages
    file_model.option_copies = options.get('copies') or file_model.option_copies
    file_model.option_two_sided = options.get('two_sided') or file_model.option_two_sided
    db.session.commit()
    return {
        'pin': file_model.pin,
        'options': {
            'pages': file_model.option_pages,
            'copies': file_model.option_copies,
            'two_sided': file_model.option_two_sided,
        },
    }


@router.get(
    '/{pin:str}',
    responses={
        404: {'detail': 'Pin not found'},
        415: {'detail': 'File error'},
    },
    response_model=ReceiveOutput,
)
async def print_file(pin: str, settings: Settings = Depends(get_settings)):
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
    #если файл был конвертирован ранее, то он уже лежит как пфд
    file_model.file=file_model.file.replace(".png",".pdf")
    file_model.filename=file_model.file.replace(".jpg",".pdf")
    

    path = abspath(settings.STATIC_FOLDER) + '/' + file_model.file
    if not exists(path):
        raise HTTPException(415, 'File has not uploaded yet'+ file_model.file)
    return {
        'filename': file_model.file,
        'options': {
            'pages': file_model.option_pages or '',
            'copies': file_model.option_copies or 1,
            'two_sided': file_model.option_two_sided or False,
        },
    }
