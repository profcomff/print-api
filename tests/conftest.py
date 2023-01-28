import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from print_service.routes import app
from print_service.settings import Settings


@pytest.fixture
def client(mocker):
    mocker.patch("auth_lib.fastapi.UnionAuth.__call__", return_value={"email": "test"})
    client = TestClient(app)
    return client


@pytest.fixture
def dbsession() -> Session:
    settings = Settings()
    engine = create_engine(settings.DB_DSN, pool_pre_ping=True)
    TestingSessionLocal = sessionmaker(bind=engine)
    yield TestingSessionLocal()
