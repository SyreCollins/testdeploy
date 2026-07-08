import pytest

from app.ai.grounding import GroundingResult, GroundingVerifier


@pytest.fixture
def verifier() -> GroundingVerifier:
    return GroundingVerifier()


@pytest.fixture
def sample_citations() -> list[dict]:
    return [
        {"text_content": "Paracetamol is used for pain relief and fever reduction."},
        {"text_content": "Ibuprofen is an NSAID used for inflammation."},
        {"text_content": "Amoxicillin is an antibiotic for bacterial infections."},
    ]


class TestGroundingVerifier:
    def test_verify_fully_grounded(self, verifier: GroundingVerifier, sample_citations: list[dict]) -> None:
        response = (
            "Paracetamol is used for pain relief. Ibuprofen is an NSAID for inflammation."
        )
        result = verifier.verify(response, sample_citations)
        assert result.score > 0
        assert result.total_claims >= 2
        assert result.grounded_claims >= 1

    def test_verify_no_grounding(self, verifier: GroundingVerifier, sample_citations: list[dict]) -> None:
        response = "The weather is nice today. Python is a programming language."
        result = verifier.verify(response, sample_citations)
        assert result.score == 0.0

    def test_verify_empty_response(self, verifier: GroundingVerifier) -> None:
        result = verifier.verify("", [])
        assert result.score == 0.0
        assert result.total_claims == 0

    def test_verify_no_citations(self, verifier: GroundingVerifier) -> None:
        result = verifier.verify("Paracetamol helps with pain.", [])
        assert result.score == 0.0

    def test_verify_partial_grounding(self, verifier: GroundingVerifier, sample_citations: list[dict]) -> None:
        response = (
            "Paracetamol is used for pain relief. "
            "The capital of France is Paris."
        )
        result = verifier.verify(response, sample_citations)
        assert result.grounded_claims >= 1
        assert result.total_claims >= 2

    def test_extract_claims(self, verifier: GroundingVerifier) -> None:
        text = "This is the first sentence example. And this is the second sentence here."
        claims = verifier._extract_claims(text)
        assert len(claims) >= 2

    def test_extract_claims_short_sentences(self, verifier: GroundingVerifier) -> None:
        text = "Hi. No. Yes. Paracetamol helps with fever."
        claims = verifier._extract_claims(text)
        assert all(len(c.split()) >= 4 for c in claims)

    def test_tokenize(self, verifier: GroundingVerifier) -> None:
        tokens = verifier._tokenize("Paracetamol helps with fever reduction.")
        assert "paracetamol" in tokens
        assert "helps" in tokens
        assert "fever" in tokens
        assert "reduction" in tokens
        assert "with" not in tokens
        assert "the" not in tokens

    def test_grounding_result_dataclass(self) -> None:
        from app.ai.grounding.models import GroundingDetail

        detail = GroundingDetail(claim="test", is_grounded=True, overlap_score=0.5)
        result = GroundingResult(
            score=0.5,
            grounded_claims=1,
            total_claims=2,
            details=[detail],
        )
        assert result.score == 0.5
        assert len(result.details) == 1
        assert result.details[0].is_grounded


class TestConfidenceScorerGrounding:
    def test_grounding_now_returns_real_score(self) -> None:
        from app.ai.scoring.confidence import ConfidenceScorer

        scorer = ConfidenceScorer()
        citations = [{"text_content": "Aspirin is used for pain relief.", "score": 0.9, "source_trust_tier": 1}]
        score = scorer.score_grounding(
            "Aspirin helps with pain.",
            citations,
        )
        assert score > 0.0

    def test_grounding_with_empty_citations(self) -> None:
        from app.ai.scoring.confidence import ConfidenceScorer

        scorer = ConfidenceScorer()
        score = scorer.score_grounding("Some text.", [])
        assert score == 0.0

    def test_overall_uses_grounding_when_available(self) -> None:
        from app.ai.scoring.confidence import ConfidenceScorer

        scorer = ConfidenceScorer()
        result = scorer.compute(
            [{"text_content": "Aspirin is used for pain relief.", "score": 0.9, "source_trust_tier": 1}],
            "Aspirin helps with pain.",
        )
        assert result["grounding"] > 0.0
        assert result["overall"] != result["retrieval"]
        assert result["overall"] > 0.0

    def test_overall_without_grounding_still_falls_back(self) -> None:
        from app.ai.scoring.confidence import ConfidenceScorer

        scorer = ConfidenceScorer()
        result = scorer.compute(
            [{"text_content": "Aspirin is used for pain relief.", "score": 0.9, "source_trust_tier": 1}],
        )
        assert result["grounding"] == 0.0
        assert result["overall"] == result["retrieval"]
