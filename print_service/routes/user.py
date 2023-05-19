import logging
from typing import List, Optional

from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi_sqlalchemy import db
from pydantic import constr
from sqlalchemy import and_, func, or_

from print_service import __version__
from print_service.exceptions import UnionStudentDuplicate, UserNotFound
from print_service.models import UnionMember
from print_service.schema import BaseModel
from print_service.settings import get_settings


logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


# region schemas
class UserCreate(BaseModel):
    username: constr(strip_whitespace=True, to_upper=True, min_length=1)
    union_number: Optional[constr(strip_whitespace=True, to_upper=True, min_length=1)]
    student_number: Optional[constr(strip_whitespace=True, to_upper=True, min_length=1)]


class UpdateUserList(BaseModel):
    users: List[UserCreate]


# endregion


# region handlers
@router.get(
    '/is_union_member',
    status_code=202,
    responses={
        404: {'detail': 'User not found'},
    },
)
async def check_union_member(
    surname: constr(strip_whitespace=True, to_upper=True, min_length=1),
    number: constr(strip_whitespace=True, to_upper=True, min_length=1),
    v: Optional[str] = __version__,
):
    """Проверяет наличие пользователя в списке."""
    user = db.session.query(UnionMember)
    if not settings.ALLOW_STUDENT_NUMBER:
        user = user.filter(UnionMember.union_number != None)
    user: UnionMember = user.filter(
        or_(
            func.upper(UnionMember.student_number) == number,
            func.upper(UnionMember.union_number) == number,
        ),
        func.upper(UnionMember.surname) == surname,
    ).one_or_none()

    if v == '1':
        return bool(user)

    if not user:
        raise UserNotFound()
    else:
        return {
            'surname': user.surname,
            'number': number,
            'student_number': user.student_number,
            'union_number': user.union_number,
        }


@router.post('/is_union_member')
def update_list(
    input: UpdateUserList,
    user=Depends(UnionAuth(scopes=["print.user.create", "print.user.update", "print.user.delete"])),
):
    logger.info(f"User {user} updated list")

    union_numbers = [user.union_number for user in input.users if user.union_number is not None]
    student_numbers = [user.student_number for user in input.users if user.student_number is not None]

    if len(union_numbers) != len(set(union_numbers)) or len(student_numbers) != len(
        set(student_numbers)
    ):
        raise UnionStudentDuplicate()

    for user in input.users:
        db_user: UnionMember = (
            db.session.query(UnionMember)
            .filter(
                or_(
                    and_(
                        UnionMember.union_number == user.union_number,
                        UnionMember.union_number != None,
                    ),
                    and_(
                        UnionMember.student_number == user.student_number,
                        UnionMember.student_number != None,
                    ),
                )
            )
            .one_or_none()
        )

        if db_user:
            db_user.surname = user.username
            db_user.union_number = user.union_number
            db_user.student_number = user.student_number
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


# endregion
