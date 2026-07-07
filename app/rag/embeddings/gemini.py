import asyncio
import logging

from llama_index.embeddings.gemini import GeminiEmbedding as LiGeminiEmbedding

from app.rag.embeddings.base import BaseEmbeddingProvider

logger = logging.getLogger("zam-ai-core-api.gemini-embedding")


class GeminiEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(
        self,
        api_key: str,
        model: str = "models/embedding-001",
        dimension: int = 768,
    ) -> None:
        self.dimension = dimension
        logger.info(f"Initializing GeminiEmbeddingProvider (model={model})")
        self._model = LiGeminiEmbedding(
            model_name=model,
            api_key=api_key,
            task_type="retrieval_document",
        )

    async def embed_query(self, text: str) -> list[float]:
        return await asyncio.to_thread(self._model.get_query_embedding, text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._model.get_text_embedding_batch(texts)

    def get_dimension(self) -> int:
        return self.dimension
