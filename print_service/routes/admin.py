import json
import logging
import random
from asyncio import sleep
from datetime import datetime, timedelta

from fastapi import APIRouter, Header, WebSocket, HTTPException
from fastapi_sqlalchemy import db
from pydantic import conlist
from redis import Redis

from print_service.schema import BaseModel
from print_service.settings import Settings, get_settings
from print_service.utils import get_file


logger = logging.getLogger(__name__)
settings: Settings = get_settings()
router = APIRouter()


class AdminAuth(BaseModel):
    secret: str


class UpdateInput(AdminAuth):
    terminal_token: str


class InstantCommandSender:
    def __init__(self, settings: Settings = None) -> None:
        settings = settings or get_settings()
        self.redis: Redis = Redis.from_url(settings.REDIS_DSN)

    def update(self, terminal_token: str):
        terminal = self.redis.get(terminal_token)
        if terminal:
            return None
        self.redis.set(terminal_token, json.dumps({'manual_update': True}))
        return True


@router.post("/reboot")
async def instant_print(input: UpdateInput):
    if input.secret != settings.SECRET_KEY:
        raise HTTPException(403, {"status": "error", "detail": "Incorrect secret"})
    sender = InstantCommandSender()
    if sender.update(input.terminal_token):
        sender.redis.close()
        return {'status': 'ok'}
    sender.redis.close()
    raise HTTPException(400, 'Terminal not found by token')
