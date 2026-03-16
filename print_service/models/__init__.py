from __future__ import annotations

import math
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from print_service.base import Base, BaseDbModel


Model = Base


class UnionMember(BaseDbModel):
    __tablename__ = 'union_member'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    surname: Mapped[str] = mapped_column(String, nullable=False)
    union_number: Mapped[str] = mapped_column(String, nullable=True)
    student_number: Mapped[str] = mapped_column(String, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )

    files: Mapped[list[File]] = relationship('File', back_populates='owner')
    print_facts: Mapped[list[PrintFact]] = relationship('PrintFact', back_populates='owner')


class File(BaseDbModel):
    __tablename__ = 'file'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pin: Mapped[str] = mapped_column(String, nullable=False)
    file: Mapped[str] = mapped_column(String, nullable=False)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey('union_member.id'), nullable=False)
    option_pages: Mapped[str] = mapped_column(String)
    option_copies: Mapped[int] = mapped_column(Integer)
    option_two_sided: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
    number_of_pages: Mapped[int] = mapped_column(Integer)
    source: Mapped[str] = mapped_column(String, default='unknown', nullable=False)
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )

    owner: Mapped[UnionMember] = relationship('UnionMember', back_populates='files')
    print_facts: Mapped[list[PrintFact]] = relationship('PrintFact', back_populates='file')

    @property
    def flatten_pages(self) -> list[int] | None:
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
            return (
                math.ceil(self.number_of_pages - (self.option_two_sided * self.number_of_pages / 2))
                * self.option_copies
            )
        if self.option_two_sided:
            return math.ceil(len(self.flatten_pages) / 2) * self.option_copies
        else:
            return len(self.flatten_pages) * self.option_copies


class PrintFact(BaseDbModel):
    __tablename__ = 'print_fact'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    file_id: Mapped[int] = mapped_column(Integer, ForeignKey('file.id'), nullable=False)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey('union_member.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    sheets_used: Mapped[int] = mapped_column(Integer)
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )

    owner: Mapped[UnionMember] = relationship('UnionMember', back_populates='print_facts')
    file: Mapped[File] = relationship('File', back_populates='print_facts')
