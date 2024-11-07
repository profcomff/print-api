import re

import sqlalchemy
from sqlalchemy import not_
from sqlalchemy.orm import Query, Session, as_declarative, declared_attr


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

    @classmethod
    def query(cls, session: Session, with_deleted: bool = False) -> Query:
        objs = session.query(cls)
        if not with_deleted and hasattr(cls, "is_deleted"):
            objs = objs.filter(not_(cls.is_deleted))
        return objs
