import logging
import time

import voyageai
from voyageai.error import RateLimitError

from app.rag.embeddings.base import BaseEmbeddingProvider

logger = logging.getLogger("zam-ai-core-api.voyage-embedding")


class VoyageEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(
        self,
        api_key: str,
        model: str = "voyage-3",
        dimension: int = 1024,
        min_interval: float = 21.0,
        max_retries: int = 5,
    ) -> None:
        self.dimension = dimension
        self.model = model
        self._api_key = api_key
        self._client: voyageai.Client | None = None
        self._min_interval = min_interval
        self._last_request: float = 0.0
        self._max_retries = max_retries

    def _rate_limit(self) -> None:
        elapsed = time.monotonic() - self._last_request
        if elapsed < self._min_interval:
            wait = self._min_interval - elapsed
            logger.info(f"Rate limit: waiting {wait:.1f}s before next Voyage request")
            time.sleep(wait)
        self._last_request = time.monotonic()

    def _ensure_client(self) -> voyageai.Client:
        if self._client is None:
            logger.info(f"Connecting to Voyage API ({self.model})")
            self._client = voyageai.Client(api_key=self._api_key)
        return self._client

    def _call_with_retry(self, texts: list[str], input_type: str) -> list[list[float]]:
        client = self._ensure_client()
        last_error: Exception | None = None
        for attempt in range(self._max_retries):
            try:
                result = client.embed(
                    texts=texts,
                    model=self.model,
                    input_type=input_type,
                )
                return result.embeddings
            except RateLimitError as e:
                last_error = e
                wait = 30 * (2 ** attempt)
                logger.warning(f"Voyage rate limited (attempt {attempt + 1}/{self._max_retries}), waiting {wait}s")
                time.sleep(wait)
                self._last_request = time.monotonic()
        raise last_error  # type: ignore[misc]

    def embed_query(self, text: str) -> list[float]:
        self._rate_limit()
        return self._call_with_retry([text], "query")[0]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        self._rate_limit()
        return self._call_with_retry(texts, "document")

    def get_dimension(self) -> int:
        return self.dimension
