import pytest
import json
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
        'secret': settings.SECRET_KEY,
    }
    res = client.post(url, data=json.dumps(body))
    assert res.status_code == status.HTTP_200_OK
    dbsession.query(UnionMember).filter(
        UnionMember.surname == body['users'][0]['username'],
        UnionMember.union_number == body['users'][0]['union_number'],
        UnionMember.student_number == body['users'][0]['student_number'],
    ).delete()


def test_post_incorrect_password(client):
    body = {
        'users': [
            {
                'username': 'paul',
                'union_number': '1966',
                'student_number': '1967',
            }
        ],
        'secret': f"{settings.SECRET_KEY}secret!!!",
    }
    res = client.post(url, data=json.dumps(body))
    assert res.status_code == status.HTTP_403_FORBIDDEN


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
    body = {'users': users, 'secret': settings.SECRET_KEY}
    res = client.post(url, data=json.dumps(body))
    assert res.status_code == status.HTTP_400_BAD_REQUEST
