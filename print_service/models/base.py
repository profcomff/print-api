import re

import sqlalchemy
from sqlalchemy import Integer, not_
from sqlalchemy.orm import Mapped, Query, Session, as_declarative, declared_attr, mapped_column


@as_declarative()
class Base:
    """Base class for all database entities"""

    @declared_attr
    def __tablename__(cls) -> str:  # pylint: disable=no-self-argument
        """Generate database table name automatically.
        Convert CamelCase class name to snake_case db table name.
        """
        return re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()


class BaseDbModel(Base):
    __abstract__ = True
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    @classmethod
    def query(cls, session: Session, with_deleted: bool = False) -> Query:
        objs = session.query(cls)
        if not with_deleted and hasattr(cls, "is_deleted"):
            objs = objs.filter(not_(cls.is_deleted))
        return objs
