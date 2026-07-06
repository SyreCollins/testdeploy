import logging

from llama_index.embeddings.jinaai import JinaEmbedding as LiJinaEmbedding

from app.rag.embeddings.base import BaseEmbeddingProvider

logger = logging.getLogger("zam-ai-core-api.jina-embedding")


class JinaEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(
        self,
        api_key: str,
        model: str = "jina-embeddings-v3",
        dimension: int = 1024,
    ) -> None:
        self.dimension = dimension
        logger.info(f"Initializing JinaEmbeddingProvider (model={model})")
        self._model = LiJinaEmbedding(
            model=model,
            api_key=api_key,
            dimensions=dimension,
            task="text-matching",
        )

    def embed_query(self, text: str) -> list[float]:
        return self._model.get_query_embedding(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._model.get_text_embedding_batch(texts)

    def get_dimension(self) -> int:
        return self.dimension
