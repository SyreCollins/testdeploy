import os

import pytest
from fastapi.testclient import TestClient

pytest_plugins = ("pytest_asyncio",)

from app.core.config import Settings
from app.main import create_app


_TEST_API_KEY = "test-key-123"


@pytest.fixture(autouse=True)
def _cleanup():
    saved_env = {
        k: os.environ.pop(k, None)
        for k in list(os.environ)
        if k.startswith("ZAM_AI_")
    }
    from app.api.keys.service import store as api_key_store
    api_key_store._keys.clear()
    api_key_store._bootstrapped = False
    yield
    for k, v in saved_env.items():
        if v is not None:
            os.environ[k] = v


@pytest.fixture
def settings() -> Settings:
    return Settings(
        _env_file=None,
        internal_api_keys=_TEST_API_KEY,
        database_url="sqlite:///:memory:",
    )


@pytest.fixture
def app(settings: Settings):
    return create_app(settings)


@pytest.fixture
def client(app) -> TestClient:
    return TestClient(app)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"x-zam-ai-key": _TEST_API_KEY}