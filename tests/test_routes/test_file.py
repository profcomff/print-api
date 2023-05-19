import json

import pytest
from fastapi import HTTPException
from starlette import status

from print_service.exceptions import FileNotFound, InvalidPageRequest, IsNotUpload
from print_service.models import File
from print_service.settings import get_settings
from print_service.utils import checking_for_pdf, get_file


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
    with pytest.raises((FileNotFound, IsNotUpload, InvalidPageRequest)):
        get_file(dbsession, ['1'])
        assert FileNotFound
    dbsession.commit()


def test_get_file_func_1_not_uploaded(dbsession, uploaded_file_db):
    with pytest.raises((FileNotFound, IsNotUpload, InvalidPageRequest)):
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
    with pytest.raises((FileNotFound, IsNotUpload, InvalidPageRequest)):
        data = get_file(dbsession, [uploaded_file_os.pin, '1'])


def test_file_check():
    assert checking_for_pdf(open("tests/test_routes/test_files/broken.pdf", "rb").read()) == (False, 0)
    assert checking_for_pdf(open("tests/test_routes/test_files/correct.pdf", "rb").read()) == (True, 2)


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
    assert res.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    res2 = client.get(f"{url}/{pin}")
    assert res2.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE


def test_incorrect_filename(union_member_user, client, dbsession):
    body1 = {
        "surname": union_member_user['surname'],
        "number": union_member_user['union_number'],
        "filename": "filepdf.",
        "options": {"pages": "", "copies": 1, "two_sided": False},
    }
    body2 = {
        "surname": union_member_user['surname'],
        "number": union_member_user['union_number'],
        "filename": "ffilepdf.412.-.",
        "options": {"pages": "", "copies": 1, "two_sided": False},
    }
    body3 = {
        "surname": union_member_user['surname'],
        "number": union_member_user['union_number'],
        "filename": "filepdf.421.doc.pdf...24...",
        "options": {"pages": "", "copies": 1, "two_sided": False},
    }
    body4 = {
        "surname": union_member_user['surname'],
        "number": union_member_user['union_number'],
        "filename": "&^$%#**$@)(",
        "options": {"pages": "", "copies": 1, "two_sided": False},
    }
    res1 = client.post(url, data=json.dumps(body1))
    assert res1.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    res2 = client.post(url, data=json.dumps(body2))
    assert res2.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    res3 = client.post(url, data=json.dumps(body3))
    assert res3.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    res4 = client.post(url, data=json.dumps(body4))
    assert res4.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_upload_big_file(pin_pdf, client):
    fileName = 'tests/test_routes/test_files/many_pages.pdf'
    files = {'file': (f"{fileName}", open(f"{fileName}", 'rb'), "application/pdf")}
    max_page = get_settings().MAX_PAGE_COUNT
    get_settings().MAX_PAGE_COUNT = 9
    res2 = client.post(f"{url}/{pin_pdf}", files=files)
    assert res2.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    get_settings().MAX_PAGE_COUNT = 10
    res3 = client.post(f"{url}/{pin_pdf}", files=files)
    assert res3.status_code == status.HTTP_200_OK
    get_settings().MAX_PAGE_COUNT = 3
    payload = {"options": {"pages": "2-4,6", "copies": 1, "two_sided": False}}
    res4 = client.patch(f"{url}/{pin_pdf}", json=payload)
    assert res4.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    payload2 = {"options": {"pages": "1-3, 7", "copies": 2, "two_sided": False}}
    get_settings().MAX_PAGE_COUNT = 7
    res5 = client.patch(f"{url}/{pin_pdf}", json=payload2)
    assert res5.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    payload3 = {"options": {"pages": "1-3, 7", "copies": 2, "two_sided": True}}
    get_settings().MAX_PAGE_COUNT = 3
    res6 = client.patch(f"{url}/{pin_pdf}", json=payload3)
    assert res6.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    get_settings().MAX_PAGE_COUNT = 4
    res7 = client.patch(f"{url}/{pin_pdf}", json=payload3)
    assert res7.status_code == status.HTTP_200_OK
    get_settings().MAX_PAGE_COUNT = 2
    payload4 = {"options": {"pages": "1, 1, 1", "copies": 1, "two_sided": False}}
    res8 = client.patch(f"{url}/{pin_pdf}", json=payload4)
    assert res8.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    get_settings().MAX_PAGE_COUNT = max_page
