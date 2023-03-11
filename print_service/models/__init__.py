from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, not_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import Session, Query, Mapped, relationship, mapped_column
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Boolean

from print_service.models.exceptions import ObjectNotFound


@as_declarative()
class Model:
    pass


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

    owner: Mapped[UnionMember] = relationship('UnionMember', back_populates='files', foreign_keys=[owner_id])


class UnionMember(Model):
    __tablename__ = 'union_member'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    surname: Mapped[str] = mapped_column(String, nullable=False)
    union_number: Mapped[str] = mapped_column(String, nullable=True)
    student_number: Mapped[str] = mapped_column(String, nullable=True)
    is_deleted: Mapped[bool] = Column(Boolean, nullable=True, default=False)
    files: Mapped[list[File]] = relationship('File', back_populates='owner', foreign_keys=[File.owner_id])

    @classmethod
    def create(cls, *, session: Session, **kwargs) -> UnionMember:
        obj = cls(**kwargs)
        session.add(obj)
        session.flush()
        return obj

    @classmethod
    def query(cls, *, with_deleted: bool = False, session: Session) -> Query:
        """Get all objects with soft deletes"""
        objs = session.query(cls)
        if not with_deleted and hasattr(cls, "is_deleted"):
            objs = objs.filter(not_(cls.is_deleted))
        return objs

    @classmethod
    def get(cls, obj_id: int, *, with_deleted=False, session: Session) -> UnionMember:
        """Get object with soft deletes"""
        objs = session.query(cls)
        if not with_deleted and hasattr(cls, "is_deleted"):
            objs = objs.filter(not_(cls.is_deleted))
        try:
            return objs.filter(cls.id == obj_id).one()
        except NoResultFound:
            raise ObjectNotFound(cls, obj_id)

    @classmethod
    def update(cls, obj_id: int, *, session: Session, **kwargs) -> UnionMember:
        obj = cls.get(obj_id, session=session)
        for k, v in kwargs.items():
            setattr(obj, k, v)
        session.flush()
        return obj

    @classmethod
    def delete(cls, obj_id: int, *, session: Session) -> None:
        """Soft delete object if possible, else hard delete"""
        obj = cls.get(obj_id, session=session)
        if hasattr(obj, "is_deleted"):
            obj.is_deleted = True
        else:
            session.delete(obj)
        session.flush()




