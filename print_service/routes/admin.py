import json
import logging

from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends, HTTPException
from redis import Redis

from print_service.exceptions import TerminalTokenNotFound
from print_service.schema import BaseModel
from print_service.settings import Settings, get_settings


logger = logging.getLogger(__name__)
settings: Settings = get_settings()
router = APIRouter()


class UpdateInput(BaseModel):
    terminal_token: str


class RebootInput(BaseModel):
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

    def reboot(self, terminal_token: str):
        terminal = self.redis.get(terminal_token)
        if terminal:
            return None
        self.redis.set(terminal_token, json.dumps({'reboot': True}))
        return True


@router.post("/update")
async def manual_update_terminal(
    input: UpdateInput, user=Depends(UnionAuth(scopes=["print.terminal.service"]))
):
    logger.info(f"User {user} updated terminal")
    sender = InstantCommandSender()
    if sender.update(input.terminal_token):
        sender.redis.close()
        return {'status': 'ok'}
    sender.redis.close()
    raise TerminalTokenNotFound()


@router.post("/reboot")
async def reboot_terminal(
    input: RebootInput, user=Depends(UnionAuth(scopes=["print.terminal.service"]))
):
    logger.info(f"User {user} rebooted terminal")
    sender = InstantCommandSender()
    if sender.reboot(input.terminal_token):
        sender.redis.close()
        return {'status': 'ok'}
    sender.redis.close()
    raise TerminalTokenNotFound()
