import logging
from typing import Any

import pinecone

from app.rag.schemas import DocumentChunk
from app.rag.vector_store.base import BaseVectorStore

logger = logging.getLogger("zam-ai-core-api.pinecone-vector-store")


class PineconeVectorStore(BaseVectorStore):
    def __init__(
        self,
        api_key: str,
        index_name: str,
    ) -> None:
        self._api_key = api_key
        self._index_name = index_name
        self._client: pinecone.Pinecone | None = None
        self._index: pinecone.Index | None = None

    def _ensure_index(self) -> pinecone.Index:
        if self._index is None:
            logger.info(f"Connecting to Pinecone index '{self._index_name}'")
            self._client = pinecone.Pinecone(api_key=self._api_key)
            self._index = self._client.Index(self._index_name)
        return self._index

    def upsert_chunks(self, chunks: list[DocumentChunk], embeddings: list[list[float]]) -> None:
        index = self._ensure_index()
        logger.info(f"Upserting {len(chunks)} chunks into Pinecone index '{self._index_name}'")
        vectors = []
        for chunk, embedding in zip(chunks, embeddings, strict=False):
            metadata = self._build_metadata(chunk)
            vectors.append((chunk.id, embedding, metadata))
        index.upsert(vectors=vectors)

    def search(
        self,
        query_vector: list[float],
        query_text: str,
        limit: int = 5,
        generic_name_filter: str | None = None,
    ) -> list[dict]:
        filter_dict: dict[str, Any] | None = None
        if generic_name_filter:
            filter_dict = {"generic_name": generic_name_filter.lower()}

        index = self._ensure_index()
        response = index.query(
            vector=query_vector,
            top_k=limit,
            include_metadata=True,
            filter=filter_dict,
        )

        results = []
        for match in response.matches:
            meta = match.metadata or {}
            results.append({
                "chunk_id": match.id,
                "text_content": meta.get("text_content", ""),
                "score": round(match.score, 4),
                "metadata": {
                    "document_id": meta.get("document_id"),
                    "section_path": meta.get("section_path"),
                    "page_number": meta.get("page_number"),
                    "generic_name": meta.get("generic_name"),
                    "brand_names": meta.get("brand_names"),
                    "chunk_type": meta.get("chunk_type"),
                    "source_trust_tier": meta.get("source_trust_tier"),
                },
            })

        return results

    @staticmethod
    def _build_metadata(chunk: DocumentChunk) -> dict[str, Any]:
        meta = {
            "text_content": chunk.text_content,
            "document_id": str(chunk.document_id),
            "section_path": chunk.section_path,
            "page_number": chunk.page_number,
            "generic_name": chunk.generic_name,
            "brand_names": chunk.brand_names,
            "chunk_type": chunk.chunk_type,
            "source_trust_tier": chunk.source_trust_tier,
        }
        return {k: v for k, v in meta.items() if v is not None}
