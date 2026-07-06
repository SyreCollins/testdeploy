from dataclasses import dataclass, field
from enum import StrEnum


class RiskLevel(StrEnum):
    EMERGENCY = "emergency"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SafetyAction(StrEnum):
    ANSWERED = "answered"
    REFUSED = "refused"
    ESCALATED = "escalated"
    CLARIFICATION = "clarification"


@dataclass
class SafetyDecision:
    risk_level: RiskLevel
    action: SafetyAction
    requires_escalation: bool = False
    requires_human_review: bool = False
    triggered_rules: list[str] = field(default_factory=list)
    message: str = ""


@dataclass
class SafetyContext:
    query: str
    patient_age: int | None = None
    pregnancy_status: bool | None = None
    known_conditions: list[str] = field(default_factory=list)
    has_retrieved_evidence: bool = False
    has_retrieval_failed: bool = False
    workflow: str = "medical_qa"
