import hashlib
import random

from app.rag.embeddings.base import BaseEmbeddingProvider


class MockEmbeddingProvider(BaseEmbeddingProvider):
    """
    A mock embedding provider that generates deterministic pseudo-random vectors
    seeded by the text content. Useful for fast, offline testing.
    """
    def __init__(self, dimension: int = 768) -> None:
        self.dimension = dimension

    def embed_query(self, text: str) -> list[float]:
        return self._generate_deterministic_vector(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._generate_deterministic_vector(text) for text in texts]

    def get_dimension(self) -> int:
        return self.dimension

    def _generate_deterministic_vector(self, text: str) -> list[float]:
        # Hash the text to seed the random generator deterministically
        seed = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16) % (2**32)
        rng = random.Random(seed)
        
        # Generate dimension-sized vector of floats between -1.0 and 1.0
        # Normalize to unit length (L2 norm)
        raw_vector = [rng.uniform(-1.0, 1.0) for _ in range(self.dimension)]
        norm = sum(x*x for x in raw_vector) ** 0.5
        if norm > 0:
            return [x / norm for x in raw_vector]
        return raw_vector
