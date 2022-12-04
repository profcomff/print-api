import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from print_service.settings import get_settings

settings = get_settings()


@pytest.mark.skip()
def test_ws_connect_ok(client: TestClient, uploaded_file_db):
    with client.websocket_connect('/qr', headers={"authorization": "token 123"}) as ws:
        data = ws.receive_json()
        assert set(data.keys()) == set(['qr_token'])
        t = data['qr_token']
        client.post('/qr', json={"qr_token": t, "files": [uploaded_file_db.pin]})
        data = ws.receive_json()
        assert set(data.keys()) == set(['qr_token', 'files'])
        return


def test_ws_connect_notoken(client: TestClient):
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect('/qr') as ws:
            pass
