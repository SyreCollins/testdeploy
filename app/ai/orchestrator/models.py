from dataclasses import dataclass, field
from enum import StrEnum


class Intent(StrEnum):
    MEDICAL_QA = "medical_qa"
    SYMPTOM_GUIDANCE = "symptom_guidance"
    DRUG_INFO = "drug_info"
    INTERACTION_CHECK = "interaction_check"
    EMERGENCY = "emergency"
    GENERAL = "general"
    UNKNOWN = "unknown"


@dataclass
class Message:
    text: str
    role: str = "user"
    metadata: dict = field(default_factory=dict)


@dataclass
class ConversationState:
    conversation_id: str
    messages: list[Message] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    current_intent: Intent | None = None


@dataclass
class WorkflowResult:
    success: bool
    response_text: str
    workflow: str
    citations: list[dict] = field(default_factory=list)
    safety_metadata: dict = field(default_factory=dict)
    confidence_metadata: dict = field(default_factory=dict)
    audit_metadata: dict = field(default_factory=dict)
    structured_result: dict | None = None
    error: str | None = None
    error_code: str | None = None
    retryable: bool = False
