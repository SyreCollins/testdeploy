import logging
import uuid

from fastapi import APIRouter, Request

from app.ai.gateway import get_model_provider
from app.ai.prompts import PromptManager
from app.ai.safety import SafetyContext, evaluate_safety
from app.api.schemas.ai import (
    CitationItem,
    ConfidenceMetadata,
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
    SafetyMetadata,
    SymptomGuidanceRequest,
    SymptomGuidanceResponse,
    SymptomGuidanceResult,
)
from app.rag.service import RetrievalService

logger = logging.getLogger("zam-ai-core-api.ai-routes")
router = APIRouter()


@router.post(
    "/ai/medical-qa",
    response_model=MedicalQAResponse | ErrorResponse,
)
async def medical_qa(request: Request, body: MedicalQARequest) -> MedicalQAResponse | ErrorResponse:
    req_id = body.request_id or str(uuid.uuid4())
    settings = request.app.state.settings

    svc: RetrievalService = request.app.state.retrieval_service
    prompt_mgr: PromptManager = request.app.state.prompt_manager
    model_provider = get_model_provider(settings)

    patient = body.input.patient_context

    safety_ctx = SafetyContext(
        query=body.input.question,
        patient_age=patient.age,
        pregnancy_status=None,
        known_conditions=patient.known_conditions,
        workflow="medical_qa",
    )

    decision = evaluate_safety(safety_ctx)

    if decision.requires_escalation:
        return ErrorResponse(
            request_id=req_id,
            error=ErrorDetail(
                code="emergency_escalation",
                message=decision.message or "Emergency symptoms detected. Please seek immediate medical attention.",
                retryable=False,
            ),
            safety=SafetyMetadata(
                risk_level=decision.risk_level.value,
                action=decision.action.value,
                requires_escalation=True,
            ),
        )

    if decision.action.value == "refused":
        return ErrorResponse(
            request_id=req_id,
            error=ErrorDetail(
                code="unsafe_request",
                message=decision.message or "I cannot answer this request.",
                retryable=False,
            ),
            safety=SafetyMetadata(
                risk_level="high",
                action="refused",
            ),
        )

    results = svc.search(
        query=body.input.question,
        limit=10,
    )

    safety_ctx.has_retrieved_evidence = len(results) > 0
    safety_ctx.has_retrieval_failed = len(results) == 0
    decision = evaluate_safety(safety_ctx)

    if decision.action.value == "refused":
        return ErrorResponse(
            request_id=req_id,
            error=ErrorDetail(
                code="retrieval_no_evidence",
                message="No reliable medical evidence was found for this request.",
                retryable=False,
            ),
            safety=SafetyMetadata(
                risk_level="high",
                action="refused",
            ),
        )

    citations = [
        CitationItem(
            citation_id=r["citation_id"],
            text_content=r["text_content"],
            score=r["score"],
            source_name=r["source_name"],
            source_version=r.get("source_version"),
            source_trust_tier=r.get("source_trust_tier"),
            document_title=r.get("document_title"),
            section_path=r.get("section_path"),
            page_number=r.get("page_number"),
        )
        for r in results
    ]

    evidence_for_prompt = [
        {
            "source_name": c.source_name,
            "source_version": c.source_version,
            "text_content": c.text_content,
        }
        for c in citations
    ]

    patient_context = {
        "age": patient.age,
        "sex": patient.sex,
        "known_conditions": patient.known_conditions,
        "allergies": patient.allergies,
        "current_medications": patient.current_medications,
    }

    system_prompt, user_prompt = prompt_mgr.build_medical_qa_prompt(
        question=body.input.question,
        evidence=evidence_for_prompt,
        patient_context=patient_context,
    )

    try:
        response = await model_provider.generate(
            prompt=user_prompt or body.input.question,
            system_prompt=system_prompt,
            max_tokens=1024,
            temperature=0.3,
        )
    except Exception as e:
        logger.error(f"Model generation failed: {e}")
        return ErrorResponse(
            request_id=req_id,
            error=ErrorDetail(
                code="model_provider_unavailable",
                message="The AI model is currently unavailable. Please try again later.",
                retryable=True,
            ),
        )

    model_claims = []
    for c in citations:
        model_claims.append(
            MedicalClaim(
                claim=c.text_content[:200],
                citation_ids=[c.citation_id],
            )
        )

    return MedicalQAResponse(
        request_id=req_id,
        status="success",
        workflow="medical_qa",
        result=MedicalQAResult(
            answer=response.text,
            missing_context=[],
            follow_up_questions=[],
            medical_claims=model_claims[:5],
        ),
        safety=SafetyMetadata(
            risk_level=decision.risk_level.value,
            action=decision.action.value,
            requires_escalation=decision.requires_escalation,
            requires_human_review=decision.requires_human_review,
        ),
        citations=citations[:5],
        confidence=ConfidenceMetadata(
            overall=0.0,
            grounding=0.0,
            retrieval=round(sum(c.score for c in citations[:5]) / max(len(citations[:5]), 1), 4) if citations else 0.0,
        ),
        audit={
            "model_provider": response.provider,
            "model_version": response.model,
        },
    )


@router.post(
    "/ai/interactions/check",
    response_model=InteractionCheckResponse | ErrorResponse,
)
async def interaction_check(
    request: Request, body: InteractionCheckRequest
) -> InteractionCheckResponse | ErrorResponse:
    req_id = body.request_id or str(uuid.uuid4())
    settings = request.app.state.settings

    svc: RetrievalService = request.app.state.retrieval_service
    prompt_mgr: PromptManager = request.app.state.prompt_manager
    model_provider = get_model_provider(settings)

    patient = body.input.patient_context
    drug_names = [m.name for m in body.input.medications]

    safety_ctx = SafetyContext(
        query=" ".join(drug_names),
        patient_age=patient.age,
        known_conditions=patient.known_conditions,
        workflow="interaction_check",
    )

    decision = evaluate_safety(safety_ctx)

    if decision.action.value == "refused":
        return ErrorResponse(
            request_id=req_id,
            error=ErrorDetail(
                code="unsafe_request",
                message=decision.message or "I cannot answer this request.",
                retryable=False,
            ),
            safety=SafetyMetadata(risk_level="high", action="refused"),
        )

    all_results = []
    for drug in drug_names:
        results = svc.search(query=drug, limit=5)
        all_results.extend(results)

    citations = [
        CitationItem(
            citation_id=r["citation_id"],
            text_content=r["text_content"],
            score=r["score"],
            source_name=r["source_name"],
            source_version=r.get("source_version"),
            source_trust_tier=r.get("source_trust_tier"),
        )
        for r in all_results
    ]

    evidence_for_prompt = [
        {
            "source_name": c.source_name,
            "source_version": c.source_version,
            "text_content": c.text_content,
        }
        for c in citations
    ]

    patient_context = {
        "age": patient.age,
        "known_conditions": patient.known_conditions,
        "current_medications": patient.current_medications,
    }

    system_prompt, user_prompt = prompt_mgr.build_interaction_check_prompt(
        medications=[{"name": m.name, "dose": m.dose} for m in body.input.medications],
        evidence=evidence_for_prompt,
        patient_context=patient_context,
    )

    try:
        response = await model_provider.generate(
            prompt=user_prompt or "Check interactions between: " + ", ".join(drug_names),
            system_prompt=system_prompt,
            max_tokens=1024,
            temperature=0.3,
        )
    except Exception as e:
        logger.error(f"Model generation failed: {e}")
        return ErrorResponse(
            request_id=req_id,
            error=ErrorDetail(
                code="model_provider_unavailable",
                message="The AI model is currently unavailable. Please try again later.",
                retryable=True,
            ),
        )

    return InteractionCheckResponse(
        request_id=req_id,
        status="success",
        workflow="interaction_check",
        result=InteractionCheckResult(
            interactions=[
                InteractionResult(
                    medications=drug_names,
                    severity="unknown",
                    summary=response.text,
                    citation_ids=[c.citation_id for c in citations[:5]],
                )
            ],
            unknowns=[],
        ),
        safety=SafetyMetadata(risk_level="medium", action="answered"),
        citations=citations[:5],
        confidence=ConfidenceMetadata(
            retrieval=round(sum(c.score for c in citations[:5]) / max(len(citations[:5]), 1), 4) if citations else 0.0,
        ),
        audit={
            "model_provider": response.provider,
            "model_version": response.model,
        },
    )


@router.post(
    "/ai/drug-info",
    response_model=DrugInfoResponse | ErrorResponse,
)
async def drug_info(request: Request, body: DrugInfoRequest) -> DrugInfoResponse | ErrorResponse:
    req_id = body.request_id or str(uuid.uuid4())
    settings = request.app.state.settings

    svc: RetrievalService = request.app.state.retrieval_service
    prompt_mgr: PromptManager = request.app.state.prompt_manager
    model_provider = get_model_provider(settings)

    safety_ctx = SafetyContext(
        query=body.input.drug_name,
        workflow="drug_info",
    )

    decision = evaluate_safety(safety_ctx)

    if decision.action.value == "refused":
        return ErrorResponse(
            request_id=req_id,
            error=ErrorDetail(
                code="unsafe_request",
                message=decision.message or "I cannot answer this request.",
                retryable=False,
            ),
            safety=SafetyMetadata(risk_level="high", action="refused"),
        )

    results = svc.search(
        query=body.input.drug_name,
        limit=10,
        chunk_type_filter=None,
    )

    citations = [
        CitationItem(
            citation_id=r["citation_id"],
            text_content=r["text_content"],
            score=r["score"],
            source_name=r["source_name"],
            source_version=r.get("source_version"),
            source_trust_tier=r.get("source_trust_tier"),
            document_title=r.get("document_title"),
            section_path=r.get("section_path"),
            page_number=r.get("page_number"),
        )
        for r in results
    ]

    evidence_for_prompt = [
        {
            "source_name": c.source_name,
            "source_version": c.source_version,
            "text_content": c.text_content,
            "chunk_type": getattr(c, "chunk_type", None),
        }
        for c in citations
    ]

    system_prompt, user_prompt = prompt_mgr.build_drug_info_prompt(
        drug_name=body.input.drug_name,
        evidence=evidence_for_prompt,
        requested_sections=body.input.requested_sections,
    )

    try:
        response = await model_provider.generate(
            prompt=user_prompt or body.input.drug_name,
            system_prompt=system_prompt,
            max_tokens=1024,
            temperature=0.3,
        )
    except Exception as e:
        logger.error(f"Model generation failed: {e}")
        return ErrorResponse(
            request_id=req_id,
            error=ErrorDetail(
                code="model_provider_unavailable",
                message="The AI model is currently unavailable. Please try again later.",
                retryable=True,
            ),
        )

    return DrugInfoResponse(
        request_id=req_id,
        status="success",
        workflow="drug_info",
        result=DrugInfoResult(
            normalized_drug=NormalizedDrug(
                input_name=body.input.drug_name,
            ),
            sections={"information": response.text},
        ),
        safety=SafetyMetadata(risk_level="low", action="answered"),
        citations=citations[:5],
        confidence=ConfidenceMetadata(
            retrieval=round(sum(c.score for c in citations[:5]) / max(len(citations[:5]), 1), 4) if citations else 0.0,
        ),
        audit={
            "model_provider": response.provider,
            "model_version": response.model,
        },
    )


@router.post(
    "/ai/symptom-guidance",
    response_model=SymptomGuidanceResponse | ErrorResponse,
)
async def symptom_guidance(request: Request, body: SymptomGuidanceRequest) -> SymptomGuidanceResponse | ErrorResponse:
    req_id = body.request_id or str(uuid.uuid4())
    settings = request.app.state.settings

    prompt_mgr: PromptManager = request.app.state.prompt_manager
    model_provider = get_model_provider(settings)

    patient = body.input.patient_context
    symptoms = body.input.symptoms

    safety_ctx = SafetyContext(
        query=symptoms,
        patient_age=patient.age,
        pregnancy_status=None,
        known_conditions=patient.known_conditions,
        workflow="symptom_guidance",
    )

    decision = evaluate_safety(safety_ctx)

    if decision.requires_escalation:
        return SymptomGuidanceResponse(
            request_id=req_id,
            status="success",
            workflow="symptom_guidance",
            result=SymptomGuidanceResult(
                answer=decision.message or "Please seek emergency medical care immediately.",
                triage_level="emergency",
                diagnosis_provided=False,
            ),
            safety=SafetyMetadata(
                risk_level=decision.risk_level.value,
                action=decision.action.value,
                requires_escalation=True,
            ),
        )

    patient_context = {
        "age": patient.age,
        "sex": patient.sex,
        "known_conditions": patient.known_conditions,
    }

    system_prompt, user_prompt = prompt_mgr.build_symptom_guidance_prompt(
        symptoms=symptoms,
        patient_context=patient_context,
    )

    try:
        response = await model_provider.generate(
            prompt=user_prompt or symptoms,
            system_prompt=system_prompt,
            max_tokens=1024,
            temperature=0.3,
        )
    except Exception as e:
        logger.error(f"Model generation failed: {e}")
        return ErrorResponse(
            request_id=req_id,
            error=ErrorDetail(
                code="model_provider_unavailable",
                message="The AI model is currently unavailable. Please try again later.",
                retryable=True,
            ),
        )

    return SymptomGuidanceResponse(
        request_id=req_id,
        status="success",
        workflow="symptom_guidance",
        result=SymptomGuidanceResult(
            answer=response.text,
            triage_level="non_urgent",
            diagnosis_provided=False,
        ),
        safety=SafetyMetadata(
            risk_level=decision.risk_level.value,
            action=decision.action.value,
        ),
        audit={
            "model_provider": response.provider,
            "model_version": response.model,
        },
    )
