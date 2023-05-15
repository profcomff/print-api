from __future__ import annotations

import math
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
    print_facts: Mapped[list[PrintFact]] = relationship('PrintFact', back_populates='owner')


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
    number_of_pages: Mapped[int] = Column(Integer)

    owner: Mapped[UnionMember] = relationship('UnionMember', back_populates='files')
    print_facts: Mapped[list[PrintFact]] = relationship('PrintFact', back_populates='file')

    @property
    def flatten_pages(self) -> list | None:
        if self.number_of_pages is None:
            return None
        result = list()
        if self.option_pages == '':
            return result
        for part in self.option_pages.split(','):
            x = part.split('-')
            result.extend(range(int(x[0]), int(x[-1]) + 1))
        return result

    @property
    def sheets_count(self) -> int | None:
        if self.number_of_pages is None:
            return None
        if not self.flatten_pages:
            if self.option_two_sided:
                return (self.number_of_pages // 2 + 1) * self.option_copies
            else:
                return self.number_of_pages * self.option_copies
        if self.option_two_sided:
            return math.ceil(len(self.flatten_pages) / 2) * self.option_copies
        else:
            return len(self.flatten_pages) * self.option_copies


class PrintFact(Model):
    __tablename__ = 'print_fact'

    id: Mapped[int] = Column(Integer, primary_key=True)
    file_id: Mapped[int] = Column(Integer, ForeignKey('file.id'), nullable=False)
    owner_id: Mapped[int] = Column(Integer, ForeignKey('union_member.id'), nullable=False)
    created_at: Mapped[datetime] = Column(DateTime, nullable=False, default=datetime.utcnow)

    owner: Mapped[UnionMember] = relationship('UnionMember', back_populates='print_facts')
    file: Mapped[File] = relationship('File', back_populates='print_facts')

    sheets_used: Mapped[int] = Column(Integer)
