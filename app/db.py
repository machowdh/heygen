import sqlite3
from datetime import datetime
from sqlmodel import create_engine, SQLModel, Session
from collections.abc import Generator
from typing import Annotated
from fastapi import Depends
from dotenv import load_dotenv

import os

DATABASE_URL = "sqlite:///./heygen.db"

load_dotenv()

users = {
    "2685f17f-3854-4216-9f21-18c24d20d02b": "Client",
    "66b63089-33de-4a8f-adc0-28dc4047c42d": "TestClient",
}


def is_valid(api_key: str) -> bool:
    return api_key == os.getenv("API_KEY")


def get_user(api_key: str) -> str:
    return users[api_key]


def adapt_datetime(dt: datetime) -> str:
    return dt.isoformat()


def convert_datetime(iso_str: bytes) -> datetime:
    return datetime.fromisoformat(iso_str.decode())


sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("DATETIME", convert_datetime)

engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"detect_types": sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES},
)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
