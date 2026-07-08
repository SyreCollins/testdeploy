import pytest

from app.ai.orchestrator.models import WorkflowResult
from app.api.composer import ResponseComposer
from app.api.schemas.ai import (
    ActorContext,
    AuthorizationContext,
    CallerInfo,
    ContraindicationCheckInput,
    ContraindicationCheckRequest,
    ContraindicationMedication,
    DosageMedication,
    DosageVerifyInput,
    DosageVerifyRequest,
    Locale,
    PrescriptionExplainInput,
    PrescriptionExplainRequest,
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
def sr() -> WorkflowResult:
    return WorkflowResult(
        success=True,
        response_text="Test result.",
        workflow="test",
        citations=[{
            "citation_id": "c1", "text_content": "Evidence text.",
            "score": 0.85, "source_name": "Test Source",
            "source_version": "1.0", "source_trust_tier": 1,
        }],
        safety_metadata={"risk_level": "low", "action": "answered"},
        confidence_metadata={"overall": 0.8, "grounding": 0.0, "retrieval": 0.8},
        audit_metadata={"model_provider": "test", "model_version": "test-v1"},
    )


@pytest.fixture
def er() -> WorkflowResult:
    return WorkflowResult(
        success=False,
        response_text="Error message.",
        workflow="test",
        error="Something went wrong.",
        error_code="emergency_escalation",
        safety_metadata={
            "risk_level": "emergency", "action": "escalated",
            "requires_escalation": True,
        },
    )


class TestContraindicationCheckComposer:
    def test_success(
        self, composer: ResponseComposer, sr: WorkflowResult,
        actor: ActorContext, caller: CallerInfo,
    ) -> None:
        sr.workflow = "contraindication_check"
        sr.structured_result = {
            "contraindications": [{
                "medication": "ibuprofen",
                "condition": "peptic ulcer disease",
                "severity": "contraindicated",
                "reason": "Increased bleeding risk.",
                "citation_ids": ["c1"],
            }],
            "missing_context": [],
            "unknowns": [],
        }
        body = ContraindicationCheckRequest(
            request_id="req-1", caller=caller, actor_context=actor,
            authorization_context=AuthorizationContext(workflow="contraindication_check"),
            locale=Locale(),
            input=ContraindicationCheckInput(
                medications=[ContraindicationMedication(name="ibuprofen")],
            ),
        )
        response = composer.contraindication_check(sr, body)
        assert response.status == "success"
        assert response.workflow == "contraindication_check"
        assert response.result is not None
        assert len(response.result.contraindications) == 1
        assert response.result.contraindications[0].medication == "ibuprofen"
        assert response.result.contraindications[0].severity == "contraindicated"
        assert len(response.citations) == 1

    def test_error(
        self, composer: ResponseComposer, er: WorkflowResult,
        actor: ActorContext, caller: CallerInfo,
    ) -> None:
        er.workflow = "contraindication_check"
        body = ContraindicationCheckRequest(
            request_id="req-1", caller=caller, actor_context=actor,
            authorization_context=AuthorizationContext(workflow="contraindication_check"),
            locale=Locale(),
            input=ContraindicationCheckInput(
                medications=[ContraindicationMedication(name="ibuprofen")],
            ),
        )
        response = composer.contraindication_check(er, body)
        assert response.status == "error"

    def test_empty_contraindications(
        self, composer: ResponseComposer, sr: WorkflowResult,
        actor: ActorContext, caller: CallerInfo,
    ) -> None:
        sr.workflow = "contraindication_check"
        sr.structured_result = {
            "contraindications": [],
            "missing_context": ["weight"],
            "unknowns": [],
        }
        body = ContraindicationCheckRequest(
            request_id="req-1", caller=caller, actor_context=actor,
            authorization_context=AuthorizationContext(workflow="contraindication_check"),
            locale=Locale(),
            input=ContraindicationCheckInput(
                medications=[ContraindicationMedication(name="ibuprofen")],
            ),
        )
        response = composer.contraindication_check(sr, body)
        assert response.status == "success"
        assert response.result is not None
        assert len(response.result.contraindications) == 0
        assert "weight" in response.result.missing_context


class TestDosageVerifyComposer:
    def test_success(
        self, composer: ResponseComposer, sr: WorkflowResult,
        actor: ActorContext, caller: CallerInfo,
    ) -> None:
        sr.workflow = "dosage_verify"
        sr.structured_result = {
            "dosages": [{
                "medication_name": "amoxicillin",
                "stated_dosage": "500 mg three times daily",
                "assessment": "verified",
                "typical_range": "250-500 mg three times daily",
                "flags": [],
                "citation_ids": ["c1"],
            }],
            "missing_context": [],
        }
        body = DosageVerifyRequest(
            request_id="req-1", caller=caller, actor_context=actor,
            authorization_context=AuthorizationContext(workflow="dosage_verify"),
            locale=Locale(),
            input=DosageVerifyInput(
                medication=DosageMedication(name="amoxicillin", strength="500 mg"),
            ),
        )
        response = composer.dosage_verify(sr, body)
        assert response.status == "success"
        assert response.workflow == "dosage_verify"
        assert response.result is not None
        assert len(response.result.dosages) == 1
        assert response.result.dosages[0].assessment == "verified"

    def test_error(
        self, composer: ResponseComposer, er: WorkflowResult,
        actor: ActorContext, caller: CallerInfo,
    ) -> None:
        er.workflow = "dosage_verify"
        body = DosageVerifyRequest(
            request_id="req-1", caller=caller, actor_context=actor,
            authorization_context=AuthorizationContext(workflow="dosage_verify"),
            locale=Locale(),
            input=DosageVerifyInput(
                medication=DosageMedication(name="amoxicillin"),
            ),
        )
        response = composer.dosage_verify(er, body)
        assert response.status == "error"


class TestPrescriptionExplainComposer:
    def test_success(
        self, composer: ResponseComposer, sr: WorkflowResult,
        actor: ActorContext, caller: CallerInfo,
    ) -> None:
        sr.workflow = "prescription_explain"
        sr.structured_result = {
            "summary": "This prescription is for amoxicillin.",
            "sections": [{
                "title": "What it is for",
                "content": "Amoxicillin is an antibiotic.",
                "citation_ids": ["c1"],
            }],
            "warnings": ["Take with food."],
        }
        body = PrescriptionExplainRequest(
            request_id="req-1", caller=caller, actor_context=actor,
            authorization_context=AuthorizationContext(workflow="prescription_explain"),
            locale=Locale(),
            input=PrescriptionExplainInput(prescription_text="Amoxicillin 500mg"),
        )
        response = composer.prescription_explain(sr, body)
        assert response.status == "success"
        assert response.workflow == "prescription_explain"
        assert response.result is not None
        assert "amoxicillin" in response.result.summary.lower()
        assert len(response.result.sections) == 1
        assert len(response.result.warnings) == 1

    def test_error(
        self, composer: ResponseComposer, er: WorkflowResult,
        actor: ActorContext, caller: CallerInfo,
    ) -> None:
        er.workflow = "prescription_explain"
        body = PrescriptionExplainRequest(
            request_id="req-1", caller=caller, actor_context=actor,
            authorization_context=AuthorizationContext(workflow="prescription_explain"),
            locale=Locale(),
            input=PrescriptionExplainInput(prescription_text="Amoxicillin 500mg"),
        )
        response = composer.prescription_explain(er, body)
        assert response.status == "error"


class TestPromptTemplates:
    def test_contraindication_checker_template_loads(self) -> None:
        from app.ai.prompts.registry import PromptRegistry
        registry = PromptRegistry()
        registry.load_all()
        template = registry.get("workflows.patient.contraindication_checker")
        assert template is not None
        assert template.version == "1.0.0"

    def test_dosage_verifier_template_loads(self) -> None:
        from app.ai.prompts.registry import PromptRegistry
        registry = PromptRegistry()
        registry.load_all()
        template = registry.get("workflows.patient.dosage_verifier")
        assert template is not None
        assert template.version == "1.0.0"

    def test_prescription_explainer_template_loads(self) -> None:
        from app.ai.prompts.registry import PromptRegistry
        registry = PromptRegistry()
        registry.load_all()
        template = registry.get("workflows.patient.prescription_explainer")
        assert template is not None
        assert template.version == "1.0.0"

    def test_workflow_versions(self) -> None:
        from app.ai.prompts.manager import PromptManager
        mgr = PromptManager()
        assert mgr.get_workflow_version("contraindication_check") == "1.0.0"
        assert mgr.get_workflow_version("dosage_verify") == "1.0.0"
        assert mgr.get_workflow_version("prescription_explain") == "1.0.0"
