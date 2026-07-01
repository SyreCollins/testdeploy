import os
import tempfile
import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


@pytest.fixture(autouse=True)
def _cleanup_db() -> None:
    yield
    for f in os.listdir(tempfile.gettempdir()):
        if f.startswith("test_") and f.endswith(".db"):
            try:
                os.remove(os.path.join(tempfile.gettempdir(), f))
            except OSError:
                pass


def _client() -> TestClient:
    db_path = os.path.join(tempfile.gettempdir(), f"test_{uuid.uuid4().hex}.db")
    settings = Settings(internal_api_keys=["test-key"], database_url=f"sqlite:///{db_path}")
    app = create_app(settings)
    return TestClient(app)


def test_register_source() -> None:
    client = _client()
    resp = client.post(
        "/v1/admin/sources",
        json={
            "name": "NAFDAC",
            "publisher": "NAFDAC",
            "version": "2024",
            "license_status": "active",
            "jurisdiction": "NG",
            "trust_tier": 3,
        },
        headers={"X-Zam-AI-Key": "test-key"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "NAFDAC"
    assert data["trust_tier"] == 3
    assert "id" in data


def test_register_source_requires_auth() -> None:
    client = _client()
    resp = client.post(
        "/v1/admin/sources",
        json={
            "name": "Test",
            "publisher": "T",
            "version": "1",
            "license_status": "active",
            "jurisdiction": "NG",
        },
    )
    assert resp.status_code == 401


def test_ingest_document() -> None:
    client = _client()
    src_resp = client.post(
        "/v1/admin/sources",
        json={
            "name": "TestSrc",
            "publisher": "T",
            "version": "1",
            "license_status": "active",
            "jurisdiction": "NG",
            "trust_tier": 2,
        },
        headers={"X-Zam-AI-Key": "test-key"},
    )
    source_id = src_resp.json()["id"]

    path = os.path.join(tempfile.gettempdir(), "test_api_ing.csv")
    with open(path, "w") as f:
        f.write("Medicine Name,Composition,Uses,Side_effects\n")
        f.write("APIDrug,APIDrug (50mg),Fever,Nausea\n")

    resp = client.post(
        "/v1/admin/documents/ingest",
        json={"source_id": source_id, "file_path": path, "title": "API Test"},
        headers={"X-Zam-AI-Key": "test-key"},
    )
    os.remove(path)

    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "ingested"
    assert data["chunks_count"] == 3


def test_ingest_missing_source() -> None:
    client = _client()
    resp = client.post(
        "/v1/admin/documents/ingest",
        json={"source_id": 999, "file_path": "nope.csv"},
        headers={"X-Zam-AI-Key": "test-key"},
    )
    assert resp.status_code == 404


def test_search() -> None:
    client = _client()

    src_resp = client.post(
        "/v1/admin/sources",
        json={
            "name": "SearchSrc",
            "publisher": "S",
            "version": "1",
            "license_status": "active",
            "jurisdiction": "NG",
            "trust_tier": 1,
        },
        headers={"X-Zam-AI-Key": "test-key"},
    )
    source_id = src_resp.json()["id"]

    path = os.path.join(tempfile.gettempdir(), "test_search.csv")
    with open(path, "w") as f:
        f.write("Medicine Name,Composition,Uses,Side_effects\n")
        f.write("SearchDrug,SearchDrug (100mg),Pain relief,Dizziness\n")

    client.post(
        "/v1/admin/documents/ingest",
        json={"source_id": source_id, "file_path": path},
        headers={"X-Zam-AI-Key": "test-key"},
    )
    os.remove(path)

    resp = client.post(
        "/v1/retrieval/search",
        json={"query": "pain", "limit": 5},
        headers={"X-Zam-AI-Key": "test-key"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] > 0
    assert len(data["results"]) > 0


def test_search_with_filters() -> None:
    client = _client()

    src_resp = client.post(
        "/v1/admin/sources",
        json={
            "name": "FilterSrc",
            "publisher": "F",
            "version": "1",
            "license_status": "active",
            "jurisdiction": "NG",
            "trust_tier": 2,
        },
        headers={"X-Zam-AI-Key": "test-key"},
    )
    source_id = src_resp.json()["id"]

    path = os.path.join(tempfile.gettempdir(), "test_filt2.csv")
    with open(path, "w") as f:
        f.write("Medicine Name,Composition,Uses,Side_effects\n")
        f.write("FilterDrug,FilterDrug (200mg),Fever relief,Nausea\n")

    client.post(
        "/v1/admin/documents/ingest",
        json={"source_id": source_id, "file_path": path},
        headers={"X-Zam-AI-Key": "test-key"},
    )
    os.remove(path)

    resp = client.post(
        "/v1/retrieval/search",
        json={"query": "fever", "chunk_type_filter": "indication", "limit": 5},
        headers={"X-Zam-AI-Key": "test-key"},
    )
    assert resp.status_code == 200
    for r in resp.json()["results"]:
        assert r["chunk_type"] == "indication"
