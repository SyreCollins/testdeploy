from dataclasses import dataclass
from typing import Any


@dataclass
class Citation:
    citation_id: str
    text_content: str
    score: float
    source_name: str | None = None
    source_version: str | None = None
    source_trust_tier: int | None = None
    document_title: str | None = None
    section_path: str | None = None
    page_number: int | None = None
    chunk_type: str | None = None
    generic_name: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}

    @classmethod
    def from_retrieval_result(cls, result: dict) -> "Citation":
        return cls(
            citation_id=result["citation_id"],
            text_content=result["text_content"],
            score=result["score"],
            source_name=result.get("source_name"),
            source_version=result.get("source_version"),
            source_trust_tier=result.get("source_trust_tier"),
            document_title=result.get("document_title"),
            section_path=result.get("section_path"),
            page_number=result.get("page_number"),
            chunk_type=result.get("chunk_type"),
            generic_name=result.get("generic_name"),
        )
