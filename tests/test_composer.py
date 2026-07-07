import pytest

from app.ai.orchestrator.models import WorkflowResult
from app.api.composer import ResponseComposer
from app.api.schemas.ai import (
    ActorContext,
    AuthorizationContext,
    CallerInfo,
    DrugInfoInput,
    DrugInfoRequest,
    InteractionCheckInput,
    InteractionCheckRequest,
    InteractionMedication,
    Locale,
    MedicalQAInput,
    MedicalQARequest,
    SymptomGuidanceInput,
    SymptomGuidanceRequest,
)


@pytest.fixture
def composer() -> ResponseComposer:
    return ResponseComposer()


@pytest.fixture
def actor() -> ActorContext:
    return ActorContext(actor_type="patient", actor_id="test-1", role="patient")


@pytest.fixture
def caller() -> CallerInfo:
    return CallerInfo(service="test", environment="test")


@pytest.fixture
def success_result() -> WorkflowResult:
    return WorkflowResult(
        success=True,
        response_text="Test answer.",
        workflow="medical_qa",
        citations=[
            {
                "citation_id": "c1",
                "text_content": "Evidence text.",
                "score": 0.85,
                "source_name": "Test Source",
                "source_version": "1.0",
                "source_trust_tier": 1,
            }
        ],
        safety_metadata={"risk_level": "low", "action": "answered"},
        confidence_metadata={"overall": 0.8, "grounding": 0.0, "retrieval": 0.8},
        audit_metadata={"model_provider": "test", "model_version": "test-v1"},
        structured_result={
            "medical_claims": [{"claim": "Test claim.", "citation_ids": ["c1"]}],
        },
    )


@pytest.fixture
def error_result() -> WorkflowResult:
    return WorkflowResult(
        success=False,
        response_text="Error message.",
        workflow="medical_qa",
        error="Something went wrong.",
        error_code="emergency_escalation",
        safety_metadata={"risk_level": "emergency", "action": "escalated", "requires_escalation": True},
    )


class TestResponseComposer:
    def test_medical_qa_success(
        self, composer: ResponseComposer, success_result: WorkflowResult, actor: ActorContext, caller: CallerInfo
    ) -> None:
        auth = AuthorizationContext(workflow="medical_qa")
        body = MedicalQARequest(
            request_id="req-1",
            caller=caller,
            actor_context=actor,
            authorization_context=auth,
            locale=Locale(),
            input=MedicalQAInput(question="Test?"),
        )
        response = composer.medical_qa(success_result, body)
        assert response.status == "success"
        assert response.workflow == "medical_qa"
        assert response.result is not None
        assert response.result.answer == "Test answer."
        assert len(response.result.medical_claims) == 1
        assert len(response.citations) == 1
        assert response.confidence.retrieval == 0.8
        assert response.audit.model_provider == "test"

    def test_medical_qa_error(
        self, composer: ResponseComposer, error_result: WorkflowResult, actor: ActorContext, caller: CallerInfo
    ) -> None:
        auth = AuthorizationContext(workflow="medical_qa")
        body = MedicalQARequest(
            request_id="req-1",
            caller=caller,
            actor_context=actor,
            authorization_context=auth,
            locale=Locale(),
            input=MedicalQAInput(question="Test?"),
        )
        response = composer.medical_qa(error_result, body)
        assert response.status == "error"
        assert response.error.code == "emergency_escalation"
        assert response.safety is not None
        assert response.safety.risk_level == "emergency"
        assert response.safety.requires_escalation

    def test_drug_info_success(
        self, composer: ResponseComposer, actor: ActorContext, caller: CallerInfo
    ) -> None:
        result = WorkflowResult(
            success=True,
            response_text="Drug info.",
            workflow="drug_info",
            citations=[],
            safety_metadata={"risk_level": "low", "action": "answered"},
            confidence_metadata={"retrieval": 0.7},
            audit_metadata={"model_provider": "test"},
            structured_result={
                "normalized_drug": {"input_name": "Augmentin"},
                "sections": {"uses": "For infections."},
            },
        )
        auth = AuthorizationContext(workflow="drug_info")
        body = DrugInfoRequest(
            request_id="req-2",
            caller=caller,
            actor_context=actor,
            authorization_context=auth,
            locale=Locale(),
            input=DrugInfoInput(drug_name="Augmentin"),
        )
        response = composer.drug_info(result, body)
        assert response.status == "success"
        assert response.result is not None
        assert response.result.normalized_drug.input_name == "Augmentin"
        assert response.result.sections["uses"] == "For infections."

    def test_interaction_check_success(
        self, composer: ResponseComposer, actor: ActorContext, caller: CallerInfo
    ) -> None:
        result = WorkflowResult(
            success=True,
            response_text="Interaction info.",
            workflow="interaction_check",
            citations=[],
            safety_metadata={"risk_level": "medium", "action": "answered"},
            confidence_metadata={"retrieval": 0.6},
            audit_metadata={"model_provider": "test"},
            structured_result={
                "interactions": [
                    {
                        "medications": ["warfarin", "ibuprofen"],
                        "severity": "moderate",
                        "summary": "Increased bleeding risk.",
                        "citation_ids": ["c1"],
                    }
                ],
                "unknowns": [],
            },
        )
        auth = AuthorizationContext(workflow="interaction_check")
        body = InteractionCheckRequest(
            request_id="req-3",
            caller=caller,
            actor_context=actor,
            authorization_context=auth,
            locale=Locale(),
            input=InteractionCheckInput(
                medications=[
                    InteractionMedication(name="warfarin"),
                    InteractionMedication(name="ibuprofen"),
                ]
            ),
        )
        response = composer.interaction_check(result, body)
        assert response.status == "success"
        assert response.result is not None
        assert len(response.result.interactions) == 1
        assert response.result.interactions[0].severity == "moderate"

    def test_symptom_guidance_success(
        self, composer: ResponseComposer, actor: ActorContext, caller: CallerInfo
    ) -> None:
        result = WorkflowResult(
            success=True,
            response_text="Rest and hydrate.",
            workflow="symptom_guidance",
            citations=[],
            safety_metadata={"risk_level": "low", "action": "answered"},
            confidence_metadata={},
            audit_metadata={"model_provider": "test"},
            structured_result={"triage_level": "non_urgent", "diagnosis_provided": False},
        )
        auth = AuthorizationContext(workflow="symptom_guidance")
        body = SymptomGuidanceRequest(
            request_id="req-4",
            caller=caller,
            actor_context=actor,
            authorization_context=auth,
            locale=Locale(),
            input=SymptomGuidanceInput(symptoms="Headache"),
        )
        response = composer.symptom_guidance(result, body)
        assert response.status == "success"
        assert response.result is not None
        assert response.result.answer == "Rest and hydrate."
        assert response.result.triage_level == "non_urgent"
