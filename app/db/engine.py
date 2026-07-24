from collections.abc import Generator

from sqlalchemy.pool import NullPool, StaticPool
from sqlmodel import Session, SQLModel, create_engine

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
        else:
            pool_kwargs["pool_pre_ping"] = True
        _engine = create_engine(database_url, connect_args=connect_args, **pool_kwargs)
    return _engine


def reset_engine() -> None:
    global _engine
    if _engine is not None:
        SQLModel.metadata.drop_all(_engine)
    _engine = None


def init_db(database_url: str):
    e = get_engine(database_url)
    SQLModel.metadata.create_all(e)
    return e


def get_session(engine=None) -> Generator[Session, None, None]:
    e = engine or _engine
    if e is None:
        raise RuntimeError("Engine not initialized. Call init_db() first.")
    with Session(e) as session:
        yield session
