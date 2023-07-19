import json
import logging
import random
from asyncio import sleep
from datetime import datetime, timedelta
from typing import Set

from fastapi import APIRouter, Header, HTTPException, WebSocket
from fastapi_sqlalchemy import db
from pydantic import Field
from redis import Redis
from typing_extensions import Annotated

from print_service.exceptions import FileNotFound, InvalidPageRequest, IsNotUploaded, TerminalQRNotFound
from print_service.schema import BaseModel
from print_service.settings import Settings, get_settings
from print_service.utils import get_file


logger = logging.getLogger(__name__)
settings: Settings = get_settings()
router = APIRouter()


class InstantPrintCreate(BaseModel):
    qr_token: str
    files: Annotated[Set[str], Field(min_length=1, max_length=10)]


class InstantPrintSender:
    def __init__(self, settings: Settings = None) -> None:
        settings = settings or get_settings()
        self.redis: Redis = Redis.from_url(str(settings.REDIS_DSN))

    def send(self, qr_token: str, files: list[str]):
        terminal = self.redis.get(qr_token)
        if not terminal:
            return None
        self.redis.delete(qr_token)
        old = self.redis.get(terminal)
        if old:
            return None
        files = get_file(db.session, files)
        self.redis.set(terminal, json.dumps({'files': files}))
        return files


class InstantPrintFetcher:
    def __init__(self, terminal_token: str, settings: Settings = None) -> None:
        self.terminal_token = terminal_token
        settings = settings or get_settings()
        self.redis = Redis.from_url(str(settings.REDIS_DSN))
        self.ttl = settings.QR_TOKEN_TTL
        self.delay = settings.QR_TOKEN_DELAY
        self.symbols = settings.QR_TOKEN_SYMBOLS
        self.length = settings.QR_TOKEN_LENGTH

    def new_qr(self):
        for _ in range(5):
            qr_token = ''.join(random.choice(self.symbols) for _ in range(self.length))
            if not self.redis.get(qr_token):  # If this qr already exists, generate new
                break
        self.redis.set(
            qr_token, self.terminal_token, ex=self.ttl + self.delay
        )  # Send token to redis +ttl
        return qr_token

    async def get_tasks(self) -> dict[str, list[str]]:
        until = datetime.utcnow() + timedelta(seconds=self.ttl)
        while datetime.utcnow() < until:
            raw_value: bytes = self.redis.get(self.terminal_token)
            if raw_value:
                self.redis.delete(self.terminal_token)
                break
            await sleep(0.5)
        else:
            return {}
        return json.loads(raw_value)

    def __aiter__(self):
        return self

    async def __anext__(self):
        value = await self.get_tasks()
        qr_token = self.new_qr()
        result = {"qr_token": qr_token, **value}
        return result


redis_conn = InstantPrintSender()


@router.post("")
async def instant_print(options: InstantPrintCreate):
    options.qr_token = options.qr_token.removeprefix(str(settings.QR_TOKEN_PREFIX))
    if redis_conn.send(**options.dict()):
        return {'status': 'ok'}
    raise TerminalQRNotFound()


@router.websocket("")
async def instant_print_terminal_connection(
    websocket: WebSocket,
    authorization: str = Header(),
):
    await websocket.accept()
    manager = InstantPrintFetcher(authorization.removeprefix("token "))
    await websocket.send_text(json.dumps({"qr_token": str(settings.QR_TOKEN_PREFIX) + manager.new_qr()}))
    async for task in manager:
        task['qr_token'] = str(settings.QR_TOKEN_PREFIX) + task['qr_token']
        await websocket.send_text(json.dumps(task))
