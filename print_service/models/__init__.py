from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Boolean


@as_declarative()
class Model:
    pass


class UnionMember(Model):
    __tablename__ = 'union_member'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    surname: Mapped[str] = mapped_column(String, nullable=False)
    union_number: Mapped[str] = mapped_column(String, nullable=True)
    student_number: Mapped[str] = mapped_column(String, nullable=True)

    files: Mapped[list[File]] = relationship('File', back_populates='owner')


class File(Model):
    __tablename__ = 'file'

    id: Mapped[int] = Column(Integer, primary_key=True)
    pin: Mapped[str] = Column(String, nullable=False)
    file: Mapped[str] = Column(String, nullable=False)
    owner_id: Mapped[int] = Column(Integer, ForeignKey('union_member.id'), nullable=False)
    option_pages: Mapped[str] = Column(String)
    option_copies: Mapped[int] = Column(Integer)
    option_two_sided: Mapped[bool] = Column(Boolean)
    created_at: Mapped[datetime] = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    owner: Mapped[UnionMember] = relationship('UnionMember', back_populates='files')
