from pydantic import BaseModel, Field


class ActorContext(BaseModel):
    actor_type: str = Field(examples=["patient"])
    actor_id: str = Field(examples=["backend-user-ref"])
    organization_id: str | None = None
    role: str = Field(examples=["patient"])


class ConsentFlags(BaseModel):
    use_patient_context: bool = True
    store_ai_trace: bool = True


class AuthorizationContext(BaseModel):
    workflow: str = Field(examples=["medical_qa"])
    consent_flags: ConsentFlags = Field(default_factory=ConsentFlags)
    context_scope: list[str] = Field(default_factory=lambda: ["age", "allergies", "current_medications"])


class CallerInfo(BaseModel):
    service: str = Field(examples=["zamda-backend"])
    environment: str = Field(examples=["production"])


class Locale(BaseModel):
    language: str = "en"
    country: str = "NG"


class PatientContext(BaseModel):
    age: int | None = None
    sex: str | None = None
    known_conditions: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
    current_medications: list[str] = Field(default_factory=list)


class ConversationContext(BaseModel):
    conversation_id: str | None = None
    recent_messages: list[dict] = Field(default_factory=list)


class MedicalQAInput(BaseModel):
    question: str = Field(min_length=1, examples=["Can I take ibuprofen if I have stomach ulcers?"])
    patient_context: PatientContext = Field(default_factory=PatientContext)
    conversation_context: ConversationContext = Field(default_factory=ConversationContext)


class MedicalQARequest(BaseModel):
    request_id: str | None = None
    caller: CallerInfo = Field(default_factory=CallerInfo)
    actor_context: ActorContext
    authorization_context: AuthorizationContext = Field(default_factory=AuthorizationContext)
    locale: Locale = Field(default_factory=Locale)
    input: MedicalQAInput


class MedicalClaim(BaseModel):
    claim: str
    citation_ids: list[str] = Field(default_factory=list)


class MedicalQAResult(BaseModel):
    answer: str
    missing_context: list[str] = Field(default_factory=list)
    follow_up_questions: list[str] = Field(default_factory=list)
    medical_claims: list[MedicalClaim] = Field(default_factory=list)


class SafetyMetadata(BaseModel):
    risk_level: str = "low"
    action: str = "answered"
    requires_escalation: bool = False
    requires_human_review: bool = False


class ConfidenceMetadata(BaseModel):
    overall: float = 0.0
    grounding: float = 0.0
    retrieval: float = 0.0


class CitationItem(BaseModel):
    citation_id: str
    text_content: str
    score: float
    source_name: str | None = None
    source_version: str | None = None
    source_trust_tier: int | None = None
    document_title: str | None = None
    section_path: str | None = None
    page_number: int | None = None


class AuditMetadata(BaseModel):
    trace_id: str | None = None
    prompt_version: str | None = None
    model_provider: str | None = None
    model_version: str | None = None


class SymptomGuidanceInput(BaseModel):
    symptoms: str = Field(min_length=1, examples=["I have chest pain and shortness of breath"])
    patient_context: PatientContext = Field(default_factory=PatientContext)


class SymptomGuidanceRequest(BaseModel):
    request_id: str | None = None
    caller: CallerInfo = Field(default_factory=CallerInfo)
    actor_context: ActorContext
    authorization_context: AuthorizationContext = Field(default_factory=AuthorizationContext)
    locale: Locale = Field(default_factory=Locale)
    input: SymptomGuidanceInput


class InteractionMedication(BaseModel):
    name: str = Field(min_length=1, examples=["warfarin"])
    dose: str | None = None


class InteractionCheckInput(BaseModel):
    medications: list[InteractionMedication] = Field(min_length=2)
    patient_context: PatientContext = Field(default_factory=PatientContext)


class InteractionCheckRequest(BaseModel):
    request_id: str | None = None
    caller: CallerInfo = Field(default_factory=CallerInfo)
    actor_context: ActorContext
    authorization_context: AuthorizationContext = Field(default_factory=AuthorizationContext)
    locale: Locale = Field(default_factory=Locale)
    input: InteractionCheckInput


class InteractionResult(BaseModel):
    medications: list[str]
    severity: str
    summary: str
    recommended_action: str = "consult_clinician_or_pharmacist"
    citation_ids: list[str] = Field(default_factory=list)


class InteractionCheckResult(BaseModel):
    interactions: list[InteractionResult] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)


class InteractionCheckResponse(BaseModel):
    request_id: str | None = None
    status: str = "success"
    workflow: str = "interaction_check"
    result: InteractionCheckResult | None = None
    safety: SafetyMetadata = Field(default_factory=SafetyMetadata)
    citations: list[CitationItem] = Field(default_factory=list)
    confidence: ConfidenceMetadata = Field(default_factory=ConfidenceMetadata)
    audit: AuditMetadata = Field(default_factory=AuditMetadata)


class DrugInfoInput(BaseModel):
    drug_name: str = Field(min_length=1, examples=["Augmentin"])
    requested_sections: list[str] | None = Field(default=None, examples=[["uses", "warnings", "side_effects"]])
    country: str = "NG"


class DrugInfoRequest(BaseModel):
    request_id: str | None = None
    caller: CallerInfo = Field(default_factory=CallerInfo)
    actor_context: ActorContext
    authorization_context: AuthorizationContext = Field(default_factory=AuthorizationContext)
    locale: Locale = Field(default_factory=Locale)
    input: DrugInfoInput


class NormalizedDrug(BaseModel):
    input_name: str
    generic_name: str | None = None
    match_confidence: float = 0.0


class DrugInfoResult(BaseModel):
    normalized_drug: NormalizedDrug
    sections: dict[str, str] = Field(default_factory=dict)


class DrugInfoResponse(BaseModel):
    request_id: str | None = None
    status: str = "success"
    workflow: str = "drug_info"
    result: DrugInfoResult | None = None
    safety: SafetyMetadata = Field(default_factory=SafetyMetadata)
    citations: list[CitationItem] = Field(default_factory=list)
    confidence: ConfidenceMetadata = Field(default_factory=ConfidenceMetadata)
    audit: AuditMetadata = Field(default_factory=AuditMetadata)


class SymptomGuidanceResult(BaseModel):
    answer: str
    triage_level: str = "non_urgent"
    diagnosis_provided: bool = False


class SymptomGuidanceResponse(BaseModel):
    request_id: str | None = None
    status: str = "success"
    workflow: str = "symptom_guidance"
    result: SymptomGuidanceResult | None = None
    safety: SafetyMetadata = Field(default_factory=SafetyMetadata)
    audit: AuditMetadata = Field(default_factory=AuditMetadata)


class MedicalQAResponse(BaseModel):
    request_id: str | None = None
    status: str = "success"
    workflow: str = "medical_qa"
    result: MedicalQAResult | None = None
    safety: SafetyMetadata = Field(default_factory=SafetyMetadata)
    citations: list[CitationItem] = Field(default_factory=list)
    confidence: ConfidenceMetadata = Field(default_factory=ConfidenceMetadata)
    audit: AuditMetadata = Field(default_factory=AuditMetadata)


class ErrorDetail(BaseModel):
    code: str
    message: str
    retryable: bool = False
    details: dict | None = None


class ErrorResponse(BaseModel):
    request_id: str | None = None
    status: str = "error"
    error: ErrorDetail
    safety: SafetyMetadata | None = None
