from collections.abc import Generator
import pytest
from fastapi import HTTPException, Depends
from fastapi.testclient import TestClient
from sqlmodel import create_engine, SQLModel, Session, delete
from app.db import get_session
from app.auth import get_current_user, api_key_header
from app.main import app
from app.models import Video

import sqlite3
import datetime
from dotenv import load_dotenv
import os

load_dotenv()


def adapt_datetime(dt: datetime.datetime) -> str:
    return dt.isoformat()


def convert_datetime(iso_str: bytes) -> datetime.datetime:
    return datetime.datetime.fromisoformat(iso_str.decode())


sqlite3.register_adapter(datetime.datetime, adapt_datetime)
sqlite3.register_converter("DATETIME", convert_datetime)

DATABASE_URL = "sqlite:///./test.db"
TEST_API_KEY = os.getenv("TEST_API_KEY")

engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"detect_types": sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES},
)


@pytest.fixture(scope="session")
def session() -> Generator[Session, None, None]:
    """
    Initialize the test database and clean up after the session.
    """
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

        statement = delete(Video)
        session.exec(statement)
        session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    """
    Provide a FastAPI test client with database dependency overridden.
    """

    def override_get_session() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    def override_get_current_user(api_key: str = Depends(api_key_header)):
        if not api_key == TEST_API_KEY:
            raise HTTPException(status_code=401, detail="Invalid API Key")
        return "TestClient"

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def headers() -> dict:
    """
    Provides default headers including the API key for testing.
    """
    return {"X-Api-Key": TEST_API_KEY}
