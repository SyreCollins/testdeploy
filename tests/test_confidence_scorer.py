import pytest

from app.ai.scoring.confidence import ConfidenceScorer


@pytest.fixture
def scorer() -> ConfidenceScorer:
    return ConfidenceScorer()


class TestConfidenceScorer:
    def test_empty_citations(self, scorer: ConfidenceScorer) -> None:
        result = scorer.compute([])
        assert result["retrieval"] == 0.0
        assert result["grounding"] == 0.0
        assert result["overall"] == 0.0

    def test_single_citation_tier_1(self, scorer: ConfidenceScorer) -> None:
        citations = [{"score": 0.9, "source_trust_tier": 1}]
        result = scorer.compute(citations)
        assert result["retrieval"] > 0.0
        assert result["retrieval"] <= 0.9

    def test_single_citation_tier_4(self, scorer: ConfidenceScorer) -> None:
        citations = [{"score": 0.9, "source_trust_tier": 4}]
        result = scorer.compute(citations)
        tier_1 = scorer.compute([{"score": 0.9, "source_trust_tier": 1}])
        # Tier 4 (weight 0.6) should score lower than tier 1 (weight 1.0)
        assert result["retrieval"] < tier_1["retrieval"]

    def test_multiple_citations_boost_confidence(self, scorer: ConfidenceScorer) -> None:
        single = scorer.compute([{"score": 0.8, "source_trust_tier": 1}])
        multi = scorer.compute(
            [{"score": 0.8, "source_trust_tier": 1} for _ in range(5)]
        )
        # More citations with same score should give higher confidence
        assert multi["retrieval"] > single["retrieval"]

    def test_coverage_saturation(self, scorer: ConfidenceScorer) -> None:
        five = scorer.compute(
            [{"score": 0.8, "source_trust_tier": 1} for _ in range(5)]
        )
        ten = scorer.compute(
            [{"score": 0.8, "source_trust_tier": 1} for _ in range(10)]
        )
        # Beyond saturation, more chunks shouldn't meaningfully increase score
        assert abs(ten["retrieval"] - five["retrieval"]) < 0.01

    def test_no_trust_tier(self, scorer: ConfidenceScorer) -> None:
        result = scorer.compute([{"score": 0.8}])
        assert result["retrieval"] > 0.0

    def test_overall_equals_retrieval_when_no_grounding(
        self, scorer: ConfidenceScorer
    ) -> None:
        result = scorer.compute([{"score": 0.8, "source_trust_tier": 1}])
        assert result["overall"] == result["retrieval"]
        assert result["grounding"] == 0.0

    def test_compute_returns_all_keys(self, scorer: ConfidenceScorer) -> None:
        result = scorer.compute(
            [{"score": 0.85, "source_trust_tier": 1}], "some response"
        )
        assert set(result.keys()) == {"overall", "grounding", "retrieval"}

    def test_mixed_trust_tiers(self, scorer: ConfidenceScorer) -> None:
        citations = [
            {"score": 0.9, "source_trust_tier": 1},
            {"score": 0.8, "source_trust_tier": 3},
            {"score": 0.7, "source_trust_tier": 4},
        ]
        result = scorer.compute(citations)
        assert 0.0 < result["retrieval"] <= 0.9
