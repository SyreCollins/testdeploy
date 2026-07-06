import hashlib
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from app.core.config import get_settings
from app.rag.chunker import Chunker
from app.rag.embeddings.base import BaseEmbeddingProvider
from app.rag.embeddings.mock import MockEmbeddingProvider
from app.rag.normalizer import clean_whitespace, normalize_dosage_units
from app.rag.parsers import get_parser
from app.rag.registry import RagRegistry
from app.rag.schemas import DocumentChunk, MedicalSource
from app.rag.vector_store.base import BaseVectorStore
from app.rag.vector_store.memory import MemoryVectorStore

logger = logging.getLogger("zam-ai-core-api.ingestion-service")


class IngestionService:
    def __init__(
        self,
        registry: RagRegistry | None = None,
        embedding_provider: BaseEmbeddingProvider | None = None,
        vector_store: BaseVectorStore | None = None,
        chunker: Chunker | None = None,
        auto_init_db: bool = True,
    ) -> None:
        self.registry = registry or RagRegistry()
        self.embedding_provider = embedding_provider or MockEmbeddingProvider()
        self.vector_store = vector_store or MemoryVectorStore()
        self.chunker = chunker or Chunker()
        if auto_init_db:
            self.registry.init_db()

    def register_source(
        self,
        name: str,
        publisher: str,
        version: str,
        license_status: str,
        jurisdiction: str,
        trust_tier: int | None = None,
        publication_date: str | None = None,
    ) -> MedicalSource:
        return self.registry.register_source(
            name=name,
            publisher=publisher,
            version=version,
            license_status=license_status,
            jurisdiction=jurisdiction,
            publication_date=publication_date,
            trust_tier=trust_tier,
        )

    def ingest_document(
        self,
        source: MedicalSource,
        file_path: str,
        title: str | None = None,
        document_version: str | None = None,
    ) -> dict[str, Any]:
        resolved_title = title or os.path.basename(file_path)
        checksum = self._compute_checksum(file_path)

        document = self.registry.register_document(
            source_id=source.id,
            title=resolved_title,
            file_path=file_path,
            checksum=checksum,
            document_version=document_version,
        )

        if document.status == "parsed":
            logger.info(f"Document already ingested, skipping: {resolved_title}")
            return {"document_id": document.id, "status": "skipped", "chunks_count": 0}

        parser = get_parser(file_path)
        raw_sections = parser.parse(file_path)
        logger.info(f"Parsed {len(raw_sections)} sections from {resolved_title}")

        all_chunks: list[DocumentChunk] = []
        for i, section in enumerate(raw_sections):
            section = self._normalize_section(section)
            chunks = self.chunker.chunk_section(section, document.id)
            for chunk in chunks:
                chunk.source_trust_tier = source.trust_tier
                chunk.drug_entity_id = self._resolve_drug_entity_id(
                    chunk.generic_name, chunk.brand_names
                )
            all_chunks.extend(chunks)
            if (i + 1) % 500 == 0:
                logger.info(f"  Chunked {i + 1}/{len(raw_sections)} sections ({len(all_chunks)} chunks so far)")

        logger.info(f"Generated {len(all_chunks)} chunks from {resolved_title}")

        if all_chunks:
            texts = [c.text_content for c in all_chunks]
            BATCH_SIZE = 100
            batches = [texts[i:i + BATCH_SIZE] for i in range(0, len(texts), BATCH_SIZE)]
            all_embeddings: list[list[float]] = []
            concurrency = get_settings().embedding_batch_concurrency
            with ThreadPoolExecutor(max_workers=concurrency) as executor:
                future_map = {
                    executor.submit(self.embedding_provider.embed_documents, batch): idx
                    for idx, batch in enumerate(batches)
                }
                results = [None] * len(batches)
                for future in as_completed(future_map):
                    idx = future_map[future]
                    results[idx] = future.result()
                    start = idx * BATCH_SIZE
                    end = min(start + BATCH_SIZE, len(texts))
                    logger.info(
                        f"  Embedding batch {idx + 1}/{len(batches)} "
                        f"({start}-{end} of {len(texts)})"
                    )
            for r in results:
                all_embeddings.extend(r)
            logger.info(f"Embedded {len(all_embeddings)} chunks")
            self.registry.add_chunks(all_chunks)
            self.vector_store.upsert_chunks(all_chunks, all_embeddings)
            logger.info(f"Upserted {len(all_embeddings)} chunks to vector store")

        self.registry.update_document_status(document.id, "parsed")
        logger.info(
            f"Ingested {len(all_chunks)} chunks from {resolved_title}"
        )
        return {
            "document_id": document.id,
            "status": "ingested",
            "chunks_count": len(all_chunks),
        }

    @staticmethod
    def _compute_checksum(file_path: str) -> str:
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for block in iter(lambda: f.read(65536), b""):
                hasher.update(block)
        return hasher.hexdigest()

    @staticmethod
    def _normalize_section(section: dict[str, Any]) -> dict[str, Any]:
        text = section.get("text_content", "")
        text = clean_whitespace(text)
        text = normalize_dosage_units(text)
        section["text_content"] = text
        return section

    @staticmethod
    def _resolve_drug_entity_id(
        generic_name: str | None, brand_names: str | None
    ) -> str | None:
        key = (generic_name or "").strip().lower()
        if not key and brand_names:
            key = brand_names.split(",")[0].strip().lower()
        if not key:
            return None
        return hashlib.md5(key.encode()).hexdigest()[:16]


class RetrievalService:
    def __init__(
        self,
        registry: RagRegistry | None = None,
        embedding_provider: BaseEmbeddingProvider | None = None,
        vector_store: BaseVectorStore | None = None,
    ) -> None:
        self.registry = registry or RagRegistry()
        self.embedding_provider = embedding_provider or MockEmbeddingProvider()
        self.vector_store = vector_store or MemoryVectorStore()

    def search(
        self,
        query: str,
        limit: int = 10,
        generic_name_filter: str | None = None,
        chunk_type_filter: str | None = None,
        min_trust_tier: int | None = None,
    ) -> list[dict[str, Any]]:
        query_vector = self.embedding_provider.embed_query(query)
        results = self.vector_store.search(
            query_vector=query_vector,
            query_text=query,
            limit=limit * 2,
            generic_name_filter=generic_name_filter,
        )

        filtered = []
        for r in results:
            meta = r.get("metadata", {})
            chunk_tier = meta.get("chunk_tier") or meta.get("source_trust_tier")
            if min_trust_tier is not None and (chunk_tier is None or chunk_tier > min_trust_tier):
                continue
            chunk_type = meta.get("chunk_type")
            if chunk_type_filter and chunk_type != chunk_type_filter:
                continue

            source_meta = self.registry.get_source_metadata_for_chunk(r["chunk_id"])
            citation = {
                "citation_id": r["chunk_id"],
                "text_content": r["text_content"],
                "score": r["score"],
                "section_path": meta.get("section_path"),
                "page_number": meta.get("page_number"),
                "generic_name": meta.get("generic_name"),
                "chunk_type": chunk_type,
                "source_name": (source_meta or {}).get("source_name"),
                "source_version": (source_meta or {}).get("source_version"),
                "source_trust_tier": chunk_tier,
                "document_title": (source_meta or {}).get("document_title"),
            }
            filtered.append(citation)
            if len(filtered) >= limit:
                break

        return filtered
