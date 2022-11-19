import logging
from fastapi import APIRouter
from print_service.settings import get_settings
from print_service.schema import BaseModel


class QrPrint(BaseModel):
    token: str
    files: list[str]


logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


@router.websocket("/terminal", "Send new QR codes and files to print")
def ws():
    pass


@router.post("/print")
def read():
    pass
