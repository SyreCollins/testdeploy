from collections.abc import Generator
from functools import lru_cache

from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine


_engine = None


def get_engine(database_url: str):
    global _engine
    if _engine is None:
        connect_args = {}
        pool_kwargs = {}
        if database_url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}
            if ":memory:" in database_url:
                pool_kwargs["poolclass"] = StaticPool
        _engine = create_engine(database_url, connect_args=connect_args, **pool_kwargs)
    return _engine


def reset_engine() -> None:
    global _engine
    _engine = None


def init_db(database_url: str):
    e = get_engine(database_url)
    SQLModel.metadata.create_all(e)
    return e


def get_session() -> Generator[Session, None, None]:
    if _engine is None:
        raise RuntimeError("Engine not initialized. Call init_db() first.")
    with Session(_engine) as session:
        yield session
