import os
from datetime import UTC, datetime

import pytest
from sqlmodel import Session, select

from app.core.config import Settings, get_settings
from app.db.engine import get_engine
from app.db.models.platform import Organization
from app.db.models.usage import UsageRecord

BOOTSTRAP_ORG_ID = 1


def _seed_usage(app, org_id: int = BOOTSTRAP_ORG_ID):
    engine = get_engine(get_settings().database_url)
    with Session(engine) as session:
        org = session.get(Organization, org_id)
        if org is None:
            org = Organization(id=org_id, clerk_org_id="org_test", name="Test Org", slug="test-org", plan="free", is_active=True, created_at=datetime.now(UTC))
            session.add(org)
            session.commit()

        records = [
            UsageRecord(organization_id=org_id, date="2026-07-28", endpoint="/v1/ai/medical-qa", request_count=10, prompt_tokens=1000, completion_tokens=500),
            UsageRecord(organization_id=org_id, date="2026-07-28", endpoint="/v1/ai/drug-info", request_count=5, prompt_tokens=500, completion_tokens=250),
            UsageRecord(organization_id=org_id, date="2026-07-29", endpoint="/v1/ai/medical-qa", request_count=20, prompt_tokens=2000, completion_tokens=1000),
            UsageRecord(organization_id=org_id, date="2026-07-29", endpoint="/v1/ai/interactions/check", request_count=8, prompt_tokens=800, completion_tokens=400),
            UsageRecord(organization_id=org_id, date="2026-07-30", endpoint="/v1/ai/medical-qa", request_count=15, prompt_tokens=1500, completion_tokens=750),
        ]
        for r in records:
            session.add(r)
        session.commit()


@pytest.fixture
def authed_client(app):
    from fastapi.testclient import TestClient
    _seed_usage(app)
    from app.api.keys.service import store as api_key_store
    key_result = api_key_store.create_key(
        label="analytics-test",
        organization_id=BOOTSTRAP_ORG_ID,
        is_admin=True,
    )
    client = TestClient(app)
    client.headers.update({"x-zam-ai-key": key_result["key"]})
    return client


@pytest.fixture
def admin_auth_headers(app):
    from app.api.keys.service import store as api_key_store
    _seed_usage(app)
    key = api_key_store.create_key(label="admin-test", organization_id=BOOTSTRAP_ORG_ID)
    return {"x-zam-ai-key": key["key"]}


class TestOrgAnalytics:
    def test_summary_returns_correct_totals(self, authed_client):
        resp = authed_client.get("/v1/organizations/me/analytics/summary?from=2026-07-28&to=2026-07-30")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_requests"] == 58
        assert data["total_prompt_tokens"] == 5800
        assert data["total_completion_tokens"] == 2900
        assert data["unique_endpoints"] == 3
        assert data["period_days"] == 3
        assert abs(data["daily_avg_requests"] - 58 / 3) < 0.1

    def test_summary_defaults_to_30_days(self, authed_client):
        resp = authed_client.get("/v1/organizations/me/analytics/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert data["from_date"] is not None
        assert data["to_date"] is not None

    def test_summary_no_data(self, authed_client):
        resp = authed_client.get("/v1/organizations/me/analytics/summary?from=2020-01-01&to=2020-01-01")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_requests"] == 0
        assert data["unique_endpoints"] == 0

    def test_trends_returns_daily_breakdown(self, authed_client):
        resp = authed_client.get("/v1/organizations/me/analytics/trends?from=2026-07-28&to=2026-07-30")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["trends"]) == 3
        assert data["trends"][0]["date"] == "2026-07-28"
        assert data["trends"][0]["requests"] == 15
        assert data["trends"][1]["requests"] == 28
        assert data["trends"][2]["requests"] == 15

    def test_trends_fills_gaps(self, authed_client):
        resp = authed_client.get("/v1/organizations/me/analytics/trends?from=2026-07-27&to=2026-07-30")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["trends"]) == 4
        assert data["trends"][0]["requests"] == 0

    def test_top_endpoints(self, authed_client):
        resp = authed_client.get("/v1/organizations/me/analytics/top-endpoints?from=2026-07-28&to=2026-07-30")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["endpoints"]) == 3
        assert data["endpoints"][0]["endpoint"] == "/v1/ai/medical-qa"
        assert data["endpoints"][0]["request_count"] == 45
        assert data["endpoints"][0]["percentage"] > 0

    def test_top_endpoints_limit(self, authed_client):
        resp = authed_client.get("/v1/organizations/me/analytics/top-endpoints?from=2026-07-28&to=2026-07-30&limit=2")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["endpoints"]) == 2

    def test_requires_auth(self, client, app):
        resp = client.get("/v1/organizations/me/analytics/summary")
        assert resp.status_code == 401


class TestAdminAnalytics:
    def _ensure_org_exists(self, app, org_id: int, name: str, slug: str):
        engine = get_engine(get_settings().database_url)
        with Session(engine) as session:
            existing = session.get(Organization, org_id)
            if existing is None:
                org = Organization(id=org_id, clerk_org_id=f"org_{org_id}", name=name, slug=slug, plan="free", is_active=True, created_at=datetime.now(UTC))
                session.add(org)
                session.commit()

    def test_overview_returns_cross_org_totals(self, authed_client, app):
        self._ensure_org_exists(app, 2, "Org 2", "org-2")
        _seed_usage(app, org_id=2)

        resp = authed_client.get("/v1/admin/analytics/overview?from=2026-07-28&to=2026-07-30")
        assert resp.status_code == 200
        data = resp.json()
        # org 1 is seeded by the fixture (58) + org 2 seeded here (58) = 116
        assert data["total_requests"] == 116
        assert data["total_organizations"] >= 2
        assert data["total_prompt_tokens"] == 11600
        assert data["total_completion_tokens"] == 5800
        assert data["top_workflow"] == "/v1/ai/medical-qa"

    def test_overview_requires_auth(self, client, app):
        resp = client.get("/v1/admin/analytics/overview")
        assert resp.status_code == 401

    def test_orgs_returns_per_org_breakdown(self, authed_client, app):
        self._ensure_org_exists(app, 2, "Org Beta", "org-beta")
        engine = get_engine(get_settings().database_url)
        with Session(engine) as session:
            records = [
                UsageRecord(organization_id=2, date="2026-07-28", endpoint="/v1/ai/medical-qa", request_count=100, prompt_tokens=10000, completion_tokens=5000),
            ]
            for r in records:
                session.add(r)
            session.commit()

        resp = authed_client.get("/v1/admin/analytics/orgs?from=2026-07-28&to=2026-07-30")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 2
        orgs_by_id = {o["organization_id"]: o for o in data["organizations"]}
        assert orgs_by_id[2]["total_requests"] == 100
        assert orgs_by_id[1]["total_requests"] == 58

    def test_orgs_sorts_by_requests(self, authed_client, app):
        self._ensure_org_exists(app, 2, "Org B", "org-b")
        engine = get_engine(get_settings().database_url)
        with Session(engine) as session:
            session.add(UsageRecord(organization_id=2, date="2026-07-28", endpoint="/v1/ai/medical-qa", request_count=100, prompt_tokens=10000, completion_tokens=5000))
            session.commit()

        resp = authed_client.get("/v1/admin/analytics/orgs?from=2026-07-28&to=2026-07-30")
        data = resp.json()
        assert data["organizations"][0]["total_requests"] >= data["organizations"][1]["total_requests"]
