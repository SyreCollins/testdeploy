from abc import ABC, abstractmethod


class BaseEmbeddingProvider(ABC):
    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """Generate an embedding vector for a single query text."""
        pass

    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Generate embedding vectors for a list of document texts."""
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """Return the vector dimensionality of the embedding model."""
        pass
