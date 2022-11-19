from print_service.settings import get_settings
from print_service.models import File
from starlette import status
import json


url = '/file'
settings = get_settings()


def test_post_success(union_member_user, client, dbsession):
    body = {
        "surname": union_member_user['surname'],
        "number": union_member_user['union_number'],
        "filename": "filename.pdf",
        "options": {"pages": "", "copies": 1, "two_sided": False},
    }
    res = client.post(url, data=json.dumps(body))
    assert res.status_code == status.HTTP_200_OK
    db_file = dbsession.query(File).filter(File.pin == res.json()['pin']).one_or_none()
    assert db_file is not None
    dbsession.delete(db_file)


def test_post_unauthorized_user(client):
    body = {
        "surname": 'surname',
        "number": 'union_number',
        "filename": "filename.pdf",
        "options": {"pages": "", "copies": 1, "two_sided": False},
    }
    res = client.post(url, data=json.dumps(body))
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_get_file_no_path(uploaded_file_db, client):
    res = client.get(f"{url}/{uploaded_file_db.pin}")
    assert res.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE


def test_get_file_mock_path(uploaded_file_os, client):
    res = client.get(f"{url}/{uploaded_file_os.pin}")
    assert res.status_code == status.HTTP_200_OK


def test_get_file_wrong_pin(uploaded_file_os, client):
    res = client.get(f"{url}/{uploaded_file_os.pin}test404")
    assert res.status_code == status.HTTP_404_NOT_FOUND
