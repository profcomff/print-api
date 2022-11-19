from typing import List, Optional

from pydantic import BaseModel


class UserCreate(BaseModel):
    username: Optional[str]
    union_number: Optional[str]
    student_number: Optional[str]


class UpdateUserList(BaseModel):
    users: List[UserCreate]
    secret: str
