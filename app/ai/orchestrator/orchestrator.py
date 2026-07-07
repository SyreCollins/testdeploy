import logging
import uuid
from typing import Any

from app.ai.gateway.base import BaseModelProvider, ModelResponse
from app.ai.orchestrator.intent_classifier import IntentClassifier
from app.ai.orchestrator.models import ConversationState, Intent, WorkflowResult
from app.ai.prompts.manager import PromptManager
from app.ai.safety.base import RiskLevel, SafetyAction, SafetyContext, SafetyDecision
from app.ai.safety.engine import evaluate_safety
from app.ai.scoring.confidence import ConfidenceScorer
from app.rag.service import RetrievalService

logger = logging.getLogger("zam-ai-core-api.orchestrator")


class ConversationOrchestrator:
    def __init__(
        self,
        retrieval_service: RetrievalService,
        prompt_manager: PromptManager,
        model_provider: BaseModelProvider | None = None,
        settings: Any | None = None,
    ) -> None:
        self.retrieval = retrieval_service
        self.prompt_mgr = prompt_manager
        self._model_provider = model_provider
        self.settings = settings
        self.intent_classifier = IntentClassifier()
        self.scorer = ConfidenceScorer()

    @property
    def model_provider(self) -> BaseModelProvider:
        if self._model_provider is None:
            from app.ai.gateway.factory import get_model_provider
            from app.core.config import get_settings
            self._model_provider = get_model_provider(self.settings or get_settings())
        return self._model_provider

    def classify_intent(self, message: str) -> tuple[Intent, float]:
        return self.intent_classifier.classify(message)

    def _build_safety_context(
        self,
        query: str,
        workflow: str,
        patient_age: int | None = None,
        known_conditions: list[str] | None = None,
    ) -> SafetyContext:
        return SafetyContext(
            query=query,
            patient_age=patient_age,
            known_conditions=known_conditions or [],
            workflow=workflow,
        )

    def _check_safety_pre_retrieval(
        self, ctx: SafetyContext
    ) -> SafetyDecision | None:
        decision = evaluate_safety(ctx)
        if decision.action in (SafetyAction.ESCALATED, SafetyAction.REFUSED):
            return decision
        if decision.risk_level == RiskLevel.HIGH:
            return decision
        return None

    def _check_safety_post_retrieval(
        self, ctx: SafetyContext, results: list[dict]
    ) -> SafetyDecision:
        ctx.has_retrieved_evidence = len(results) > 0
        ctx.has_retrieval_failed = len(results) == 0
        return evaluate_safety(ctx)

    def _build_citations(self, results: list[dict]) -> list[dict]:
        return [
            {
                "citation_id": r["citation_id"],
                "text_content": r["text_content"],
                "score": r["score"],
                "source_name": r.get("source_name"),
                "source_version": r.get("source_version"),
                "source_trust_tier": r.get("source_trust_tier"),
                "document_title": r.get("document_title"),
                "section_path": r.get("section_path"),
                "page_number": r.get("page_number"),
            }
            for r in results
        ]

    def _build_evidence_for_prompt(self, citations: list[dict]) -> list[dict]:
        return [
            {
                "source_name": c["source_name"],
                "source_version": c["source_version"],
                "text_content": c["text_content"],
            }
            for c in citations
        ]

    def _build_patient_context_dict(
        self,
        age: int | None = None,
        sex: str | None = None,
        known_conditions: list[str] | None = None,
        allergies: list[str] | None = None,
        current_medications: list[str] | None = None,
    ) -> dict:
        return {
            "age": age,
            "sex": sex,
            "known_conditions": known_conditions or [],
            "allergies": allergies or [],
            "current_medications": current_medications or [],
        }

    async def _call_model(
        self,
        system_prompt: str,
        user_prompt: str | None,
        fallback_text: str,
        max_tokens: int = 1024,
        temperature: float = 0.3,
    ) -> ModelResponse | None:
        try:
            return await self.model_provider.generate(
                prompt=user_prompt or fallback_text,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        except Exception as e:
            logger.error(f"Model generation failed: {e}")
            return None

    def _safety_block_result(
        self,
        decision: SafetyDecision,
        workflow: str,
        req_id: str,
    ) -> WorkflowResult:
        action = decision.action.value
        if action == "escalated":
            return WorkflowResult(
                success=False,
                response_text=decision.message or "Please seek emergency medical care immediately.",
                workflow=workflow,
                error=decision.message,
                error_code="emergency_escalation",
                safety_metadata={
                    "risk_level": decision.risk_level.value,
                    "action": action,
                    "requires_escalation": True,
                },
            )
        return WorkflowResult(
            success=False,
            response_text=decision.message or "I cannot answer this request.",
            workflow=workflow,
            error=decision.message or "Request refused by safety policy.",
            error_code="unsafe_request" if action == "refused" else "retrieval_no_evidence",
            safety_metadata={
                "risk_level": decision.risk_level.value,
                "action": action,
            },
        )

    def _model_unavailable_result(self, workflow: str, req_id: str) -> WorkflowResult:
        return WorkflowResult(
            success=False,
            response_text="The AI model is currently unavailable. Please try again later.",
            workflow=workflow,
            error="The AI model is currently unavailable. Please try again later.",
            error_code="model_provider_unavailable",
            retryable=True,
        )

    async def run_medical_qa(
        self,
        question: str,
        patient_age: int | None = None,
        patient_sex: str | None = None,
        known_conditions: list[str] | None = None,
        allergies: list[str] | None = None,
        current_medications: list[str] | None = None,
        conversation_state: ConversationState | None = None,
        request_id: str | None = None,
    ) -> WorkflowResult:
        req_id = request_id or str(uuid.uuid4())

        safety_ctx = self._build_safety_context(
            query=question,
            workflow="medical_qa",
            patient_age=patient_age,
            known_conditions=known_conditions,
        )

        block = self._check_safety_pre_retrieval(safety_ctx)
        if block:
            return self._safety_block_result(block, "medical_qa", req_id)

        results = await self.retrieval.search(query=question, limit=10)

        post_decision = self._check_safety_post_retrieval(safety_ctx, results)
        if post_decision.action == SafetyAction.REFUSED:
            return self._safety_block_result(post_decision, "medical_qa", req_id)

        citations = self._build_citations(results)
        evidence = self._build_evidence_for_prompt(citations)
        patient_context = self._build_patient_context_dict(
            age=patient_age,
            sex=patient_sex,
            known_conditions=known_conditions,
            allergies=allergies,
            current_medications=current_medications,
        )

        system_prompt, user_prompt = self.prompt_mgr.build_medical_qa_prompt(
            question=question,
            evidence=evidence,
            patient_context=patient_context,
        )

        response = await self._call_model(system_prompt, user_prompt, question)
        if response is None:
            return self._model_unavailable_result("medical_qa", req_id)

        model_claims = [
            {
                "claim": c["text_content"][:200],
                "citation_ids": [c["citation_id"]],
            }
            for c in citations
        ]

        return WorkflowResult(
            success=True,
            response_text=response.text,
            workflow="medical_qa",
            citations=citations[:5],
            safety_metadata={
                "risk_level": post_decision.risk_level.value,
                "action": post_decision.action.value,
                "requires_escalation": post_decision.requires_escalation,
                "requires_human_review": post_decision.requires_human_review,
            },
            confidence_metadata=self.scorer.compute(citations, response.text),
            audit_metadata={
                "model_provider": response.provider,
                "model_version": response.model,
            },
            structured_result={
                "medical_claims": model_claims[:5],
                "missing_context": [],
                "follow_up_questions": [],
            },
        )

    async def run_symptom_guidance(
        self,
        symptoms: str,
        patient_age: int | None = None,
        patient_sex: str | None = None,
        known_conditions: list[str] | None = None,
        conversation_state: ConversationState | None = None,
        request_id: str | None = None,
    ) -> WorkflowResult:
        req_id = request_id or str(uuid.uuid4())

        safety_ctx = self._build_safety_context(
            query=symptoms,
            workflow="symptom_guidance",
            patient_age=patient_age,
            known_conditions=known_conditions,
        )

        block = self._check_safety_pre_retrieval(safety_ctx)
        if block and block.requires_escalation:
            triage_level = "emergency"
            return WorkflowResult(
                success=True,
                response_text=block.message or "Please seek emergency medical care immediately.",
                workflow="symptom_guidance",
                safety_metadata={
                    "risk_level": block.risk_level.value,
                    "action": block.action.value,
                    "requires_escalation": True,
                },
                structured_result={
                    "triage_level": triage_level,
                    "diagnosis_provided": False,
                },
            )

        patient_context = self._build_patient_context_dict(
            age=patient_age,
            sex=patient_sex,
            known_conditions=known_conditions,
        )

        system_prompt, user_prompt = self.prompt_mgr.build_symptom_guidance_prompt(
            symptoms=symptoms,
            patient_context=patient_context,
        )

        response = await self._call_model(system_prompt, user_prompt, symptoms)
        if response is None:
            return self._model_unavailable_result("symptom_guidance", req_id)

        return WorkflowResult(
            success=True,
            response_text=response.text,
            workflow="symptom_guidance",
            safety_metadata={
                "risk_level": block.risk_level.value if block else "low",
                "action": "answered",
            },
            audit_metadata={
                "model_provider": response.provider,
                "model_version": response.model,
            },
            structured_result={
                "triage_level": "non_urgent",
                "diagnosis_provided": False,
            },
        )

    async def run_drug_info(
        self,
        drug_name: str,
        requested_sections: list[str] | None = None,
        conversation_state: ConversationState | None = None,
        request_id: str | None = None,
    ) -> WorkflowResult:
        req_id = request_id or str(uuid.uuid4())

        safety_ctx = self._build_safety_context(
            query=drug_name,
            workflow="drug_info",
        )

        block = self._check_safety_pre_retrieval(safety_ctx)
        if block:
            return self._safety_block_result(block, "drug_info", req_id)

        results = await self.retrieval.search(
            query=drug_name,
            limit=10,
            chunk_type_filter=None,
        )

        citations = self._build_citations(results)
        evidence = [
            {**e, "chunk_type": c.get("chunk_type")}
            for e, c in zip(self._build_evidence_for_prompt(citations), citations, strict=False)
        ]

        system_prompt, user_prompt = self.prompt_mgr.build_drug_info_prompt(
            drug_name=drug_name,
            evidence=evidence,
            requested_sections=requested_sections,
        )

        response = await self._call_model(system_prompt, user_prompt, drug_name)
        if response is None:
            return self._model_unavailable_result("drug_info", req_id)

        return WorkflowResult(
            success=True,
            response_text=response.text,
            workflow="drug_info",
            citations=citations[:5],
            safety_metadata={"risk_level": "low", "action": "answered"},
            confidence_metadata=self.scorer.compute(citations, response.text),
            audit_metadata={
                "model_provider": response.provider,
                "model_version": response.model,
            },
            structured_result={
                "normalized_drug": {
                    "input_name": drug_name,
                },
                "sections": {"information": response.text},
            },
        )

    async def run_interaction_check(
        self,
        medications: list[dict],
        patient_age: int | None = None,
        known_conditions: list[str] | None = None,
        current_medications: list[str] | None = None,
        conversation_state: ConversationState | None = None,
        request_id: str | None = None,
    ) -> WorkflowResult:
        req_id = request_id or str(uuid.uuid4())
        drug_names = [m.get("name", "") for m in medications]

        safety_ctx = self._build_safety_context(
            query=" ".join(drug_names),
            workflow="interaction_check",
            patient_age=patient_age,
            known_conditions=known_conditions,
        )

        block = self._check_safety_pre_retrieval(safety_ctx)
        if block:
            return self._safety_block_result(block, "interaction_check", req_id)

        all_results = []
        for drug in drug_names:
            results = await self.retrieval.search(query=drug, limit=5)
            all_results.extend(results)

        citations = self._build_citations(all_results)
        evidence = self._build_evidence_for_prompt(citations)
        patient_context = self._build_patient_context_dict(
            age=patient_age,
            known_conditions=known_conditions,
            current_medications=current_medications,
        )

        system_prompt, user_prompt = self.prompt_mgr.build_interaction_check_prompt(
            medications=[
                {"name": m.get("name", ""), "dose": m.get("dose")}
                for m in medications
            ],
            evidence=evidence,
            patient_context=patient_context,
        )

        fallback = "Check interactions between: " + ", ".join(drug_names)
        response = await self._call_model(system_prompt, user_prompt, fallback)
        if response is None:
            return self._model_unavailable_result("interaction_check", req_id)

        return WorkflowResult(
            success=True,
            response_text=response.text,
            workflow="interaction_check",
            citations=citations[:5],
            safety_metadata={"risk_level": "medium", "action": "answered"},
            confidence_metadata=self.scorer.compute(citations, response.text),
            audit_metadata={
                "model_provider": response.provider,
                "model_version": response.model,
            },
            structured_result={
                "interactions": [
                    {
                        "medications": drug_names,
                        "severity": "unknown",
                        "summary": response.text,
                        "citation_ids": [c["citation_id"] for c in citations[:5]],
                    }
                ],
                "unknowns": [],
            },
        )

    async def run_workflow(
        self,
        message: str,
        intent: Intent | None = None,
        patient_context: dict | None = None,
        conversation_state: ConversationState | None = None,
        request_id: str | None = None,
    ) -> WorkflowResult:
        if intent is None or intent == Intent.UNKNOWN:
            intent, _ = self.classify_intent(message)

        patient = patient_context or {}

        if intent == Intent.MEDICAL_QA:
            return await self.run_medical_qa(
                question=message,
                patient_age=patient.get("age"),
                patient_sex=patient.get("sex"),
                known_conditions=patient.get("known_conditions"),
                allergies=patient.get("allergies"),
                current_medications=patient.get("current_medications"),
                conversation_state=conversation_state,
                request_id=request_id,
            )

        if intent == Intent.SYMPTOM_GUIDANCE:
            return await self.run_symptom_guidance(
                symptoms=message,
                patient_age=patient.get("age"),
                patient_sex=patient.get("sex"),
                known_conditions=patient.get("known_conditions"),
                conversation_state=conversation_state,
                request_id=request_id,
            )

        if intent == Intent.DRUG_INFO:
            return await self.run_drug_info(
                drug_name=message,
                conversation_state=conversation_state,
                request_id=request_id,
            )

        if intent == Intent.INTERACTION_CHECK:
            medications = patient.get("medications", [{"name": message}])
            return await self.run_interaction_check(
                medications=medications,
                patient_age=patient.get("age"),
                known_conditions=patient.get("known_conditions"),
                current_medications=patient.get("current_medications"),
                conversation_state=conversation_state,
                request_id=request_id,
            )

        if intent == Intent.EMERGENCY:
            return WorkflowResult(
                success=True,
                response_text="Please seek emergency medical care immediately.",
                workflow="emergency",
                safety_metadata={
                    "risk_level": "emergency",
                    "action": "escalated",
                    "requires_escalation": True,
                },
                structured_result={"triage_level": "emergency"},
            )

        return WorkflowResult(
            success=False,
            response_text="I can only answer medical questions about medications, symptoms, and health information.",
            workflow="general",
            error="Unsupported intent",
            error_code="unsupported_intent",
            safety_metadata={"risk_level": "low", "action": "refused"},
        )
