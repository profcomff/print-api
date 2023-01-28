import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from print_service.routes import app
from print_service.settings import Settings


@pytest.fixture(scope='session')
def client():
    client = TestClient(app)
    return client


@pytest.fixture(scope='session')
def dbsession() -> Session:
    settings = Settings()
    engine = create_engine(settings.DB_DSN, pool_pre_ping=True)
    TestingSessionLocal = sessionmaker(bind=engine)
    yield TestingSessionLocal()
