import logging

from app.rag.schemas import DocumentChunk
from app.rag.vector_store.base import BaseVectorStore

logger = logging.getLogger("zam-ai-core-api.memory-vector-store")


class MemoryVectorStore(BaseVectorStore):
    """
    An in-memory vector store implementing hybrid search and L2/cosine similarity.
    Ideal for local testing and prototyping without external dependencies.
    """
    def __init__(self) -> None:
        # List of dicts, each having: "chunk": DocumentChunk, "vector": List[float]
        self.storage: list[dict] = []

    def upsert_chunks(self, chunks: list[DocumentChunk], embeddings: list[list[float]]) -> None:
        """Store chunks and their embeddings in-memory."""
        logger.info(f"Upserting {len(chunks)} chunks into memory vector store")
        for chunk, embedding in zip(chunks, embeddings, strict=False):
            # Check if chunk already exists and update, else insert
            existing_idx = next(
                (i for i, item in enumerate(self.storage) if item["chunk"].id == chunk.id),
                None
            )
            item = {"chunk": chunk, "vector": embedding}
            if existing_idx is not None:
                self.storage[existing_idx] = item
            else:
                self.storage.append(item)

    def search(
        self,
        query_vector: list[float],
        query_text: str,
        limit: int = 5,
        generic_name_filter: str | None = None,
    ) -> list[dict]:
        """
        Retrieves matching chunks based on cosine similarity and keyword overlap.
        """
        results = []
        query_keywords = set(query_text.lower().split())

        for item in self.storage:
            chunk: DocumentChunk = item["chunk"]
            vector: list[float] = item["vector"]

            # 1. Apply generic name filter if specified
            if generic_name_filter:
                chunk_generic = (chunk.generic_name or "").lower()
                filter_generic = generic_name_filter.lower()
                if chunk_generic != filter_generic:
                    continue

            # 2. Calculate cosine similarity (dot product since vectors are normalized)
            if len(vector) == len(query_vector):
                similarity = sum(qv * cv for qv, cv in zip(query_vector, vector, strict=False))
            else:
                similarity = 0.0

            # 3. Hybrid boost: increase score for exact keyword matches in text_content
            keyword_matches = 0
            chunk_words = chunk.text_content.lower()
            for word in query_keywords:
                if len(word) > 2 and word in chunk_words:
                    keyword_matches += 1

            # Score formula: semantic similarity (0-1) + small keyword boost (0.05 per keyword)
            hybrid_score = similarity + (keyword_matches * 0.05)

            results.append({
                "chunk_id": chunk.id,
                "text_content": chunk.text_content,
                "score": round(hybrid_score, 4),
                "metadata": {
                    "document_id": chunk.document_id,
                    "section_path": chunk.section_path,
                    "page_number": chunk.page_number,
                    "generic_name": chunk.generic_name,
                    "brand_names": chunk.brand_names,
                    "chunk_type": chunk.chunk_type,
                    "source_trust_tier": chunk.source_trust_tier,
                }
            })

        # Sort by score descending and limit results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
