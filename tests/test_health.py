from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


def test_health_does_not_require_api_key() -> None:
    app = create_app(Settings(internal_api_keys=["test-key"]))
    client = TestClient(app)

    response = client.get("/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.headers["x-request-id"]


def test_ready_requires_api_key() -> None:
    app = create_app(Settings(internal_api_keys=["test-key"]))
    client = TestClient(app)

    response = client.get("/v1/ready")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "authentication_failed"


def test_ready_with_api_key() -> None:
    app = create_app(Settings(internal_api_keys=["test-key"]))
    client = TestClient(app)

    response = client.get("/v1/ready", headers={"x-zam-ai-key": "test-key"})

    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert response.json()["dependencies"]["api"]["status"] == "ok"

