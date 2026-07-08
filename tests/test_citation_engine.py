import pytest

from app.ai.citation import Citation, CitationEngine


@pytest.fixture
def engine() -> CitationEngine:
    return CitationEngine()


@pytest.fixture
def sample_results() -> list[dict]:
    return [
        {
            "citation_id": "c1",
            "text_content": "Paracetamol is used for pain relief.",
            "score": 0.92,
            "source_name": "EMDEX",
            "source_version": "2024.1",
            "source_trust_tier": 1,
            "document_title": "Drug Reference",
            "section_path": "Section 1",
            "page_number": 5,
            "chunk_type": "general",
            "generic_name": "paracetamol",
        },
        {
            "citation_id": "c2",
            "text_content": "Ibuprofen is an NSAID.",
            "score": 0.85,
            "source_name": "NAFDAC",
            "source_version": "2023.2",
            "source_trust_tier": 3,
        },
    ]


class TestCitation:
    def test_from_retrieval_result(self, sample_results: list[dict]) -> None:
        citation = Citation.from_retrieval_result(sample_results[0])
        assert citation.citation_id == "c1"
        assert citation.source_name == "EMDEX"
        assert citation.source_trust_tier == 1
        assert citation.chunk_type == "general"

    def test_from_retrieval_result_minimal(self) -> None:
        result = {
            "citation_id": "c3",
            "text_content": "Some text.",
            "score": 0.5,
        }
        citation = Citation.from_retrieval_result(result)
        assert citation.citation_id == "c3"
        assert citation.source_name is None
        assert citation.chunk_type is None

    def test_to_dict(self) -> None:
        citation = Citation(
            citation_id="c1",
            text_content="Text.",
            score=0.9,
            source_name="Test",
        )
        d = citation.to_dict()
        assert d["citation_id"] == "c1"
        assert "generic_name" not in d


class TestCitationEngine:
    def test_build_citations(self, engine: CitationEngine, sample_results: list[dict]) -> None:
        citations = engine.build_citations(sample_results)
        assert len(citations) == 2
        assert all(isinstance(c, Citation) for c in citations)
        assert citations[0].citation_id == "c1"
        assert citations[1].source_trust_tier == 3

    def test_build_citations_empty(self, engine: CitationEngine) -> None:
        assert engine.build_citations([]) == []

    def test_build_evidence_for_prompt(self, engine: CitationEngine, sample_results: list[dict]) -> None:
        citations = engine.build_citations(sample_results)
        evidence = engine.build_evidence_for_prompt(citations)
        assert len(evidence) == 2
        assert evidence[0]["source_name"] == "EMDEX"
        assert "source_trust_tier" not in evidence[0]
        assert "text_content" in evidence[0]

    def test_format_for_response(self, engine: CitationEngine, sample_results: list[dict]) -> None:
        citations = engine.build_citations(sample_results)
        formatted = engine.format_for_response(citations)
        assert len(formatted) == 2
        assert formatted[0]["citation_id"] == "c1"
        assert formatted[0]["source_trust_tier"] == 1
        assert "chunk_type" not in formatted[0]

    def test_deduplicate(self, engine: CitationEngine, sample_results: list[dict]) -> None:
        duplicates = sample_results + [sample_results[0]]
        citations = engine.build_citations(duplicates)
        deduped = engine.deduplicate(citations)
        assert len(deduped) == 2
        assert len(citations) == 3

    def test_truncate(self, engine: CitationEngine) -> None:
        citations = [
            Citation(citation_id=f"c{i}", text_content=f"Text {i}.", score=0.5)
            for i in range(10)
        ]
        truncated = engine.truncate(citations, max_count=3)
        assert len(truncated) == 3
        assert truncated[0].citation_id == "c0"
        assert truncated[-1].citation_id == "c2"

    def test_truncate_default_max(self, engine: CitationEngine) -> None:
        citations = [
            Citation(citation_id=f"c{i}", text_content=f"Text {i}.", score=0.5)
            for i in range(10)
        ]
        truncated = engine.truncate(citations)
        assert len(truncated) == 5

    def test_build_claims(self, engine: CitationEngine, sample_results: list[dict]) -> None:
        citations = engine.build_citations(sample_results)
        claims = engine.build_claims(citations)
        assert len(claims) == 2
        assert claims[0]["claim"] == sample_results[0]["text_content"][:200]
        assert claims[0]["citation_ids"] == ["c1"]

    def test_build_claims_truncated(self, engine: CitationEngine) -> None:
        citations = [
            Citation(citation_id=f"c{i}", text_content=f"Text {i}.", score=0.5)
            for i in range(10)
        ]
        claims = engine.build_claims(citations, max_claims=3)
        assert len(claims) == 3
