import logging

from app.ai.citation.models import Citation

logger = logging.getLogger("zam-ai-core-api.citation-engine")

MAX_CITATIONS = 5


class CitationEngine:
    def build_citations(self, results: list[dict]) -> list[Citation]:
        return [Citation.from_retrieval_result(r) for r in results]

    def build_evidence_for_prompt(self, citations: list[Citation]) -> list[dict]:
        return [
            {
                "source_name": c.source_name,
                "source_version": c.source_version,
                "text_content": c.text_content,
            }
            for c in citations
        ]

    def format_for_response(self, citations: list[Citation]) -> list[dict]:
        return [
            {
                "citation_id": c.citation_id,
                "text_content": c.text_content,
                "score": c.score,
                "source_name": c.source_name,
                "source_version": c.source_version,
                "source_trust_tier": c.source_trust_tier,
                "document_title": c.document_title,
                "section_path": c.section_path,
                "page_number": c.page_number,
            }
            for c in citations
        ]

    def deduplicate(self, citations: list[Citation]) -> list[Citation]:
        seen: set[str] = set()
        unique: list[Citation] = []
        for c in citations:
            if c.citation_id not in seen:
                seen.add(c.citation_id)
                unique.append(c)
        return unique

    def truncate(self, citations: list[Citation], max_count: int = MAX_CITATIONS) -> list[Citation]:
        return citations[:max_count]

    @staticmethod
    def _clean_claim(text: str) -> str:
        cleaned = text.replace("\n- ", " - ").replace("\n", " ")
        return " ".join(cleaned.split())[:200]

    def build_claims(self, citations: list[Citation], max_claims: int = MAX_CITATIONS) -> list[dict]:
        return [
            {
                "claim": self._clean_claim(c.text_content),
                "citation_ids": [c.citation_id],
            }
            for c in citations[:max_claims]
        ]
