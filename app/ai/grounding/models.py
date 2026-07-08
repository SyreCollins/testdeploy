from dataclasses import dataclass, field


@dataclass
class GroundingDetail:
    claim: str
    is_grounded: bool
    overlap_score: float
    supporting_evidence: list[str] = field(default_factory=list)


@dataclass
class GroundingResult:
    score: float
    grounded_claims: int
    total_claims: int
    details: list[GroundingDetail] = field(default_factory=list)
