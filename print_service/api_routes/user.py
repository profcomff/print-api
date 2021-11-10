import logging
from typing import Optional

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi_sqlalchemy import db
from sqlalchemy import func

from print_service import __version__
from print_service.models import UnionMember


logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    '/is_union_member',
    status_code=202,
    responses={
        404: {'detail': 'User not found'},
    },
)
async def check_union_member(surname: str, number: str, v: Optional[str] = __version__):
    """Проверяет наличие пользователя в списке."""
    user = (
        db.session.query(UnionMember)
        .filter(
            func.upper(UnionMember.number) == number.upper(),
            func.upper(UnionMember.surname) == surname.upper(),
        )
        .one_or_none()
    )
    if v == '1':
        return bool(user)

    if not user:
        raise HTTPException(404, 'User not found')
    else:
        return {'surname': user.surname, 'number': user.number}
