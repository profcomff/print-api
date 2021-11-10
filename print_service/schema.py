from pydantic import BaseModel
from pydantic.fields import Field
from pydantic.networks import AnyHttpUrl


class SendInput(BaseModel):
    surname: str= Field(
        description='Фамилия',
        example='Иванов',
    )
    number: str= Field(
        description='Номер профсоюзного билета',
        example='1015000',
    )
    filename: str= Field(
        description='Название файла',
        example='filename.pdf',
    )


class SendOutput(BaseModel):
    pin: str = Field(
        description='Пин-код, который используется для манипуляции файлами',
        example='OF72I1',
    )


class RecieveOutput(BaseModel):
    filename: AnyHttpUrl = Field(
        description='Путь, по которому файл можно скачать',
        example='https://app.profcomff.com/print/static/2021-11-02-ZMNF5V...9.pdf',
    )
