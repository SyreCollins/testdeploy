
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import Settings
from app.db.engine import get_engine, reset_engine
from app.db.models.platform import Organization, User
from app.main import create_app

_TEST_API_KEY = "test-key-123"


@pytest.fixture(autouse=True)
def _cleanup():
    from app.api.keys.service import store as api_key_store
    api_key_store._engine = None
    api_key_store._rate_cache.clear()
    reset_engine()
    yield


@pytest.fixture
def settings():
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
def auth_headers():
    return {"x-zam-ai-key": _TEST_API_KEY}


# ─── Webhook Tests ───────────────────────────────────────────────────


def test_webhook_missing_headers(client):
    resp = client.post("/v1/auth/webhook", json={})
    assert resp.status_code == 200
    assert resp.json() == {"received": True}


def test_webhook_user_created(client, auth_headers):
    payload = {
        "type": "user.created",
        "data": {
            "id": "user_abc123",
            "email_addresses": [{"id": "email_1", "email_address": "test@example.com"}],
            "primary_email_address_id": "email_1",
            "first_name": "John",
            "last_name": "Doe",
        },
    }
    resp = client.post("/v1/auth/webhook", json=payload)
    assert resp.status_code == 200

    engine = get_engine("sqlite:///:memory:")
    with Session(engine) as session:
        user = session.exec(select(User).where(User.clerk_user_id == "user_abc123")).first()
        assert user is not None
        assert user.email == "test@example.com"
        assert user.name == "John Doe"
        assert user.role == "member"


def test_webhook_organization_created(client, auth_headers):
    payload = {
        "type": "organization.created",
        "data": {
            "id": "org_xyz789",
            "name": "Test Org",
            "slug": "test-org",
        },
    }
    resp = client.post("/v1/auth/webhook", json=payload)
    assert resp.status_code == 200

    engine = get_engine("sqlite:///:memory:")
    with Session(engine) as session:
        org = session.exec(select(Organization).where(Organization.clerk_org_id == "org_xyz789")).first()
        assert org is not None
        assert org.name == "Test Org"
        assert org.slug == "test-org"
        assert org.plan == "free"


def test_webhook_invalid_signature_still_returns_200(settings):
    settings.clerk_webhook_secret = "whsec_test"
    app = create_app(settings)
    client = TestClient(app)
    resp = client.post(
        "/v1/auth/webhook",
        json={"type": "user.created", "data": {"id": "user_bad_sig"}},
        headers={"svix-id": "id1", "svix-timestamp": "123456", "svix-signature": "v1,invalidsig"},
    )
    assert resp.status_code == 200


# ─── Auth Middleware Tests ────────────────────────────────────────────


def test_endpoint_without_auth_returns_401(client):
    resp = client.get("/v1/ready")
    assert resp.status_code == 401


def test_endpoint_with_valid_api_key_succeeds(client, auth_headers):
    resp = client.get("/v1/ready", headers=auth_headers)
    assert resp.status_code == 200


def test_endpoint_with_invalid_api_key_returns_401(client):
    resp = client.get("/v1/ready", headers={"x-zam-ai-key": "invalid-key"})
    assert resp.status_code == 401


def test_public_paths_do_not_require_auth(client):
    resp = client.get("/v1/health")
    assert resp.status_code == 200


# ─── Org Endpoint Tests ───────────────────────────────────────────────


def seed_org(engine):
    with Session(engine) as session:
        org = Organization(
            clerk_org_id="org_test",
            name="Test Organization",
            slug="test-org",
            plan="pro",
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


def test_get_org_me(client, auth_headers):
    engine = get_engine("sqlite:///:memory:")
    org_id = seed_org(engine)

    from app.api.keys.service import store as api_key_store
    key_data = api_key_store.create_key(label="test-org-key", organization_id=org_id)
    headers = {"x-zam-ai-key": key_data["key"]}

    resp = client.get("/v1/organizations/me", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Test Organization"
    assert data["slug"] == "test-org"
    assert data["plan"] == "pro"


def test_get_org_me_with_bootstrap_key_fails(client, auth_headers):
    resp = client.get("/v1/organizations/me", headers=auth_headers)
    assert resp.status_code == 401


def test_create_org_api_key(client, auth_headers):
    engine = get_engine("sqlite:///:memory:")
    org_id = seed_org(engine)

    from app.api.keys.service import store as api_key_store
    key_data = api_key_store.create_key(label="admin-key", organization_id=org_id)

    resp = client.post(
        "/v1/organizations/me/api-keys",
        json={"label": "my-key"},
        headers={"x-zam-ai-key": key_data["key"]},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["label"] == "my-key"
    assert data["key"].startswith("zam_")
    assert data["is_active"] is True


def test_create_and_list_org_api_keys(client, auth_headers):
    engine = get_engine("sqlite:///:memory:")
    org_id = seed_org(engine)

    from app.api.keys.service import store as api_key_store
    key_data = api_key_store.create_key(label="admin-key", organization_id=org_id)
    org_headers = {"x-zam-ai-key": key_data["key"]}

    client.post("/v1/organizations/me/api-keys", json={"label": "key-1"}, headers=org_headers)
    client.post("/v1/organizations/me/api-keys", json={"label": "key-2"}, headers=org_headers)

    resp = client.get("/v1/organizations/me/api-keys", headers=org_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["keys"]) == 3
    labels = {k["label"] for k in data["keys"]}
    assert "key-1" in labels
    assert "key-2" in labels
    assert "admin-key" in labels


def test_rotate_org_api_key(client, auth_headers):
    engine = get_engine("sqlite:///:memory:")
    org_id = seed_org(engine)

    from app.api.keys.service import store as api_key_store
    key_data = api_key_store.create_key(label="admin-key", organization_id=org_id)
    org_headers = {"x-zam-ai-key": key_data["key"]}

    create_resp = client.post("/v1/organizations/me/api-keys", json={"label": "rotatable"}, headers=org_headers)
    key_id = create_resp.json()["id"]

    resp = client.post(f"/v1/organizations/me/api-keys/{key_id}/rotate", headers=org_headers)
    assert resp.status_code == 200
    assert resp.json()["key"].startswith("zam_")


def test_revoke_org_api_key(client, auth_headers):
    engine = get_engine("sqlite:///:memory:")
    org_id = seed_org(engine)

    from app.api.keys.service import store as api_key_store
    key_data = api_key_store.create_key(label="admin-key", organization_id=org_id)
    org_headers = {"x-zam-ai-key": key_data["key"]}

    create_resp = client.post("/v1/organizations/me/api-keys", json={"label": "revocable"}, headers=org_headers)
    key_id = create_resp.json()["id"]

    resp = client.post(f"/v1/organizations/me/api-keys/{key_id}/revoke", headers=org_headers)
    assert resp.status_code == 200
    assert resp.json()["revoked"] is True


# ─── Project Endpoint Tests ───────────────────────────────────────────


def test_create_project(client, auth_headers):
    engine = get_engine("sqlite:///:memory:")
    org_id = seed_org(engine)

    from app.api.keys.service import store as api_key_store
    key_data = api_key_store.create_key(label="admin-key", organization_id=org_id)
    org_headers = {"x-zam-ai-key": key_data["key"]}

    resp = client.post(
        "/v1/organizations/me/projects",
        json={"name": "My Project", "slug": "my-project", "environment": "development"},
        headers=org_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "My Project"
    assert data["slug"] == "my-project"
    assert data["organization_id"] == org_id


def test_create_duplicate_project_slug(client, auth_headers):
    engine = get_engine("sqlite:///:memory:")
    org_id = seed_org(engine)

    from app.api.keys.service import store as api_key_store
    key_data = api_key_store.create_key(label="admin-key", organization_id=org_id)
    org_headers = {"x-zam-ai-key": key_data["key"]}

    client.post(
        "/v1/organizations/me/projects",
        json={"name": "First", "slug": "same-slug"},
        headers=org_headers,
    )
    resp = client.post(
        "/v1/organizations/me/projects",
        json={"name": "Second", "slug": "same-slug"},
        headers=org_headers,
    )
    assert resp.status_code == 409


def test_list_projects(client, auth_headers):
    engine = get_engine("sqlite:///:memory:")
    org_id = seed_org(engine)

    from app.api.keys.service import store as api_key_store
    key_data = api_key_store.create_key(label="admin-key", organization_id=org_id)
    org_headers = {"x-zam-ai-key": key_data["key"]}

    client.post("/v1/organizations/me/projects", json={"name": "P1", "slug": "p1"}, headers=org_headers)
    client.post("/v1/organizations/me/projects", json={"name": "P2", "slug": "p2"}, headers=org_headers)

    resp = client.get("/v1/organizations/me/projects", headers=org_headers)
    assert resp.status_code == 200
    assert len(resp.json()["projects"]) == 2


def test_get_project_detail(client, auth_headers):
    engine = get_engine("sqlite:///:memory:")
    org_id = seed_org(engine)

    from app.api.keys.service import store as api_key_store
    key_data = api_key_store.create_key(label="admin-key", organization_id=org_id)
    org_headers = {"x-zam-ai-key": key_data["key"]}

    create_resp = client.post(
        "/v1/organizations/me/projects",
        json={"name": "Detail Me", "slug": "detail-me"},
        headers=org_headers,
    )
    project_id = create_resp.json()["id"]

    resp = client.get(f"/v1/organizations/me/projects/{project_id}", headers=org_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Detail Me"


def test_update_project(client, auth_headers):
    engine = get_engine("sqlite:///:memory:")
    org_id = seed_org(engine)

    from app.api.keys.service import store as api_key_store
    key_data = api_key_store.create_key(label="admin-key", organization_id=org_id)
    org_headers = {"x-zam-ai-key": key_data["key"]}

    create_resp = client.post(
        "/v1/organizations/me/projects",
        json={"name": "Old Name", "slug": "old-name"},
        headers=org_headers,
    )
    project_id = create_resp.json()["id"]

    resp = client.patch(
        f"/v1/organizations/me/projects/{project_id}",
        json={"name": "New Name"},
        headers=org_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"


def test_delete_project(client, auth_headers):
    engine = get_engine("sqlite:///:memory:")
    org_id = seed_org(engine)

    from app.api.keys.service import store as api_key_store
    key_data = api_key_store.create_key(label="admin-key", organization_id=org_id)
    org_headers = {"x-zam-ai-key": key_data["key"]}

    create_resp = client.post(
        "/v1/organizations/me/projects",
        json={"name": "Delete Me", "slug": "delete-me"},
        headers=org_headers,
    )
    project_id = create_resp.json()["id"]

    resp = client.delete(f"/v1/organizations/me/projects/{project_id}", headers=org_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "deleted"

    resp = client.get(f"/v1/organizations/me/projects/{project_id}", headers=org_headers)
    assert resp.status_code == 404


def test_project_api_key_crud(client, auth_headers):
    engine = get_engine("sqlite:///:memory:")
    org_id = seed_org(engine)

    from app.api.keys.service import store as api_key_store
    key_data = api_key_store.create_key(label="admin-key", organization_id=org_id)
    org_headers = {"x-zam-ai-key": key_data["key"]}

    create_resp = client.post(
        "/v1/organizations/me/projects",
        json={"name": "Keyed", "slug": "keyed"},
        headers=org_headers,
    )
    project_id = create_resp.json()["id"]

    create_key_resp = client.post(
        f"/v1/organizations/me/projects/{project_id}/api-keys",
        json={"label": "project-key"},
        headers=org_headers,
    )
    assert create_key_resp.status_code == 201
    key_id = create_key_resp.json()["id"]

    list_resp = client.get(
        f"/v1/organizations/me/projects/{project_id}/api-keys",
        headers=org_headers,
    )
    assert list_resp.status_code == 200
    assert len(list_resp.json()["keys"]) == 1

    rotate_resp = client.post(
        f"/v1/organizations/me/projects/{project_id}/api-keys/{key_id}/rotate",
        headers=org_headers,
    )
    assert rotate_resp.status_code == 200

    revoke_resp = client.post(
        f"/v1/organizations/me/projects/{project_id}/api-keys/{key_id}/revoke",
        headers=org_headers,
    )
    assert revoke_resp.status_code == 200
    assert revoke_resp.json()["revoked"] is True


# ─── Org Usage Tests ──────────────────────────────────────────────────


def test_get_org_usage_empty(client, auth_headers):
    engine = get_engine("sqlite:///:memory:")
    org_id = seed_org(engine)

    from app.api.keys.service import store as api_key_store
    key_data = api_key_store.create_key(label="admin-key", organization_id=org_id)
    org_headers = {"x-zam-ai-key": key_data["key"]}

    resp = client.get("/v1/organizations/me/usage", headers=org_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["organization_id"] == org_id
    assert data["totals"]["total_requests"] == 0
