from app.ai.orchestrator.models import WorkflowResult
from app.api.schemas.ai import (
    AuditMetadata,
    ChatResponse,
    ChatResult,
    CitationItem,
    ConfidenceMetadata,
    ContraindicationCheckRequest,
    ContraindicationCheckResponse,
    ContraindicationCheckResult,
    ContraindicationItem,
    DosageResult,
    DosageVerifyRequest,
    DosageVerifyResponse,
    DosageVerifyResult,
    DrugInfoRequest,
    DrugInfoResponse,
    DrugInfoResult,
    ErrorDetail,
    ErrorResponse,
    InteractionCheckRequest,
    InteractionCheckResponse,
    InteractionCheckResult,
    InteractionResult,
    MedicalClaim,
    MedicalQARequest,
    MedicalQAResponse,
    MedicalQAResult,
    NormalizedDrug,
    PrescriptionExplainRequest,
    PrescriptionExplainResponse,
    PrescriptionExplainResult,
    PrescriptionSection,
    SafetyMetadata,
    SymptomGuidanceRequest,
    SymptomGuidanceResponse,
    SymptomGuidanceResult,
)


class ResponseComposer:
    _ERROR_CODE_MAP: dict[str, str] = {
        "medical_qa": "retrieval_no_evidence",
        "interaction_check": "retrieval_no_evidence",
        "drug_info": "retrieval_no_evidence",
        "symptom_guidance": "retrieval_no_evidence",
        "contraindication_check": "retrieval_no_evidence",
        "dosage_verify": "retrieval_no_evidence",
        "prescription_explain": "retrieval_no_evidence",
    }

    @staticmethod
    def _error(result: WorkflowResult) -> ErrorResponse:
        return ErrorResponse(
            request_id=None,
            error=ErrorDetail(
                code=result.error_code or "unknown_error",
                message=result.error or "An error occurred.",
                retryable=result.retryable,
            ),
            safety=SafetyMetadata(
                risk_level=result.safety_metadata.get("risk_level", "low"),
                action=result.safety_metadata.get("action", "refused"),
                requires_escalation=result.safety_metadata.get("requires_escalation", False),
            ) if result.safety_metadata else None,
        )

    @staticmethod
    def _citations(result: WorkflowResult) -> list[CitationItem]:
        return [
            CitationItem(
                citation_id=c["citation_id"],
                text_content=c["text_content"],
                score=c["score"],
                source_name=c.get("source_name"),
                source_version=c.get("source_version"),
                source_trust_tier=c.get("source_trust_tier"),
                document_title=c.get("document_title"),
                section_path=c.get("section_path"),
                page_number=c.get("page_number"),
            )
            for c in result.citations
        ]

    @staticmethod
    def _confidence(result: WorkflowResult) -> ConfidenceMetadata:
        return ConfidenceMetadata(
            overall=result.confidence_metadata.get("overall", 0.0),
            grounding=result.confidence_metadata.get("grounding", 0.0),
            retrieval=result.confidence_metadata.get("retrieval", 0.0),
        )

    @staticmethod
    def _audit(result: WorkflowResult) -> AuditMetadata:
        return AuditMetadata(
            trace_id=result.audit_metadata.get("trace_id"),
            prompt_version=result.audit_metadata.get("prompt_version"),
            model_provider=result.audit_metadata.get("model_provider"),
            model_version=result.audit_metadata.get("model_version"),
        )

    @staticmethod
    def _safety(
        result: WorkflowResult,
        overrides: dict | None = None,
    ) -> SafetyMetadata:
        meta = {**result.safety_metadata, **(overrides or {})}
        return SafetyMetadata(
            risk_level=meta.get("risk_level", "low"),
            action=meta.get("action", "answered"),
            requires_escalation=meta.get("requires_escalation", False),
            requires_human_review=meta.get("requires_human_review", False),
        )

    def medical_qa(
        self,
        result: WorkflowResult,
        body: MedicalQARequest,
    ) -> MedicalQAResponse | ErrorResponse:
        if not result.success:
            return self._error(result)

        structured = result.structured_result or {}
        model_claims = [
            MedicalClaim(claim=m["claim"], citation_ids=m.get("citation_ids", []))
            for m in (structured.get("medical_claims") or [])
        ]

        return MedicalQAResponse(
            request_id=body.request_id,
            status="success",
            workflow="medical_qa",
            result=MedicalQAResult(
                answer=result.response_text,
                missing_context=structured.get("missing_context") or [],
                follow_up_questions=structured.get("follow_up_questions") or [],
                medical_claims=model_claims,
            ),
            safety=self._safety(result),
            citations=self._citations(result),
            confidence=self._confidence(result),
            audit=self._audit(result),
        )

    def interaction_check(
        self,
        result: WorkflowResult,
        body: InteractionCheckRequest,
    ) -> InteractionCheckResponse | ErrorResponse:
        if not result.success:
            return self._error(result)

        structured = result.structured_result or {}

        return InteractionCheckResponse(
            request_id=body.request_id,
            status="success",
            workflow="interaction_check",
            result=InteractionCheckResult(
                interactions=[
                    InteractionResult(
                        medications=ix.get("medications", []),
                        severity=ix.get("severity", "unknown"),
                        summary=ix.get("summary", ""),
                        citation_ids=ix.get("citation_ids", []),
                    )
                    for ix in (structured.get("interactions") or [])
                ],
                unknowns=structured.get("unknowns") or [],
            ),
            safety=self._safety(result, {"risk_level": "medium"}),
            citations=self._citations(result),
            confidence=self._confidence(result),
            audit=self._audit(result),
        )

    def drug_info(
        self,
        result: WorkflowResult,
        body: DrugInfoRequest,
    ) -> DrugInfoResponse | ErrorResponse:
        if not result.success:
            return self._error(result)

        structured = result.structured_result or {}

        return DrugInfoResponse(
            request_id=body.request_id,
            status="success",
            workflow="drug_info",
            result=DrugInfoResult(
                normalized_drug=NormalizedDrug(
                    input_name=(structured.get("normalized_drug") or {}).get(
                        "input_name", body.input.drug_name
                    ),
                ),
                sections=structured.get("sections") or {"information": result.response_text},
            ),
            safety=self._safety(result, {"risk_level": "low"}),
            citations=self._citations(result),
            confidence=self._confidence(result),
            audit=self._audit(result),
        )

    def symptom_guidance(
        self,
        result: WorkflowResult,
        body: SymptomGuidanceRequest,
    ) -> SymptomGuidanceResponse | ErrorResponse:
        if not result.success:
            return self._error(result)

        structured = result.structured_result or {}

        return SymptomGuidanceResponse(
            request_id=body.request_id,
            status="success",
            workflow="symptom_guidance",
            result=SymptomGuidanceResult(
                answer=result.response_text,
                triage_level=structured.get("triage_level", "non_urgent"),
                diagnosis_provided=structured.get("diagnosis_provided", False),
            ),
            safety=self._safety(result),
            citations=self._citations(result),
            confidence=self._confidence(result),
            audit=self._audit(result),
        )

    def contraindication_check(
        self,
        result: WorkflowResult,
        body: ContraindicationCheckRequest,
    ) -> ContraindicationCheckResponse | ErrorResponse:
        if not result.success:
            return self._error(result)

        structured = result.structured_result or {}

        return ContraindicationCheckResponse(
            request_id=body.request_id,
            status="success",
            workflow="contraindication_check",
            result=ContraindicationCheckResult(
                contraindications=[
                    ContraindicationItem(
                        medication=c.get("medication", ""),
                        condition=c.get("condition", ""),
                        severity=c.get("severity", "unknown"),
                        reason=c.get("reason", ""),
                        evidence_summary=c.get("evidence_summary"),
                        citation_ids=c.get("citation_ids", []),
                    )
                    for c in (structured.get("contraindications") or [])
                ],
                missing_context=structured.get("missing_context") or [],
                unknowns=structured.get("unknowns") or [],
            ),
            safety=self._safety(result, {"risk_level": "medium"}),
            citations=self._citations(result),
            confidence=self._confidence(result),
            audit=self._audit(result),
        )

    def dosage_verify(
        self,
        result: WorkflowResult,
        body: DosageVerifyRequest,
    ) -> DosageVerifyResponse | ErrorResponse:
        if not result.success:
            return self._error(result)

        structured = result.structured_result or {}

        return DosageVerifyResponse(
            request_id=body.request_id,
            status="success",
            workflow="dosage_verify",
            result=DosageVerifyResult(
                dosages=[
                    DosageResult(
                        medication_name=d.get("medication_name", ""),
                        stated_dosage=d.get("stated_dosage", ""),
                        assessment=d.get("assessment", "unknown"),
                        typical_range=d.get("typical_range"),
                        flags=d.get("flags", []),
                        citation_ids=d.get("citation_ids", []),
                    )
                    for d in (structured.get("dosages") or [])
                ],
                missing_context=structured.get("missing_context") or [],
            ),
            safety=self._safety(result, {"risk_level": "low"}),
            citations=self._citations(result),
            confidence=self._confidence(result),
            audit=self._audit(result),
        )

    def chat(
        self,
        result: WorkflowResult,
        request_id: str | None,
        intent: str,
        confidence: float,
    ) -> ChatResponse | ErrorResponse:
        if not result.success:
            return self._error(result)

        return ChatResponse(
            request_id=request_id,
            status="success",
            workflow="chat",
            result=ChatResult(
                intent=intent,
                confidence=confidence,
                answer=result.response_text,
            ),
            safety=self._safety(result),
            citations=self._citations(result),
            confidence=self._confidence(result),
            audit=self._audit(result),
        )

    def prescription_explain(
        self,
        result: WorkflowResult,
        body: PrescriptionExplainRequest,
    ) -> PrescriptionExplainResponse | ErrorResponse:
        if not result.success:
            return self._error(result)

        structured = result.structured_result or {}

        return PrescriptionExplainResponse(
            request_id=body.request_id,
            status="success",
            workflow="prescription_explain",
            result=PrescriptionExplainResult(
                summary=structured.get("summary", ""),
                sections=[
                    PrescriptionSection(
                        title=s.get("title", ""),
                        content=s.get("content", ""),
                        citation_ids=s.get("citation_ids", []),
                    )
                    for s in (structured.get("sections") or [])
                ],
                warnings=structured.get("warnings", []),
            ),
            safety=self._safety(result, {"risk_level": "low"}),
            citations=self._citations(result),
            confidence=self._confidence(result),
            audit=self._audit(result),
        )
