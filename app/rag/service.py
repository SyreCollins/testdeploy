import hashlib
import logging
import os
import threading
import time
from typing import Any

from app.core.config import get_settings
from app.rag.chunker import Chunker
from app.rag.embeddings.base import BaseEmbeddingProvider
from app.rag.embeddings.mock import MockEmbeddingProvider
from app.rag.normalizer import clean_whitespace, normalize_dosage_units
from app.rag.parsers import get_parser
from app.rag.registry import RagRegistry
from app.db.models.rag import DocumentChunk, MedicalSource
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
            settings = get_settings()
            timeout = settings.embedding_batch_timeout
            max_retries = 3

            for idx, batch in enumerate(batches):
                logger.info(
                    f"  Embedding batch {idx + 1}/{len(batches)} "
                    f"({len(batch)} chunks)..."
                )

                for attempt in range(max_retries):
                    output: list[list[list[float]] | None] = [None]
                    exc: list[BaseException | None] = [None]

                    def _embed(b=batch, out=output, ex=exc):
                        try:
                            out[0] = self.embedding_provider.embed_documents(b)
                        except BaseException as e:
                            ex[0] = e

                    t = threading.Thread(target=_embed, daemon=True)
                    t.start()
                    t.join(timeout=timeout)

                    if not t.is_alive() and exc[0] is None:
                        all_embeddings.extend(output[0])
                        break

                    if t.is_alive():
                        msg = f"  Batch {idx+1} timed out (attempt {attempt+1}/{max_retries})"
                    else:
                        msg = f"  Batch {idx+1} failed: {exc[0]} (attempt {attempt+1}/{max_retries})"
                    logger.warning(msg)

                    if attempt < max_retries - 1:
                        wait = 2 ** attempt
                        logger.info(f"  Retrying in {wait}s...")
                        time.sleep(wait)
                else:
                    if t.is_alive():
                        raise TimeoutError(
                            f"Batch {idx+1} did not complete after "
                            f"{max_retries} attempts ({timeout}s each)"
                        )
                    raise exc[0]  # type: ignore[arg-type]

                logger.info(f"  Batch {idx + 1}/{len(batches)} complete")

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

    async def search(
        self,
        query: str,
        limit: int = 10,
        generic_name_filter: str | None = None,
        chunk_type_filter: str | None = None,
        min_trust_tier: int | None = None,
    ) -> list[dict[str, Any]]:
        query_vector = await self.embedding_provider.embed_query(query)
        results = await self.vector_store.search(
            query_vector=query_vector,
            query_text=query,
            limit=limit * 2,
            generic_name_filter=generic_name_filter,
        )

        seen: list[dict] = []
        chunk_ids: list[str] = []
        for r in results:
            meta = r.get("metadata", {})
            chunk_tier = meta.get("chunk_tier") or meta.get("source_trust_tier")
            if min_trust_tier is not None and (chunk_tier is None or chunk_tier > min_trust_tier):
                continue
            chunk_type = meta.get("chunk_type")
            if chunk_type_filter and chunk_type != chunk_type_filter:
                continue
            seen.append(r)
            chunk_ids.append(r["chunk_id"])

        metadata_map = self.registry.get_chunk_metadata_batch(chunk_ids)

        filtered = []
        for r in seen:
            meta = r.get("metadata", {})
            chunk_tier = meta.get("chunk_tier") or meta.get("source_trust_tier")
            chunk_type = meta.get("chunk_type")
            source_meta = metadata_map.get(r["chunk_id"]) or {}
            citation = {
                "citation_id": r["chunk_id"],
                "text_content": r["text_content"],
                "score": r["score"],
                "section_path": meta.get("section_path"),
                "page_number": meta.get("page_number"),
                "generic_name": meta.get("generic_name"),
                "chunk_type": chunk_type,
                "source_name": source_meta.get("source_name"),
                "source_version": source_meta.get("source_version"),
                "source_trust_tier": chunk_tier,
                "document_title": source_meta.get("document_title"),
            }
            filtered.append(citation)
            if len(filtered) >= limit:
                break

        return filtered
