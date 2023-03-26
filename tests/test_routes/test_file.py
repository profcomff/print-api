import asyncio
import json
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi import HTTPException
from starlette import status

from print_service.models import File
from print_service.settings import get_settings
from print_service.utils import check_pdf_ok, get_file


url = '/file'
settings = get_settings()
settings.STATIC_FOLDER = './static'


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
    dbsession.commit()


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


def test_get_file_func_1_not_exists(dbsession):
    with pytest.raises(HTTPException):
        get_file(dbsession, ['1'])
    dbsession.commit()


def test_get_file_func_1_not_uploaded(dbsession, uploaded_file_db):
    with pytest.raises(HTTPException):
        data = get_file(dbsession, [uploaded_file_db.pin])
    dbsession.commit()


def test_get_file_func_1_ok(dbsession, uploaded_file_os):
    data = get_file(dbsession, [uploaded_file_os.pin])
    assert len(data) == 1
    assert data[0] == {
        'filename': uploaded_file_os.file,
        'options': {
            'pages': uploaded_file_os.option_pages or '',
            'copies': uploaded_file_os.option_copies or 1,
            'two_sided': uploaded_file_os.option_two_sided or False,
        },
    }
    dbsession.commit()


def test_get_file_func_2_not_exists(dbsession, uploaded_file_os):
    with pytest.raises(HTTPException):
        data = get_file(dbsession, [uploaded_file_os.pin, '1'])


def test_file_check():
    assert check_pdf_ok(open("tests/test_routes/test_files/broken.pdf", "rb").read()) is False
    assert check_pdf_ok(open("tests/test_routes/test_files/correct.pdf", "rb").read()) is True


def test_upload_and_print_correct_pdf(pin_pdf, client):
    pin = pin_pdf
    fileName = 'tests/test_routes/test_files/correct.pdf'
    files = {'file': (f"{fileName}", open(f"{fileName}", 'rb'), "application/pdf")}
    res = client.post(f"{url}/{pin}", files=files)
    assert res.status_code == status.HTTP_200_OK
    res2 = client.get(f"{url}/{pin}")
    assert res2.status_code == status.HTTP_200_OK


def test_upload_and_print_broken_file(pin_pdf, client):
    pin = pin_pdf
    fileName = 'tests/test_routes/test_files/broken.pdf'
    files = {'file': (f"{fileName}", open(f"{fileName}", 'rb'), "application/pdf")}
    res = client.post(f"{url}/{pin}", files=files)
    assert res.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    res2 = client.get(f"{url}/{pin}")
    assert res2.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE


def test_upload_and_print_not_pdf_file(pin_pdf, client):
    pin = pin_pdf
    fileName = 'tests/test_routes/test_files/not_pdf.pdf'
    files = {'file': (f"{fileName}", open(f"{fileName}", 'rb'), "application/pdf")}
    res = client.post(f"{url}/{pin}", files=files)
    assert res.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    res2 = client.get(f"{url}/{pin}")
    assert res2.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE


def test_upload_and_print_encrypted_file(pin_pdf, client):
    pin = pin_pdf
    fileName = 'tests/test_routes/test_files/encrypted.pdf'
    files = {'file': (f"{fileName}", open(f"{fileName}", 'rb'), "application/pdf")}
    res = client.post(f"{url}/{pin}", files=files)
    assert res.status_code == status.HTTP_200_OK
    res2 = client.get(f"{url}/{pin}")
    assert res2.status_code == status.HTTP_200_OK
