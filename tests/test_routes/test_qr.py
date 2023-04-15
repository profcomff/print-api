import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from print_service.settings import get_settings


settings = get_settings()
settings.STATIC_FOLDER = './static'


@pytest.mark.skip()
def test_ws_connect_ok(client: TestClient, uploaded_file_os):
    with client.websocket_connect('/qr', headers={"authorization": "token 123"}) as ws:
        data = ws.receive_json()
        assert set(data.keys()) == set(['qr_token'])
        t = data['qr_token']
        result = client.post('/qr', json={"qr_token": t, "files": [uploaded_file_os.pin]})
        data = ws.receive_json()
        assert set(data.keys()) == set(['qr_token', 'files'])
        assert data["qr_token"] != t
        assert len(data["files"]) == 1
        assert data["files"][0] == {
            'filename': uploaded_file_os.file,
            'options': {
                'pages': uploaded_file_os.option_pages or '',
                'copies': uploaded_file_os.option_copies or 1,
                'two_sided': uploaded_file_os.option_two_sided or False,
            },
        }
        return


def test_ws_connect_notoken(client: TestClient):
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect('/qr') as ws:
            pass
