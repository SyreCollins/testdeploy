import logging

import voyageai

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
        self.model = model
        self._api_key = api_key
        self._client: voyageai.Client | None = None

    def _ensure_client(self) -> voyageai.Client:
        if self._client is None:
            logger.info(f"Connecting to Voyage API ({self.model})")
            self._client = voyageai.Client(api_key=self._api_key)
        return self._client

    def embed_query(self, text: str) -> list[float]:
        client = self._ensure_client()
        result = client.embed(
            texts=[text],
            model=self.model,
            input_type="query",
        )
        return result.embeddings[0]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        client = self._ensure_client()
        result = client.embed(
            texts=texts,
            model=self.model,
            input_type="document",
        )
        return result.embeddings

    def get_dimension(self) -> int:
        return self.dimension
