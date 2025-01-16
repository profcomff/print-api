import os

import pytest

from print_service.models import File, PrintFact, UnionMember


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
    db_user = (
        UnionMember.query(session=dbsession, with_deleted=True)
        .filter(UnionMember.id == union_member['id'])
        .one_or_none()
    )
    assert db_user is not None
    PrintFact.query(session=dbsession).filter(PrintFact.owner_id == union_member['id']).delete()
    UnionMember.query(session=dbsession, with_deleted=True).filter(
        UnionMember.id == union_member['id']
    ).delete()
    dbsession.commit()


@pytest.fixture(scope='function')
def add_is_deleted_flag(dbsession):
    db_user = UnionMember.query(session=dbsession).filter(UnionMember.id == 42).one_or_none()
    db_user.is_deleted = True
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
    db_file = File.query(session=dbsession).filter(File.pin == res.json()['pin']).one_or_none()
    yield db_file
    file = File.query(session=dbsession).filter(File.pin == res.json()['pin']).one_or_none()
    assert file is not None
    PrintFact.query(session=dbsession).filter(PrintFact.file_id == file.id).delete()
    File.query(session=dbsession).filter(File.pin == res.json()['pin']).delete()
    dbsession.commit()


@pytest.fixture
def uploaded_file_os(uploaded_file_db):
    with open(f'static/{uploaded_file_db.file}', 'w') as file:
        file.write('\n')
    yield uploaded_file_db
    os.remove(f'static/{uploaded_file_db.file}')


@pytest.fixture
def pin_pdf(dbsession, union_member_user, client):
    body = {
        "surname": union_member_user['surname'],
        "number": union_member_user['union_number'],
        "filename": "tets.pdf",
        "options": {"pages": "", "copies": 1, "two_sided": False},
    }
    res = client.post('/file', json=body)
    pin = res.json()['pin']
    yield pin
    file = File.query(session=dbsession).filter(File.pin == res.json()['pin']).one_or_none()
    assert file is not None
    PrintFact.query(session=dbsession).filter(PrintFact.file_id == file.id).delete()
    File.query(session=dbsession).filter(File.pin == res.json()['pin']).delete()
    dbsession.commit()
