from print_service.models import UnionMember
from sqlalchemy import not_


def test_union_member_create(dbsession):
    union_member = dict(
        id=1534,
        surname='test',
        union_number='6666667',
        student_number='13033224',
    )
    tmp = UnionMember.create(session=dbsession, **union_member)
    dbsession.flush()
    assert tmp is not None
    dbsession.query(UnionMember).filter(UnionMember.id == union_member['id']).delete()
    dbsession.commit()


def test_union_member_query_without_deleted(dbsession):
    tmp = UnionMember.query(session=dbsession)
    assert tmp is not None
    tmp_filtered = tmp.filter(not_(UnionMember.is_deleted))
    fl = (tmp.count() == tmp_filtered.count())
    assert fl is True


def test_union_member_query_with_deleted(dbsession):
    tmp = UnionMember.query(session=dbsession, with_deleted=True)
    assert tmp is not None


def test_union_member_get(dbsession):
    union_member = dict(
        id=1000,
        surname='test',
        union_number='6666667',
        student_number='13033224',
    )
    UnionMember.create(session=dbsession, **union_member)
    dbsession.flush()
    tmp = UnionMember.get(session=dbsession, obj_id=union_member['id'])
    assert type(tmp) is UnionMember
    dbsession.query(UnionMember).filter(UnionMember.id == union_member['id']).delete()
    dbsession.commit()


def test_union_member_update(dbsession):
    union_member = dict(
        id=644,
        surname='test',
        union_number='6666667',
        student_number='13033224',
    )
    union_member_updated = dict(
        id=644,
        surname='not_test',
        union_number='1233454',
        student_number='00000004'
    )
    UnionMember.create(session=dbsession, **union_member)
    dbsession.flush()
    tmp = UnionMember.update(obj_id=union_member['id'], session=dbsession, **union_member_updated)
    dbsession.flush()
    assert tmp is not None
    db_union_member_updated = dbsession.query(UnionMember).filter(UnionMember.id == union_member['id']).one_or_none()
    assert db_union_member_updated.surname != union_member['surname']
    assert db_union_member_updated.union_number != union_member['union_number']
    assert db_union_member_updated.student_number != union_member['student_number']
    dbsession.query(UnionMember).filter(UnionMember.id == union_member['id']).delete()
    dbsession.commit()


def test_union_member_delete(dbsession):
    union_member = dict(
        id=104,
        surname='test_4',
        union_number='6666660',
        student_number='45033224',
    )
    UnionMember.create(session=dbsession, **union_member)
    dbsession.flush()
    UnionMember.delete(obj_id=union_member['id'], session=dbsession)
    dbsession.commit()
    tmp = dbsession.query(UnionMember).filter(UnionMember.id == union_member['id']).one_or_none()
    assert tmp.is_deleted is True
