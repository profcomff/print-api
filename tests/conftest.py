from print_service.fastapi import app
from print_service.settings import Settings
from print_service.models import Model
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


@pytest.fixture(scope='session')
def client():
    client = TestClient(app)
    return client


@pytest.fixture(scope='session')
def dbsession() -> Session:
    settings = Settings()
    engine = create_engine(settings.DB_DSN)
    TestingSessionLocal = sessionmaker(autocommit=True, autoflush=True, bind=engine)
    yield TestingSessionLocal()
