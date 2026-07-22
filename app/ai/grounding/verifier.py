import logging
import re

from app.ai.grounding.models import GroundingDetail, GroundingResult

logger = logging.getLogger("zam-ai-core-api.grounding-verifier")

_STOPWORDS = frozenset({
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "i", "you", "he", "she", "it",
    "we", "they", "this", "that", "these", "those", "of", "in", "on", "at",
    "by", "for", "with", "about", "to", "from", "and", "or", "but", "not",
    "no", "if", "so", "as", "than", "then", "also", "very", "just", "because",
    "some", "any", "all", "both", "each", "few", "more", "most", "other",
    "into", "over", "such", "only", "own", "same", "too", "please",
})

OVERLAP_THRESHOLD = 0.20
MIN_CLAIM_WORDS = 4


class GroundingVerifier:
    def verify(
        self,
        response_text: str,
        citations: list[dict],
    ) -> GroundingResult:
        claims = self._extract_claims(response_text)
        if not claims:
            return GroundingResult(score=0.0, grounded_claims=0, total_claims=0)

        evidence_texts = [c.get("text_content", "") for c in citations]

        grounded_count = 0
        details: list[GroundingDetail] = []

        for claim in claims:
            detail = self._check_claim(claim, evidence_texts)
            details.append(detail)
            if detail.is_grounded:
                grounded_count += 1

        score = round(grounded_count / len(claims), 4)
        return GroundingResult(
            score=score,
            grounded_claims=grounded_count,
            total_claims=len(claims),
            details=details,
        )

    def _extract_claims(self, text: str) -> list[str]:
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            return []
        raw = re.split(r"(?<=[.!?])\s+", text)
        return [
            s.strip()
            for s in raw
            if len(s.strip().split()) >= MIN_CLAIM_WORDS
        ]

    def _check_claim(
        self,
        claim: str,
        evidence_texts: list[str],
    ) -> GroundingDetail:
        claim_tokens = self._tokenize(claim)
        if not claim_tokens:
            return GroundingDetail(
                claim=claim, is_grounded=False, overlap_score=0.0
            )

        best_score = 0.0
        supporting: list[str] = []

        for ev in evidence_texts:
            ev_tokens = self._tokenize(ev)
            if not ev_tokens:
                continue
            overlap = claim_tokens & ev_tokens
            score = len(overlap) / len(claim_tokens)
            if score > best_score:
                best_score = score
                supporting = [ev] if score > 0 else []
            elif score == best_score and score > 0:
                supporting.append(ev)

        return GroundingDetail(
            claim=claim,
            is_grounded=best_score >= OVERLAP_THRESHOLD,
            overlap_score=round(best_score, 4),
            supporting_evidence=supporting[:3],
        )

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        words = re.findall(r"[a-zA-Z0-9]+", text.lower())
        unigrams = {t for t in words if t not in _STOPWORDS and len(t) > 1}
        bigrams = set()
        for i in range(len(words) - 1):
            if (
                words[i] not in _STOPWORDS
                and words[i + 1] not in _STOPWORDS
                and len(words[i]) > 1
                and len(words[i + 1]) > 1
            ):
                bigrams.add(f"{words[i]} {words[i + 1]}")
        return unigrams | bigrams
