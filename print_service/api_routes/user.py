import logging
import secrets
from typing import List, Optional

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi_sqlalchemy import db
from sqlalchemy import func, or_, and_

from print_service import __version__
from print_service.settings import get_settings
from print_service.models import UnionMember
from print_service.schema import UpdateUserList


logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


@router.get(
    '/is_union_member',
    status_code=202,
    responses={
        404: {'detail': 'User not found'},
    },
)
async def check_union_member(surname: str, number: str, v: Optional[str] = __version__):
    """Проверяет наличие пользователя в списке."""
    user: UnionMember = db.session.query(UnionMember)
    if not settings.ALLOW_STUDENT_NUMBER:
        user = user.filter(UnionMember.union_number != None)
    user = user.filter(
        or_(
            func.upper(UnionMember.student_number) == number.upper(),
            func.upper(UnionMember.union_number) == number.upper(),
        ),
        func.upper(UnionMember.surname) == surname.upper(),
    ).one_or_none()

    if v == '1':
        return bool(user)

    if not user:
        raise HTTPException(404, 'User not found')
    else:
        return {
            'surname': user.surname,
            'number': number,
            'student_number': user.student_number,
            'union_number': user.union_number,
        }


@router.post('/is_union_member')
def update_list(input: UpdateUserList):
    if input.secret != settings.SECRET_KEY:
        raise HTTPException(403, {"status": "error", "detail": "Incorrect secret"})

    union_numbers = [user.union_number for user in input.users if user.union_number is not None]
    student_numbers = [user.student_number for user in input.users if user.student_number is not None]

    if len(union_numbers) != len(set(union_numbers)) or len(student_numbers) != len(set(student_numbers)):
        raise HTTPException(400, {"status": "error", "detail": "Duplicates by union_numbers or student_numbers"})

    for user in input.users:
        db_user: UnionMember = db.session.query(UnionMember).filter(
            or_(
                and_(UnionMember.union_number == user.union_number, UnionMember.union_number != None),
                and_(UnionMember.student_number == user.student_number, UnionMember.student_number != None),
            )
        ).one_or_none()

        if db_user:
            db_user.surname=user.username
            db_user.union_number=user.union_number
            db_user.student_number=user.student_number
            db.session.flush()
        else:
            db.session.add(
                UnionMember(
                    surname=user.username,
                    union_number=user.union_number,
                    student_number=user.student_number,
                )
            )
            db.session.flush()

    db.session.commit()
    return {"status": "ok", "count": len(input.users)}
