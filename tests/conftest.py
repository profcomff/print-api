import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from print_service.routes import app
from print_service.settings import Settings


@pytest.fixture
def client(mocker):
    user_mock = mocker.patch('auth_lib.fastapi.UnionAuth.__call__')
    user_mock.return_value = {
        "session_scopes": [{"id": 0, "name": "string", "comment": "string"}],
        "user_scopes": [{"id": 0, "name": "string", "comment": "string"}],
        "indirect_groups": [{"id": 0, "name": "string", "parent_id": 0}],
        "groups": [{"id": 0, "name": "string", "parent_id": 0}],
        "id": 0,
        "email": "string",
    }
    client = TestClient(app)
    return client


@pytest.fixture
def dbsession() -> Session:
    settings = Settings()
    engine = create_engine(settings.DB_DSN, pool_pre_ping=True)
    TestingSessionLocal = sessionmaker(bind=engine)
    yield TestingSessionLocal()
