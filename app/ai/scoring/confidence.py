import logging
import math

from app.ai.grounding import GroundingVerifier

logger = logging.getLogger("zam-ai-core-api.confidence-scorer")

TRUST_TIER_WEIGHTS: dict[int | None, float] = {
    1: 1.0,
    2: 0.9,
    3: 0.7,
    4: 0.6,
    None: 0.5,
}

COVERAGE_SATURATION = 5


class ConfidenceScorer:
    def __init__(self, grounding_verifier: GroundingVerifier | None = None) -> None:
        self._grounding = grounding_verifier or GroundingVerifier()

    def score_retrieval(self, citations: list[dict]) -> float:
        if not citations:
            return 0.0

        top = citations[:COVERAGE_SATURATION]
        total = 0.0

        for c in top:
            raw_score = c.get("score", 0.0)
            tier = c.get("source_trust_tier")
            tier_weight = TRUST_TIER_WEIGHTS.get(tier, TRUST_TIER_WEIGHTS[None])
            total += raw_score * tier_weight

        avg = total / len(top)

        coverage = len(top) / COVERAGE_SATURATION
        coverage_factor = 1.0 - math.exp(-3.0 * coverage)

        return round(avg * coverage_factor, 4)

    def score_grounding(self, response_text: str | None, citations: list[dict]) -> float:
        if not response_text or not citations:
            return 0.0
        result = self._grounding.verify(response_text, citations)
        return result.score

    def score_overall(self, retrieval: float, grounding: float) -> float:
        if retrieval == 0.0 and grounding == 0.0:
            return 0.0
        if grounding == 0.0:
            return retrieval
        return round(0.4 * retrieval + 0.6 * grounding, 4)

    def compute(
        self,
        citations: list[dict],
        response_text: str | None = None,
    ) -> dict:
        retrieval = self.score_retrieval(citations)
        grounding = self.score_grounding(response_text, citations)
        overall = self.score_overall(retrieval, grounding)

        return {
            "overall": overall,
            "grounding": grounding,
            "retrieval": retrieval,
        }
