import asyncio
import logging
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.db.models.rag import DocumentChunk
from app.rag.vector_store.base import BaseVectorStore

logger = logging.getLogger("zam-ai-core-api.qdrant-vector-store")


class QdrantVectorStore(BaseVectorStore):
    def __init__(
        self,
        url: str = "http://localhost:6333",
        api_key: str | None = None,
        collection_name: str = "zam-ai",
        prefer_grpc: bool = False,
    ) -> None:
        self._collection_name = collection_name
        logger.info(f"Connecting to Qdrant at '{url}' (collection: {collection_name})")
        self._client = QdrantClient(
            url=url,
            api_key=api_key,
            prefer_grpc=prefer_grpc,
        )

    def _ensure_collection(self, dimension: int) -> None:
        if not self._client.collection_exists(self._collection_name):
            logger.info(f"Creating Qdrant collection '{self._collection_name}' (dim={dimension})")
            self._client.create_collection(
                collection_name=self._collection_name,
                vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
            )

    def upsert_chunks(self, chunks: list[DocumentChunk], embeddings: list[list[float]]) -> None:
        if not chunks:
            return

        dimension = len(embeddings[0])
        self._ensure_collection(dimension)

        points = []
        for chunk, embedding in zip(chunks, embeddings, strict=False):
            payload = self._build_payload(chunk)
            points.append(
                PointStruct(
                    id=chunk.id,
                    vector=embedding,
                    payload=payload,
                )
            )

        self._client.upsert(
            collection_name=self._collection_name,
            points=points,
        )
        logger.info(f"Upserted {len(points)} points into Qdrant")

    async def search(
        self,
        query_vector: list[float],
        query_text: str,
        limit: int = 5,
        generic_name_filter: str | None = None,
    ) -> list[dict]:
        query_filter = None
        if generic_name_filter:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="generic_name",
                        match=MatchValue(value=generic_name_filter.lower()),
                    ),
                ],
            )

        result = await asyncio.to_thread(
            self._client.query_points,
            collection_name=self._collection_name,
            query=query_vector,
            query_filter=query_filter,
            limit=limit,
            with_payload=True,
        )

        results = []
        for point in result.points:
            payload = point.payload or {}
            results.append({
                "chunk_id": str(point.id),
                "text_content": payload.get("text_content", ""),
                "score": round(point.score, 4),
                "metadata": {
                    "document_id": payload.get("document_id"),
                    "section_path": payload.get("section_path"),
                    "page_number": payload.get("page_number"),
                    "generic_name": payload.get("generic_name"),
                    "brand_names": payload.get("brand_names"),
                    "chunk_type": payload.get("chunk_type"),
                    "source_trust_tier": payload.get("source_trust_tier"),
                },
            })

        return results

    @staticmethod
    def _build_payload(chunk: DocumentChunk) -> dict[str, Any]:
        payload = {
            "text_content": chunk.text_content,
            "document_id": str(chunk.document_id),
            "section_path": chunk.section_path,
            "page_number": chunk.page_number,
            "generic_name": chunk.generic_name,
            "brand_names": chunk.brand_names,
            "chunk_type": chunk.chunk_type,
            "source_trust_tier": chunk.source_trust_tier,
        }
        return {k: v for k, v in payload.items() if v is not None}
