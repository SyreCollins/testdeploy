from abc import ABC, abstractmethod

from app.rag.schemas import DocumentChunk


class BaseVectorStore(ABC):
    @abstractmethod
    def upsert_chunks(self, chunks: list[DocumentChunk], embeddings: list[list[float]]) -> None:
        """
        Upsert a batch of chunks along with their corresponding vector embeddings.
        """
        pass

    @abstractmethod
    def search(
        self,
        query_vector: list[float],
        query_text: str,
        limit: int = 5,
        generic_name_filter: str | None = None,
    ) -> list[dict]:
        """
        Perform a hybrid semantic and keyword search, returning list of dictionary results.
        
        Each returned result dict should contain:
            - "chunk_id": str
            - "text_content": str
            - "score": float (similarity/hybrid score)
            - "metadata": dict (e.g. section_path, page_number, generic_name)
        """
        pass
