import pytest
from unittest.mock import Mock
from print_service.models import UnionMember


@pytest.fixture
def union_member_user(client, dbsession):
    union_member = dict(
        id=42,
        surname='test',
        union_number='6666667',
        student_number='13033224',
    )
    dbsession.add(UnionMember(**union_member))
    dbsession.flush()
    yield union_member
    db_user = dbsession.query(UnionMember).filter(UnionMember.id == 42).one_or_none()
    assert db_user is not None
    dbsession.delete(db_user)
