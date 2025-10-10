import json
import logging
from typing import List, Optional

from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends, HTTPException
from fastapi_sqlalchemy import db
from redis import Redis

from print_service.exceptions import TerminalTokenNotFound
from print_service.models import UnionMember, File as FileModel, PrintFact
from print_service.schema import BaseModel
from print_service.settings import Settings, get_settings


logger = logging.getLogger(__name__)
settings: Settings = get_settings()
router = APIRouter()


class UpdateInput(BaseModel):
    terminal_token: str


class RebootInput(BaseModel):
    terminal_token: str





class UnionMemberResponse(BaseModel):
    id: int
    surname: str
    union_number: Optional[str]
    student_number: Optional[str]
    is_deleted: bool


class FileResponse(BaseModel):
    id: int
    pin: str
    file: str
    owner_id: int
    is_deleted: bool


class PrintFactResponse(BaseModel):
    id: int
    file_id: int
    owner_id: int
    sheets_used: Optional[int]
    is_deleted: bool


class InstantCommandSender:
    def __init__(self, settings: Settings = None) -> None:
        settings = settings or get_settings()
        self.redis: Redis = Redis.from_url(str(settings.REDIS_DSN))

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


# Soft Delete Management Endpoints

@router.get("/users", response_model=List[UnionMemberResponse])
async def get_all_users(
    include_deleted: bool = False,
    user=Depends(UnionAuth(scopes=["print.admin.users.read"]))
):
    logger.info(f"User {user} requested all users")
    users = UnionMember.query(session=db.session, with_deleted=include_deleted).all()
    return [
        UnionMemberResponse(
            id=u.id,
            surname=u.surname,
            union_number=u.union_number,
            student_number=u.student_number,
            is_deleted=u.is_deleted,
        )
        for u in users
    ]


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    user=Depends(UnionAuth(scopes=["print.admin.users.delete"]))
):
    logger.info(f"User {user} deleted user {user_id}")
    UnionMember.delete(user_id, session=db.session)
    db.session.commit()
    return {'status': 'ok', 'message': f'User {user_id} soft deleted'}


@router.post("/users/{user_id}/restore")
async def restore_user(
    user_id: int,
    user=Depends(UnionAuth(scopes=["print.admin.users.restore"]))
):
    logger.info(f"User {user} restored user {user_id}")
    db_user = UnionMember.get(user_id, session=db.session, with_deleted=True)
    if not db_user.is_deleted:
        raise HTTPException(status_code=400, detail="User is not deleted")
    
    db_user.is_deleted = False
    db.session.commit()
    return {'status': 'ok', 'message': f'User {user_id} restored'}


@router.get("/files", response_model=List[FileResponse])
async def get_all_files(
    include_deleted: bool = False,
    user=Depends(UnionAuth(scopes=["print.admin.files.read"]))
):
    """Получить список всех файлов (включая удаленных, если указано)"""
    logger.info(f"User {user} requested all files")
    files = FileModel.query(session=db.session, with_deleted=include_deleted).all()
    return [
        FileResponse(
            id=f.id,
            pin=f.pin,
            file=f.file,
            owner_id=f.owner_id,
            is_deleted=f.is_deleted,
        )
        for f in files
    ]


@router.delete("/files/{file_id}")
async def delete_file(
    file_id: int,
    user=Depends(UnionAuth(scopes=["print.admin.files.delete"]))
):
    """Мягкое удаление файла"""
    logger.info(f"User {user} deleted file {file_id}")
    FileModel.delete(file_id, session=db.session)
    db.session.commit()
    return {'status': 'ok', 'message': f'File {file_id} soft deleted'}


@router.post("/files/{file_id}/restore")
async def restore_file(
    file_id: int,
    user=Depends(UnionAuth(scopes=["print.admin.files.restore"]))
):
    """Восстановление мягко удаленного файла"""
    logger.info(f"User {user} restored file {file_id}")
    db_file = FileModel.get(file_id, session=db.session, with_deleted=True)
    if not db_file.is_deleted:
        raise HTTPException(status_code=400, detail="File is not deleted")
    
    db_file.is_deleted = False
    db.session.commit()
    return {'status': 'ok', 'message': f'File {file_id} restored'}


@router.get("/print-facts", response_model=List[PrintFactResponse])
async def get_all_print_facts(
    include_deleted: bool = False,
    user=Depends(UnionAuth(scopes=["print.admin.print_facts.read"]))
):
    """Получить список всех фактов печати (включая удаленных, если указано)"""
    logger.info(f"User {user} requested all print facts")
    facts = PrintFact.query(session=db.session, with_deleted=include_deleted).all()
    return [
        PrintFactResponse(
            id=pf.id,
            file_id=pf.file_id,
            owner_id=pf.owner_id,
            sheets_used=pf.sheets_used,
            is_deleted=pf.is_deleted,
        )
        for pf in facts
    ]


@router.delete("/print-facts/{print_fact_id}")
async def delete_print_fact(
    print_fact_id: int,
    user=Depends(UnionAuth(scopes=["print.admin.print_facts.delete"]))
):
    """Мягкое удаление факта печати"""
    logger.info(f"User {user} deleted print fact {print_fact_id}")
    PrintFact.delete(print_fact_id, session=db.session)
    db.session.commit()
    return {'status': 'ok', 'message': f'Print fact {print_fact_id} soft deleted'}


@router.post("/print-facts/{print_fact_id}/restore")
async def restore_print_fact(
    print_fact_id: int,
    user=Depends(UnionAuth(scopes=["print.admin.print_facts.restore"]))
):
    """Восстановление мягко удаленного факта печати"""
    logger.info(f"User {user} restored print fact {print_fact_id}")
    db_fact = PrintFact.get(print_fact_id, session=db.session, with_deleted=True)
    if not db_fact.is_deleted:
        raise HTTPException(status_code=400, detail="Print fact is not deleted")
    
    db_fact.is_deleted = False
    db.session.commit()
    return {'status': 'ok', 'message': f'Print fact {print_fact_id} restored'}
