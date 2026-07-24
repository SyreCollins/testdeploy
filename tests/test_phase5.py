from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import Settings
from app.db.engine import get_engine, reset_engine
from app.db.models.platform import Organization, User
from app.db.models.usage import UsageRecord
from app.main import create_app
from app.rag.vector_store.memory import MemoryVectorStore

_TEST_API_KEY = "test-key-123"


@pytest.fixture(autouse=True)
def _cleanup():
    from app.api.keys.service import store as api_key_store
    api_key_store._engine = None
    api_key_store._rate_cache.clear()
    reset_engine()
    yield


def seed_org(engine, plan: str = "free"):
    with Session(engine) as session:
        org = Organization(
            clerk_org_id="org_test",
            name="Test Organization",
            slug="test-org",
            plan=plan,
        )
        session.add(org)
        session.commit()
        session.refresh(org)
        org_id = org.id
        user = User(
            clerk_user_id="user_admin",
            email="admin@test.com",
            name="Admin",
            role="admin",
            organization_id=org_id,
        )
        session.add(user)
        session.commit()
    return org_id


# ─── Rate Limiting Tests ─────────────────────────────────────────────


def test_rate_limit_exceeded_returns_429():
    settings = Settings(
        _env_file=None,
        internal_api_keys=_TEST_API_KEY,
        database_url="sqlite:///:memory:",
        free_plan_rate_limit=1,
    )
    app = create_app(settings)
    client = TestClient(app)

    engine = get_engine("sqlite:///:memory:")
    org_id = seed_org(engine)

    from app.api.keys.service import store as api_key_store
    key_data = api_key_store.create_key(label="test-key", organization_id=org_id)
    headers = {"x-zam-ai-key": key_data["key"]}

    resp1 = client.get("/v1/ready", headers=headers)
    assert resp1.status_code == 200

    resp2 = client.get("/v1/ready", headers=headers)
    assert resp2.status_code == 429
    data = resp2.json()
    assert data["error"]["code"] == "rate_limit_exceeded"


def test_rate_limit_keys_are_independent():
    settings = Settings(
        _env_file=None,
        internal_api_keys=_TEST_API_KEY,
        database_url="sqlite:///:memory:",
        free_plan_rate_limit=1,
    )
    app = create_app(settings)
    client = TestClient(app)

    engine = get_engine("sqlite:///:memory:")
    org_id = seed_org(engine)

    from app.api.keys.service import store as api_key_store
    key_a = api_key_store.create_key(label="key-a", organization_id=org_id)
    key_b = api_key_store.create_key(label="key-b", organization_id=org_id)

    resp_a1 = client.get("/v1/ready", headers={"x-zam-ai-key": key_a["key"]})
    assert resp_a1.status_code == 200

    resp_a2 = client.get("/v1/ready", headers={"x-zam-ai-key": key_a["key"]})
    assert resp_a2.status_code == 429

    resp_b = client.get("/v1/ready", headers={"x-zam-ai-key": key_b["key"]})
    assert resp_b.status_code == 200


def test_rate_limit_pro_plan_allows_higher_limit():
    settings = Settings(
        _env_file=None,
        internal_api_keys=_TEST_API_KEY,
        database_url="sqlite:///:memory:",
        free_plan_rate_limit=1,
        pro_plan_rate_limit=5,
    )
    app = create_app(settings)
    client = TestClient(app)

    engine = get_engine("sqlite:///:memory:")
    org_id = seed_org(engine, plan="pro")

    from app.api.keys.service import store as api_key_store
    key_data = api_key_store.create_key(label="pro-key", organization_id=org_id)
    headers = {"x-zam-ai-key": key_data["key"]}

    for _ in range(5):
        resp = client.get("/v1/ready", headers=headers)
        assert resp.status_code == 200, f"Expected 200 but got {resp.status_code}"


# ─── Usage Tracking Tests ────────────────────────────────────────────


def test_usage_record_created_for_ai_request():
    settings = Settings(
        _env_file=None,
        internal_api_keys=_TEST_API_KEY,
        database_url="sqlite:///:memory:",
    )
    with patch("app.main.get_vector_store", return_value=MemoryVectorStore()):
        app = create_app(settings)
    client = TestClient(app)

    engine = get_engine("sqlite:///:memory:")
    org_id = seed_org(engine)

    from app.api.keys.service import store as api_key_store
    key_data = api_key_store.create_key(label="usage-key", organization_id=org_id)
    headers = {"x-zam-ai-key": key_data["key"]}

    client.post(
        "/v1/ai/medical-qa",
        json={
            "caller": {"service": "test", "environment": "test"},
            "actor_context": {"actor_type": "patient", "actor_id": "test", "role": "patient"},
            "authorization_context": {"workflow": "medical_qa"},
            "input": {
                "question": "Can I take ibuprofen with stomach ulcers?",
                "patient_context": {"age": 30, "sex": "male"},
            },
        },
        headers=headers,
    )

    with Session(engine) as session:
        records = session.exec(
            select(UsageRecord).where(UsageRecord.organization_id == org_id)
        ).all()
        assert len(records) >= 1
        record = records[0]
        assert record.endpoint == "/v1/ai/medical-qa"
        assert record.request_count == 1
        assert record.organization_id == org_id
        assert record.api_key_id == key_data["id"]
        assert record.prompt_tokens >= 1
        assert record.completion_tokens >= 1


def test_usage_record_not_created_for_non_ai_request():
    settings = Settings(
        _env_file=None,
        internal_api_keys=_TEST_API_KEY,
        database_url="sqlite:///:memory:",
    )
    app = create_app(settings)
    client = TestClient(app)

    engine = get_engine("sqlite:///:memory:")
    org_id = seed_org(engine)

    from app.api.keys.service import store as api_key_store
    key_data = api_key_store.create_key(label="usage-key", organization_id=org_id)
    headers = {"x-zam-ai-key": key_data["key"]}

    client.get("/v1/ready", headers=headers)

    with Session(engine) as session:
        records = session.exec(
            select(UsageRecord).where(UsageRecord.organization_id == org_id)
        ).all()
        assert len(records) == 0


def test_usage_record_not_created_without_auth():
    settings = Settings(
        _env_file=None,
        internal_api_keys=_TEST_API_KEY,
        database_url="sqlite:///:memory:",
    )
    app = create_app(settings)
    client = TestClient(app)

    client.post(
        "/v1/ai/medical-qa",
        json={
            "caller": {"service": "test", "environment": "test"},
            "actor_context": {"actor_type": "patient", "actor_id": "test", "role": "patient"},
            "authorization_context": {"workflow": "medical_qa"},
            "input": {"question": "test", "patient_context": {}},
        },
    )

    engine = get_engine("sqlite:///:memory:")
    with Session(engine) as session:
        records = session.exec(select(UsageRecord)).all()
        assert len(records) == 0
