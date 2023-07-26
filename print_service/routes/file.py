import logging
import re
from os.path import abspath, exists

import aiofiles
import aiofiles.os
from fastapi import APIRouter, File, UploadFile
from fastapi.exceptions import HTTPException
from fastapi.params import Depends
from fastapi_sqlalchemy import db
from pydantic import Field, field_validator
from sqlalchemy import func, or_

from print_service.base import StatusResponseModel
from print_service.exceptions import (
    AlreadyUploaded,
    FileIsNotReceived,
    InvalidPageRequest,
    InvalidType,
    IsCorrupted,
    NotInUnion,
    PINGenerateError,
    PINNotFound,
    TooLargeSize,
    TooManyPages,
    UnprocessableFileInstance,
    UserNotFound,
)
from print_service.models import File as FileModel
from print_service.models import UnionMember
from print_service.schema import BaseModel
from print_service.settings import Settings, get_settings
from print_service.utils import checking_for_pdf, generate_filename, generate_pin, get_file


logger = logging.getLogger(__name__)
router = APIRouter()


# region Schemas
class PrintOptions(BaseModel):
    pages: str = Field('', description='Страницы для печати', example='2-4,6')
    copies: int = Field(1, description='Количество копий для печати')
    two_sided: bool = Field(False, description='Включить печать с двух сторон листа')

    @field_validator('pages', mode='before')
    def validate_pages(cls, value: str):
        if not isinstance(value, str):
            raise ValueError('Value must be str')
        value = re.sub(r'\s+', '', value)
        if value == '':
            return ''
        value_arr = re.split(r'[-,]', value)
        if not value_arr == sorted(value_arr) or re.findall(r'[^0-9-,]', value) != []:
            raise ValueError('Pages must be formated as 2-5,7')
        if value_arr[0] == '0' or value_arr[0] == '':
            raise ValueError('Can not print negative and zero pages')
        return value


class SendInput(BaseModel):
    surname: str = Field(
        description='Фамилия',
        example='Иванов',
    )
    number: str = Field(
        description='Номер профсоюзного или студенческого билетов',
        example='1015000',
    )
    filename: str = Field(
        description='Название файла',
        example='filename.pdf',
    )
    source: str
    options: PrintOptions = PrintOptions()


class SendInputUpdate(BaseModel):
    options: PrintOptions | None = None


class SendOutput(BaseModel):
    pin: str = Field(
        description='Пин-код, который используется для манипуляции файлами',
        example='OF72I1',
    )
    options: PrintOptions


class ReceiveOutput(BaseModel):
    filename: str = Field(
        description='Название файла, который можно запросить по адресу https://app.profcomff.com/print/static/{filename}',
        example='2021-11-02-ZMNF5V...9.pdf',
    )
    options: PrintOptions


# endregion


# region handlers
@router.post(
    '',
    responses={
        403: {'model': StatusResponseModel, 'detail': 'User error'},
        500: {'model': StatusResponseModel, 'detail': 'PIN generate error'},
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
    user = user.filter(
        or_(
            func.upper(UnionMember.student_number) == inp.number.upper(),
            func.upper(UnionMember.union_number) == inp.number.upper(),
        ),
        func.upper(UnionMember.surname) == inp.surname.upper(),
    ).one_or_none()
    if not user:
        raise NotInUnion()
    try:
        pin = generate_pin(db.session)
    except RuntimeError:
        raise PINGenerateError()
    filename = generate_filename(inp.filename)
    file_model = FileModel(pin=pin, file=filename, source=inp.source)
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
        400: {'model': StatusResponseModel, 'detail': 'File is not received'},
        404: {'model': StatusResponseModel, 'detail': 'Pin not found'},
        415: {'model': StatusResponseModel, 'detail': 'File error'},
        413: {'model': StatusResponseModel, 'detail': 'Too large file'},
        416: {'model': StatusResponseModel, 'detail': 'Invalid page request'},
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
        raise FileIsNotReceived()
    file_model = (
        db.session.query(FileModel)
        .filter(func.upper(FileModel.pin) == pin.upper())
        .order_by(FileModel.created_at.desc())
        .one_or_none()
    )
    if not file_model:
        await file.close()
        raise PINNotFound(pin)
    if file.content_type not in settings.CONTENT_TYPES:
        raise InvalidType()
    path = abspath(settings.STATIC_FOLDER) + '/' + file_model.file
    if exists(path):
        await file.close()
        raise AlreadyUploaded()

    async with aiofiles.open(path, 'wb') as saved_file:
        memory_file = await file.read()
        if len(memory_file) > settings.MAX_SIZE:
            await file.close()
            raise TooLargeSize()
        await saved_file.write(memory_file)
    pdf_ok, number_of_pages = checking_for_pdf(memory_file)
    file_model.number_of_pages = number_of_pages
    db.session.commit()
    if not pdf_ok:
        await aiofiles.os.remove(path)
        await file.close()
        raise IsCorrupted()
    if file_model.flatten_pages:
        if number_of_pages < max(file_model.flatten_pages):
            await aiofiles.os.remove(path)
            await file.close()
            raise InvalidPageRequest()
    if file_model.sheets_count > settings.MAX_PAGE_COUNT:
        await aiofiles.os.remove(path)
        await file.close()
        raise TooManyPages()
    await file.close()

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
        404: {'model': StatusResponseModel, 'detail': 'Pin not found'},
        413: {'model': StatusResponseModel, 'detail': 'Too many pages'},
        416: {'model': StatusResponseModel, 'detail': 'Invalid page request'},
    },
    response_model=SendOutput,
)
async def update_file_options(
    pin: str, inp: SendInputUpdate, settings: Settings = Depends(get_settings)
):
    """Обновляет настройки печати.

    Требует пин-код, полученный в методе POST `/file`. Обновлять настройки
    можно бесконечное количество раз. Можно изменять настройки по одной."""
    options = inp.options.model_dump(exclude_unset=True)
    file_model = (
        db.session.query(FileModel)
        .filter(func.upper(FileModel.pin) == pin.upper())
        .order_by(FileModel.created_at.desc())
        .one_or_none()
    )
    print(options)
    if not file_model:
        raise PINNotFound(pin)
    file_model.option_pages = options.get('pages') or file_model.option_pages
    file_model.option_copies = options.get('copies') or file_model.option_copies
    file_model.option_two_sided = (
        v if (v := options.get('two_sided')) is not None else file_model.option_two_sided
    )
    db.session.commit()
    if file_model.flatten_pages:
        if file_model.number_of_pages < max(file_model.flatten_pages):
            raise InvalidPageRequest
    if file_model.sheets_count > settings.MAX_PAGE_COUNT:
        raise TooManyPages()
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
        404: {'model': StatusResponseModel, 'detail': 'Pin not found'},
        415: {'model': StatusResponseModel, 'detail': 'File error'},
        416: {'model': StatusResponseModel, 'detail': 'Invalid page request'},
    },
    response_model=ReceiveOutput,
)
async def print_file(pin: str, settings: Settings = Depends(get_settings)):
    """Получить файл для печати.

    Требует пин-код, полученный в методе POST `/file`. Файл можно скачать
    бесконечное количество раз в течение 7 дней после загрузки (меняется в
    настройках сервера).
    """
    return get_file(db.session, pin)[0]


# endregion
