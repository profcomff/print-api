from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Boolean


@as_declarative()
class Model:
    pass


class UnionMember(Model):
    __tablename__ = 'union_member'

    id = Column(Integer, primary_key=True)
    surname = Column(String, nullable=False)
    number = Column(String, nullable=False)

    files = relationship('File', back_populates='owner')


class File(Model):
    __tablename__ = 'file'

    id = Column(Integer, primary_key=True)
    pin = Column(String, nullable=False)
    file = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey('union_member.id'), nullable=False)
    option_pages = Column(String)
    option_copies = Column(Integer)
    option_two_sided = Column(Boolean)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship('UnionMember', back_populates='files')
