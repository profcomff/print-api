import json

import pytest
from starlette import status

from print_service.models import UnionMember
from print_service.settings import get_settings


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


def test_post_success(client, dbsession):
    body = {
        'users': [
            {
                'username': 'paul',
                'union_number': '1966',
                'student_number': '1967',
            }
        ],
    }
    res = client.post(url, data=json.dumps(body))
    assert res.status_code == status.HTTP_200_OK
    dbsession.query(UnionMember).filter(
        UnionMember.surname == body['users'][0]['username'],
        UnionMember.union_number == body['users'][0]['union_number'],
        UnionMember.student_number == body['users'][0]['student_number'],
    ).delete()
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


def test_post_delete(client):
    body = {
        'users': [
            {
                'username': 'paul',
                'union_number': '1966',
                'student_number': '1967',
            }
        ],
    }
    params = {
        'surname': 'paul',
        'number': '1966',
    }
    res_post = client.post(url, json=body)
    assert res_post.status_code == status.HTTP_200_OK
    res_get1 = client.get(url, params=params)
    assert res_get1.status_code == status.HTTP_202_ACCEPTED
    res_post_delete = client.post(url, json={'users': []})
    assert res_post_delete.status_code == status.HTTP_200_OK
    res_get2 = client.get(url, params=params)
    assert res_get2.status_code == status.HTTP_404_NOT_FOUND
    body = {
        'users': [
            {
                'username': 'paul',
                'union_number': '1966',
                'student_number': '1967',
            },
            {
                'username': 'semen',
                'union_number': '1888',
                'student_number': '1887',
            },
            {
                'username': 'artem',
                'union_number': '1777',
                'student_number': '1776',
            },
        ],
    }
    res_post = client.post(url, json=body)
    assert res_post.status_code == status.HTTP_200_OK
    params = {
        'surname': 'semen',
        'number': '1888',
    }
    res_get = client.get(url, params=params)
    assert res_get.status_code == status.HTTP_202_ACCEPTED
    params = {
        'surname': 'artem',
        'number': '1777',
    }
    res_get = client.get(url, params=params)
    assert res_get.status_code == status.HTTP_202_ACCEPTED
    body = {
        'users': [
            {
                'username': 'semen',
                'union_number': '1889',
                'student_number': '1887',
            },
            {
                'username': 'artem',
                'union_number': '1777',
                'student_number': '1776',
            },
            {
                'username': 'roman',
                'union_number': '1999',
                'student_number': '1998',
            },
        ],
    }
    res_post_multi = client.post(url, json=body)
    assert res_post_multi.status_code == status.HTTP_200_OK
    params = {
        'surname': 'semen',
        'number': '1888',
    }
    res_get = client.get(url, params=params)
    assert res_get.status_code == status.HTTP_404_NOT_FOUND
    params = {
        'surname': 'semen',
        'number': '1889',
    }
    res_get = client.get(url, params=params)
    assert res_get.status_code == status.HTTP_202_ACCEPTED
    params = {
        'surname': 'artem',
        'number': '1777',
    }
    res_get = client.get(url, params=params)
    assert res_get.status_code == status.HTTP_202_ACCEPTED
    params = {
        'surname': 'roman',
        'number': '1999',
    }
    res_get = client.get(url, params=params)
    assert res_get.status_code == status.HTTP_202_ACCEPTED
