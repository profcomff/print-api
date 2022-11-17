import re
from typing import List, Optional

from pydantic import BaseModel, validator
from pydantic.fields import Field


class PrintOptions(BaseModel):
    pages: str = Field('', description='Страницы для печати', example='2-4,6')
    copies: int = Field(1, description='Количество копий для печати')
    two_sided: bool = Field(False, description='Включить печать с двух сторон листа')

    @validator('pages', pre=True, always=True)
    def validate_pages(cls, value: str):
        if not isinstance(value, str):
            raise ValueError('Value must be str')
        value = re.sub(r'\s+', '', value)
        if value == '':
            return ''
        value_arr = re.split(r'[-,]', value)
        if not value_arr == sorted(value_arr) or re.findall(r'[^0-9-,]', value) != []:
            raise ValueError('Pages must be formated as 2-5,7')
        if value_arr[0] == '0' or value_arr[0] == '-':
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
    options: PrintOptions = PrintOptions()


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


class UserCreate(BaseModel):
    username: Optional[str]
    union_number: Optional[str]
    student_number: Optional[str]


class UpdateUserList(BaseModel):
    users: List[UserCreate]
    secret: str
