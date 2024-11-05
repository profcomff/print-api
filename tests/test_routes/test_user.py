import json

import pytest
from starlette import status

from print_service.models import UnionMember
from print_service.settings import get_settings
from sqlalchemy import and_, func


url: str = '/is_union_member'
settings = get_settings()


def test_get_success(client, union_member_user):
    params = {
        'surname': union_member_user['surname'],
        'number': union_member_user['union_number'],
    }
    res = client.get(url, params=params)
    assert res.status_code == status.HTTP_202_ACCEPTED


def test_get_not_found(client):
    params = {
        'surname': 'surname',
        'number': 444,
    }
    res = client.get(url, params=params)
    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_get_is_deleted(client, union_member_user, add_is_deleted_flag):
    params = {
        'surname': 'test',
        'number': '6666667',
    }
    res = client.get(url, params=params)
    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_post_success(client, dbsession):
    body = {
        'users': [
            {
                'username': 'paul',
                'union_number': '1966',
                'student_number': '1967',
            }
        ]
    }
    res = client.post(url, data=json.dumps(body))
    assert res.status_code == status.HTTP_200_OK
    UnionMember.query(session=dbsession).filter(and_(
        UnionMember.surname == func.upper(body['users'][0]['username']),
        UnionMember.union_number == func.upper(body['users'][0]['union_number']),
        UnionMember.student_number == func.upper(body['users'][0]['student_number']))
    ).delete()
    dbsession.commit()


def test_post_is_deleted(client, union_member_user, add_is_deleted_flag):
    body = {
        'users': [
            {
                'username': 'new_test',
                'union_number': '6666667',
                'student_number': '13033224',
            }
        ]
    }
    res = client.post(url, data=json.dumps(body))
    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_restore_is_deleted(client, dbsession):
    user = UnionMember(id=5,
                       surname='test_user',
                       union_number='123',
                       student_number='56',
                       is_deleted=False)
    dbsession.add(user)
    dbsession.commit()

    body = {
        'users': [
            {
                'username': 'test_user',
                'union_number': '123',
                'student_number': '56',
                'is_deleted': True
             }
        ]
    }
    _ = client.post(url, data=json.dumps(body))
    res = UnionMember.query(session=dbsession, with_deleted=True).filter(UnionMember.id == 5).one_or_none()
    assert res.is_deleted is False
    user.is_deleted = True
    dbsession.commit()
    body = {
        'users': [
            {
                'username': 'test_user',
                'union_number': '123',
                'student_number': '56',
                'is_deleted': False
            }
        ]
    }
    res = client.post(url, data=json.dumps(body))
    assert res.status_code == status.HTTP_404_NOT_FOUND
    UnionMember.query(session=dbsession, with_deleted=True).filter(and_(
        UnionMember.surname == func.upper(body['users'][0]['username']),
        UnionMember.union_number == func.upper(body['users'][0]['union_number']),
        UnionMember.student_number == func.upper(body['users'][0]['student_number'])
    )).delete()
    dbsession.commit()


@pytest.mark.parametrize(
    'users',
    [
        pytest.param(
            [
                {
                    'username': 'paul',
                    'union_number': '404man',
                    'student_number': '30311',
                },
                {
                    'username': 'marty',
                    'union_number': '404man',
                    'student_number': '303112',
                },
            ],
            id='same union_number',
        ),
        pytest.param(
            [
                {
                    'username': 'alice',
                    'union_number': '500',
                    'student_number': '42',
                },
                {
                    'username': 'polly',
                    'union_number': '503',
                    'student_number': '42',
                },
            ],
            id='same student_number',
        ),
    ],
)
def test_post_list_duplicates(users, client):
    body = {'users': users}
    res = client.post(url, json=body)
    assert res.status_code == status.HTTP_400_BAD_REQUEST, res.json()
