from pydantic import BaseModel


class StatusResponseModel(BaseModel):
    status: str
    message: str
    ru: str


__all__ = ('BaseModel', 'StatusResponseModel')
