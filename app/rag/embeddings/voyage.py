import asyncio
import logging

from llama_index.embeddings.voyageai import VoyageEmbedding as LiVoyageEmbedding

from app.rag.embeddings.base import BaseEmbeddingProvider

logger = logging.getLogger("zam-ai-core-api.voyage-embedding")


class VoyageEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(
        self,
        api_key: str,
        model: str = "voyage-3",
        dimension: int = 1024,
    ) -> None:
        self.dimension = dimension
        logger.info(f"Initializing VoyageEmbeddingProvider (model={model})")
        self._model = LiVoyageEmbedding(
            model_name=model,
            voyage_api_key=api_key,
            output_dimension=dimension,
        )

    async def embed_query(self, text: str) -> list[float]:
        return await asyncio.to_thread(self._model.get_query_embedding, text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._model.get_text_embedding_batch(texts)

    def get_dimension(self) -> int:
        return self.dimension
