from __future__ import annotations

import re

from sqlalchemy import not_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Mapped, Query, Session, as_declarative, declared_attr

from print_service.exceptions import ObjectNotFound


@as_declarative()
class Base:
    @declared_attr
    def __tablename__(cls) -> str:  # pylint: disable=no-self-argument
        return re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()

    def __repr__(self):
        attrs = []
        for c in self.__table__.columns:
            attrs.append(f"{c.name}={getattr(self, c.name)}")
        return "{}({})".format(c.__class__.__name__, ', '.join(attrs))



class BaseDbModel(Base):
    __abstract__ = True

    @classmethod
    def create(cls, *, session: Session, **kwargs) -> BaseDbModel:
        obj = cls(**kwargs)
        session.add(obj)
        session.flush()
        return obj

    @classmethod
    def query(cls, *, with_deleted: bool = False, session: Session) -> Query:
        objs = session.query(cls)
        if not with_deleted and hasattr(cls, "is_deleted"):
            objs = objs.filter(not_(cls.is_deleted))
        return objs

    @classmethod
    def get(cls, id: int | str, *, with_deleted=False, session: Session) -> BaseDbModel:
        objs = session.query(cls)
        if not with_deleted and hasattr(cls, "is_deleted"):
            objs = objs.filter(not_(cls.is_deleted))
        try:
            if hasattr(cls, "uuid"):
                return objs.filter(cls.uuid == id).one()
            return objs.filter(cls.id == id).one()
        except NoResultFound:
            raise ObjectNotFound(cls, id)

    @classmethod
    def update(cls, id: int | str, *, session: Session, **kwargs) -> BaseDbModel:
        obj = cls.get(id, session=session)
        for k, v in kwargs.items():
            setattr(obj, k, v)

        session.flush()
        return obj

    @classmethod
    def delete(cls, id: int | str, *, session: Session) -> None:
        obj = cls.get(id, session=session)
        if hasattr(obj, "is_deleted"):
            obj.is_deleted = True
        else:
            session.delete(obj)
        session.flush()
