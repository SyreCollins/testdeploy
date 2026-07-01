import os
import tempfile

from app.rag.embeddings.mock import MockEmbeddingProvider
from app.rag.registry import RagRegistry
from app.rag.service import IngestionService, RetrievalService
from app.rag.vector_store.memory import MemoryVectorStore


def _make_registry() -> RagRegistry:
    registry = RagRegistry(database_url="sqlite:///:memory:")
    registry.init_db()
    return registry


def test_ingest_and_retrieve() -> None:
    registry = _make_registry()
    embedder = MockEmbeddingProvider()
    store = MemoryVectorStore()
    svc = IngestionService(registry=registry, embedding_provider=embedder, vector_store=store)

    src = svc.register_source(
        name="Test", publisher="TP", version="1.0",
        license_status="active", jurisdiction="NG", trust_tier=2,
    )
    assert src.id is not None
    assert src.trust_tier == 2

    path = os.path.join(tempfile.gettempdir(), "test_ing.csv")
    with open(path, "w") as f:
        f.write("Medicine Name,Composition,Uses,Side_effects,Manufacturer\n")
        f.write("DrugX,DrugX (200mg),Pain relief,Nausea,FakeCorp\n")

    result = svc.ingest_document(src, path, title="Test Doc")
    os.remove(path)

    assert result["status"] == "ingested"
    assert result["chunks_count"] == 3
    assert result["document_id"] is not None


def test_ingest_skip_duplicate() -> None:
    registry = _make_registry()
    embedder = MockEmbeddingProvider()
    store = MemoryVectorStore()
    svc = IngestionService(registry=registry, embedding_provider=embedder, vector_store=store)

    src = svc.register_source(
        name="DupTest", publisher="DP", version="1.0",
        license_status="active", jurisdiction="NG",
    )

    path = os.path.join(tempfile.gettempdir(), "test_dup.csv")
    with open(path, "w") as f:
        f.write("Medicine Name,Composition\n")
        f.write("A,A (100mg)\n")

    r1 = svc.ingest_document(src, path, title="Dup")
    r2 = svc.ingest_document(src, path, title="Dup")
    os.remove(path)

    assert r1["status"] == "ingested"
    assert r2["status"] == "skipped"


def test_retrieval_service_search() -> None:
    registry = _make_registry()
    embedder = MockEmbeddingProvider()
    store = MemoryVectorStore()

    ingest = IngestionService(registry=registry, embedding_provider=embedder, vector_store=store)
    retrieve = RetrievalService(registry=registry, embedding_provider=embedder, vector_store=store)

    src = ingest.register_source(
        name="RetrieveTest", publisher="RT", version="1.0",
        license_status="active", jurisdiction="NG", trust_tier=1,
    )

    path = os.path.join(tempfile.gettempdir(), "test_ret.csv")
    with open(path, "w") as f:
        f.write("Medicine Name,Composition,Uses,Side_effects\n")
        f.write("MedA,MedA (50mg),Headache relief,Drowsiness\n")
        f.write("MedB,MedB (100mg),Fever relief,Nausea\n")

    ingest.ingest_document(src, path, title="Ret Doc")
    os.remove(path)

    results = retrieve.search(query="headache", limit=5)
    assert len(results) > 0
    assert any("Headache" in r["text_content"] for r in results)


def test_retrieval_service_filters() -> None:
    registry = _make_registry()
    embedder = MockEmbeddingProvider()
    store = MemoryVectorStore()

    ingest = IngestionService(registry=registry, embedding_provider=embedder, vector_store=store)
    retrieve = RetrievalService(registry=registry, embedding_provider=embedder, vector_store=store)

    src = ingest.register_source(
        name="FilterTest", publisher="FT", version="1.0",
        license_status="active", jurisdiction="NG", trust_tier=2,
    )

    path = os.path.join(tempfile.gettempdir(), "test_filt.csv")
    with open(path, "w") as f:
        f.write("Medicine Name,Composition,Uses,Side_effects\n")
        f.write("DrugX,DrugX (100mg),Cough relief,Dizziness\n")

    ingest.ingest_document(src, path, title="Filter Doc")
    os.remove(path)

    filtered = retrieve.search(query="cough", chunk_type_filter="indication", limit=10)
    tier_filtered = retrieve.search(query="cough", min_trust_tier=2, limit=10)

    assert len(filtered) > 0
    assert all(r["chunk_type"] == "indication" for r in filtered)
    assert len(tier_filtered) > 0


def test_drug_entity_id_resolution() -> None:
    rid = IngestionService._resolve_drug_entity_id("Amoxicillin", "Amoxil")
    assert rid is not None
    assert isinstance(rid, str)
    assert len(rid) == 16

    rid2 = IngestionService._resolve_drug_entity_id("amoxicillin", None)
    assert rid == rid2
