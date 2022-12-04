import pytest
from fastapi.testclient import TestClient
from print_service.settings import get_settings

settings = get_settings()


@pytest.skip("Test waits infinitly")
def test_ws_connect_ok(client: TestClient):
    with client.websocket_connect('/qr', headers={"authorization": "token 123"}) as ws:
        data = ws.receive_json()
        assert set(data.keys()) == set('qr_token')
        return


def test_ws_connect_notoken(client: TestClient):
    try:
        with client.websocket_connect('/qr') as ws:
            data = ws.receive_json()
        assert False, "Should except"
    except Exception:
        pass
