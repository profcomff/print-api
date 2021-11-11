import re
from typing import Optional

from pydantic import BaseModel, validator
from pydantic.fields import Field


class PrintOptions(BaseModel):
    pages: Optional[str] = Field('', description='Страницы для печати', example='2-4,6')
    copies: Optional[int] = Field(1, description='Количество копий для печати')
    two_sided: Optional[bool] = Field(False, description='Включить печать с двух сторон листа')

    @validator('pages', pre=True, always=True)
    def validate_pages(cls, value: str):
        if value == '':
            return ''
        value = re.sub(r'\s+', '', value)
        value_arr = re.split(r'[-,]', value)
        if not value_arr == sorted(value_arr) or re.findall(r'[^0-9-,]', value) != []:
            raise ValueError('Pages must be formated as 2-5,7')
        return value


class SendInput(BaseModel):
    surname: str = Field(
        description='Фамилия',
        example='Иванов',
    )
    number: str = Field(
        description='Номер профсоюзного билета',
        example='1015000',
    )
    filename: str = Field(
        description='Название файла',
        example='filename.pdf',
    )
    options: Optional[PrintOptions]


class SendInputUpdate(BaseModel):
    options: Optional[PrintOptions]


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
