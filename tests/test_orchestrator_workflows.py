from unittest.mock import AsyncMock, MagicMock

import pytest

from app.ai.gateway.base import ModelResponse
from app.ai.orchestrator import ConversationOrchestrator

_RETRIEVAL_RESULT = {
    "citation_id": "c1",
    "text_content": "Medical evidence content for testing.",
    "score": 0.85,
    "source_name": "Test Source",
    "source_version": "1.0",
    "source_trust_tier": 1,
    "document_title": "Test Document",
    "section_path": None,
    "page_number": None,
    "generic_name": None,
    "chunk_type": "general",
}


@pytest.fixture
def mock_deps():
    retrieval = AsyncMock()
    retrieval.search.return_value = [_RETRIEVAL_RESULT]
    retrieval.registry = MagicMock()
    retrieval.registry.get_source_metadata_for_chunk.return_value = {
        "source_name": "Test Source", "source_version": "1.0",
    }
    prompt_mgr = MagicMock()
    prompt_mgr.build_medical_qa_prompt.return_value = ("system prompt", "user prompt")
    prompt_mgr.build_interaction_check_prompt.return_value = ("system prompt", "user prompt")
    prompt_mgr.build_drug_info_prompt.return_value = ("system prompt", "user prompt")
    prompt_mgr.build_symptom_guidance_prompt.return_value = ("system prompt", "user prompt")
    prompt_mgr.build_contraindication_check_prompt.return_value = ("system prompt", "user prompt")
    prompt_mgr.build_dosage_verify_prompt.return_value = ("system prompt", "user prompt")
    prompt_mgr.build_prescription_explain_prompt.return_value = ("system prompt", "user prompt")
    prompt_mgr.get_workflow_version.return_value = "1.0.0"
    model = AsyncMock()
    model.generate.return_value = ModelResponse(
        text="Test response.",
        provider="mock", model="mock-v1",
    )
    audit = MagicMock()
    return retrieval, prompt_mgr, model, audit


@pytest.fixture
def orch(mock_deps):
    retrieval, prompt_mgr, model, audit = mock_deps
    return ConversationOrchestrator(
        retrieval_service=retrieval,
        prompt_manager=prompt_mgr,
        model_provider=model,
        audit_writer=audit,
    )


class TestRunMedicalQA:
    async def test_success(self, orch, mock_deps):
        result = await orch.run_medical_qa(
            question="Can I take ibuprofen with stomach ulcers?",
            patient_age=45,
            known_conditions=["ulcer"],
            allergies=["penicillin"],
        )
        assert result.success is True
        assert result.workflow == "medical_qa"
        assert result.response_text == "Test response."
        assert len(result.citations) == 1
        assert result.structured_result is not None
        assert "medical_claims" in result.structured_result

    async def test_handles_emergency_pre_retrieval(self, mock_deps):
        retrieval, prompt_mgr, model, audit = mock_deps
        orch = ConversationOrchestrator(
            retrieval_service=retrieval,
            prompt_manager=prompt_mgr,
            model_provider=model,
            audit_writer=audit,
        )
        result = await orch.run_medical_qa(
            question="I have chest pain and difficulty breathing",
        )
        assert result.success is False
        assert result.workflow == "medical_qa"
        assert result.error_code == "emergency_escalation"

    async def test_handles_model_unavailable(self, mock_deps):
        retrieval, prompt_mgr, model, audit = mock_deps
        model.generate.return_value = None
        orch = ConversationOrchestrator(
            retrieval_service=retrieval,
            prompt_manager=prompt_mgr,
            model_provider=model,
            audit_writer=audit,
        )
        result = await orch.run_medical_qa(question="What is aspirin?")
        assert result.success is False
        assert result.error_code == "model_provider_unavailable"
        assert result.retryable is True

    async def test_includes_patient_context(self, orch, mock_deps):
        result = await orch.run_medical_qa(
            question="Is this safe?",
            patient_age=30,
            patient_sex="female",
            known_conditions=["asthma"],
            allergies=["sulfa"],
            current_medications=["albuterol"],
        )
        assert result.success is True

    async def test_with_conversation_state(self, orch, mock_deps):
        from app.ai.orchestrator.models import ConversationState
        state = ConversationState(conversation_id="conv-1")
        result = await orch.run_medical_qa(
            question="Follow up question",
            conversation_state=state,
            request_id="req-1",
        )
        assert result.success is True
        assert result.audit_metadata.get("trace_id") == "req-1"


class TestRunInteractionCheck:
    async def test_success(self, orch, mock_deps):
        result = await orch.run_interaction_check(
            medications=[{"name": "warfarin"}, {"name": "ibuprofen"}],
            patient_age=65,
        )
        assert result.success is True
        assert result.workflow == "interaction_check"

    async def test_single_medication(self, orch, mock_deps):
        result = await orch.run_interaction_check(
            medications=[{"name": "warfarin"}],
        )
        assert result.success is True

    async def test_with_doses(self, orch, mock_deps):
        result = await orch.run_interaction_check(
            medications=[{"name": "warfarin", "dose": "5mg"}, {"name": "ibuprofen", "dose": "400mg"}],
            patient_age=65,
            known_conditions=["afib"],
            current_medications=["metoprolol"],
        )
        assert result.success is True

    async def test_handles_safety_block(self, orch, mock_deps):
        result = await orch.run_interaction_check(
            medications=[{"name": "overdose"}, {"name": "emergency"}],
        )
        assert result.success is False

    async def test_handles_model_unavailable(self, mock_deps):
        retrieval, prompt_mgr, model, audit = mock_deps
        model.generate.return_value = None
        orch = ConversationOrchestrator(
            retrieval_service=retrieval,
            prompt_manager=prompt_mgr,
            model_provider=model,
            audit_writer=audit,
        )
        result = await orch.run_interaction_check(
            medications=[{"name": "a"}, {"name": "b"}],
        )
        assert result.success is False
        assert result.error_code == "model_provider_unavailable"

    async def test_with_request_id(self, orch, mock_deps):
        result = await orch.run_interaction_check(
            medications=[{"name": "x"}, {"name": "y"}],
            request_id="req-ic-1",
        )
        assert result.audit_metadata.get("trace_id") == "req-ic-1"


class TestRunDrugInfo:
    async def test_success(self, orch, mock_deps):
        result = await orch.run_drug_info(drug_name="Amoxicillin")
        assert result.success is True
        assert result.workflow == "drug_info"
        assert len(result.citations) == 1

    async def test_with_requested_sections(self, orch, mock_deps):
        result = await orch.run_drug_info(
            drug_name="Augmentin",
            requested_sections=["uses", "warnings"],
        )
        assert result.success is True

    async def test_handles_safety_block(self, orch, mock_deps):
        result = await orch.run_drug_info(drug_name="suicide pill")
        assert result.success is False

    async def test_handles_model_unavailable(self, mock_deps):
        retrieval, prompt_mgr, model, audit = mock_deps
        model.generate.return_value = None
        orch = ConversationOrchestrator(
            retrieval_service=retrieval,
            prompt_manager=prompt_mgr,
            model_provider=model,
            audit_writer=audit,
        )
        result = await orch.run_drug_info(drug_name="Test")
        assert result.success is False
        assert result.error_code == "model_provider_unavailable"

    async def test_with_request_id(self, orch, mock_deps):
        result = await orch.run_drug_info(drug_name="Test", request_id="req-di-1")
        assert result.audit_metadata.get("trace_id") == "req-di-1"


class TestRunSymptomGuidance:
    async def test_success(self, orch, mock_deps):
        result = await orch.run_symptom_guidance(
            symptoms="I have a headache and mild fever",
            patient_age=30,
        )
        assert result.success is True
        assert result.workflow == "symptom_guidance"
        assert result.structured_result.get("triage_level") == "non_urgent"

    async def test_emergency_escalation(self, mock_deps):
        retrieval, prompt_mgr, model, audit = mock_deps
        orch = ConversationOrchestrator(
            retrieval_service=retrieval,
            prompt_manager=prompt_mgr,
            model_provider=model,
            audit_writer=audit,
        )
        result = await orch.run_symptom_guidance(
            symptoms="I have chest pain and difficulty breathing",
            patient_age=55,
        )
        assert result.success is True
        assert result.structured_result.get("triage_level") == "emergency"
        assert result.safety_metadata.get("requires_escalation") is True

    async def test_handles_model_unavailable(self, mock_deps):
        retrieval, prompt_mgr, model, audit = mock_deps
        model.generate.return_value = None
        orch = ConversationOrchestrator(
            retrieval_service=retrieval,
            prompt_manager=prompt_mgr,
            model_provider=model,
            audit_writer=audit,
        )
        result = await orch.run_symptom_guidance(symptoms="Mild headache")
        assert result.success is False
        assert result.error_code == "model_provider_unavailable"

    async def test_with_patient_context(self, orch, mock_deps):
        result = await orch.run_symptom_guidance(
            symptoms="Stomach pain",
            patient_age=40,
            patient_sex="male",
            known_conditions=["diabetes"],
        )
        assert result.success is True

    async def test_with_request_id(self, orch, mock_deps):
        result = await orch.run_symptom_guidance(
            symptoms="Cough", request_id="req-sg-1",
        )
        assert result.audit_metadata.get("trace_id") == "req-sg-1"


class TestRunWorkflow:
    async def test_classifies_and_delegates_medical_qa(self, orch):
        result = await orch.run_workflow(
            message="is it safe to take this medication",
        )
        assert result.success is True
        assert result.workflow == "medical_qa"

    async def test_classifies_and_delegates_drug_info(self, orch):
        result = await orch.run_workflow(
            message="tell me about the drug amoxicillin",
        )
        assert result.success is True
        assert result.workflow == "drug_info"

    async def test_classifies_and_delegates_symptom_guidance(self, orch):
        result = await orch.run_workflow(
            message="I have a headache and fever",
        )
        assert result.success is True
        assert result.workflow == "symptom_guidance"

    async def test_classifies_and_delegates_interaction_check(self, orch):
        result = await orch.run_workflow(
            message="drug interaction warfarin ibuprofen",
        )
        assert result.success is True
        assert result.workflow == "interaction_check"

    async def test_classifies_and_delegates_contraindication_check(self, orch):
        result = await orch.run_workflow(
            message="contraindication for ibuprofen with stomach ulcer",
        )
        assert result.success is True
        assert result.workflow == "contraindication_check"

    async def test_classifies_and_delegates_dosage_verify(self, orch):
        result = await orch.run_workflow(
            message="is the dosage correct for amoxicillin",
        )
        assert result.success is True
        assert result.workflow == "dosage_verify"

    async def test_classifies_and_delegates_prescription_explain(self, orch):
        result = await orch.run_workflow(
            message="explain this prescription: Amoxicillin 500mg tid",
        )
        assert result.success is True
        assert result.workflow == "prescription_explain"

    async def test_emergency_intent(self, orch):
        result = await orch.run_workflow(
            message="I have chest pain and difficulty breathing",
        )
        assert result.success is True
        assert result.workflow == "emergency"
        assert result.structured_result.get("triage_level") == "emergency"

    async def test_unsupported_intent_returns_general_fallback(self, orch):
        result = await orch.run_workflow(
            message="What is the weather like today?",
        )
        assert result.success is False
        assert result.error_code == "unsupported_intent"

    async def test_passes_patient_context(self, orch):
        result = await orch.run_workflow(
            message="is it safe to take this medication",
            patient_context={
                "age": 45,
                "sex": "female",
                "known_conditions": ["asthma"],
                "allergies": ["penicillin"],
                "current_medications": ["albuterol"],
            },
        )
        assert result.success is True

    async def test_with_explicit_intent_skips_classification(self, orch):
        from app.ai.orchestrator.models import Intent
        result = await orch.run_workflow(
            message="Tell me about amoxicillin",
            intent=Intent.DRUG_INFO,
        )
        assert result.success is True
        assert result.workflow == "drug_info"

    async def test_with_request_id(self, orch):
        result = await orch.run_workflow(
            message="is it safe to take this medication",
            request_id="req-rw-1",
        )
        assert result.audit_metadata.get("trace_id") == "req-rw-1"

    async def test_doctor_assist_returns_placeholder(self, orch):
        result = await orch.run_workflow(
            message="doctor assist with medication review",
        )
        assert result.success is False
        assert result.error_code == "feature_not_implemented"

    async def test_pharmacy_assist_returns_placeholder(self, orch):
        result = await orch.run_workflow(
            message="pharmacy assist with drug explanation",
        )
        assert result.success is False
        assert result.error_code == "feature_not_implemented"

    async def test_reminders_returns_placeholder(self, orch):
        result = await orch.run_workflow(
            message="set a reminder for my medication",
        )
        assert result.success is False
        assert result.error_code == "feature_not_implemented"