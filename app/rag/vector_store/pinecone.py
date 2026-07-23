import asyncio
import logging
from typing import Any

from llama_index.core.schema import TextNode
from llama_index.core.vector_stores import (
    MetadataFilter,
    MetadataFilters,
    VectorStoreQuery,
)
from llama_index.vector_stores.pinecone import PineconeVectorStore as LiPineconeVectorStore

from app.db.models.rag import DocumentChunk
from app.rag.vector_store.base import BaseVectorStore

logger = logging.getLogger("zam-ai-core-api.pinecone-vector-store")


class PineconeVectorStore(BaseVectorStore):
    def __init__(
        self,
        api_key: str,
        index_name: str,
    ) -> None:
        logger.info(f"Connecting to Pinecone index '{index_name}'")
        self._store = LiPineconeVectorStore.from_params(
            api_key=api_key,
            index_name=index_name,
            text_key="text_content",
        )

    def upsert_chunks(self, chunks: list[DocumentChunk], embeddings: list[list[float]]) -> None:
        logger.info(f"Upserting {len(chunks)} chunks into Pinecone")
        nodes = []
        for chunk, embedding in zip(chunks, embeddings, strict=False):
            metadata = self._build_metadata(chunk)
            node = TextNode(
                id_=chunk.id,
                text=chunk.text_content,
                embedding=embedding,
                metadata=metadata,
            )
            nodes.append(node)
        self._store.add(nodes)

    async def search(
        self,
        query_vector: list[float],
        query_text: str,
        limit: int = 5,
        generic_name_filter: str | None = None,
    ) -> list[dict]:
        filters = None
        if generic_name_filter:
            filters = MetadataFilters(
                filters=[
                    MetadataFilter(key="generic_name", value=generic_name_filter.lower()),
                ],
            )

        query = VectorStoreQuery(
            query_embedding=query_vector,
            similarity_top_k=limit,
            filters=filters,
        )

        result = await asyncio.to_thread(self._store.query, query)

        results = []
        for node, score in zip(result.nodes or [], result.similarities or [], strict=False):
            meta = node.metadata or {}
            results.append({
                "chunk_id": node.node_id,
                "text_content": node.text or "",
                "score": round(score, 4),
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
            "document_id": str(chunk.document_id),
            "section_path": chunk.section_path,
            "page_number": chunk.page_number,
            "generic_name": chunk.generic_name,
            "brand_names": chunk.brand_names,
            "chunk_type": chunk.chunk_type,
            "source_trust_tier": chunk.source_trust_tier,
        }
        return {k: v for k, v in meta.items() if v is not None}
