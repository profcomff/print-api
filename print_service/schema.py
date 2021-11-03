from pydantic import BaseModel


class SendInput(BaseModel):
    surname: str
    number: str
    filename: str
