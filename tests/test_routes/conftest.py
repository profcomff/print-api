import os

import pytest
from unittest.mock import Mock
from print_service.models import UnionMember, File


@pytest.fixture(scope='function')
def union_member_user(dbsession):
    union_member = dict(
        id=42,
        surname='test',
        union_number='6666667',
        student_number='13033224',
    )
    dbsession.add(UnionMember(**union_member))
    dbsession.commit()
    yield union_member
    db_user = dbsession.query(UnionMember).filter(UnionMember.id == union_member['id']).one_or_none()
    assert db_user is not None
    dbsession.query(UnionMember).filter(UnionMember.id == union_member['id']).delete()
    dbsession.commit()


@pytest.fixture(scope='function')
def uploaded_file_db(dbsession, union_member_user, client):
    body = {
        "surname": union_member_user['surname'],
        "number": union_member_user['union_number'],
        "filename": "filename.pdf",
        "options": {"pages": "", "copies": 1, "two_sided": False},
    }
    res = client.post('/file', json=body)
    db_file = dbsession.query(File).filter(File.pin == res.json()['pin']).one_or_none()
    dbsession.flush()
    yield db_file
    dbsession.query(File).filter(File.pin == res.json()['pin']).delete()
    dbsession.commit()



@pytest.fixture
def uploaded_file_os(uploaded_file_db):
    with open(f'static/{uploaded_file_db.file}', 'w') as file:
        file.write('\n')
    yield uploaded_file_db
    os.remove(f'static/{uploaded_file_db.file}')
