import logging

from fastapi import APIRouter, Request

from app.ai.orchestrator import ConversationOrchestrator
from app.api.composer import ResponseComposer
from app.api.schemas.ai import (
    DrugInfoRequest,
    DrugInfoResponse,
    ErrorResponse,
    InteractionCheckRequest,
    InteractionCheckResponse,
    MedicalQARequest,
    MedicalQAResponse,
    SymptomGuidanceRequest,
    SymptomGuidanceResponse,
)

logger = logging.getLogger("zam-ai-core-api.ai-routes")
router = APIRouter()

composer = ResponseComposer()


def _orch(request: Request) -> ConversationOrchestrator:
    return request.app.state.orchestrator


@router.post(
    "/ai/medical-qa",
    response_model=MedicalQAResponse | ErrorResponse,
)
async def medical_qa(request: Request, body: MedicalQARequest) -> MedicalQAResponse | ErrorResponse:
    patient = body.input.patient_context
    result = await _orch(request).run_medical_qa(
        question=body.input.question,
        patient_age=patient.age,
        patient_sex=patient.sex,
        known_conditions=patient.known_conditions,
        allergies=patient.allergies,
        current_medications=patient.current_medications,
        request_id=body.request_id,
    )
    return composer.medical_qa(result, body)


@router.post(
    "/ai/interactions/check",
    response_model=InteractionCheckResponse | ErrorResponse,
)
async def interaction_check(
    request: Request, body: InteractionCheckRequest
) -> InteractionCheckResponse | ErrorResponse:
    patient = body.input.patient_context
    medications = [{"name": m.name, "dose": m.dose} for m in body.input.medications]
    result = await _orch(request).run_interaction_check(
        medications=medications,
        patient_age=patient.age,
        known_conditions=patient.known_conditions,
        current_medications=patient.current_medications,
        request_id=body.request_id,
    )
    return composer.interaction_check(result, body)


@router.post(
    "/ai/drug-info",
    response_model=DrugInfoResponse | ErrorResponse,
)
async def drug_info(request: Request, body: DrugInfoRequest) -> DrugInfoResponse | ErrorResponse:
    result = await _orch(request).run_drug_info(
        drug_name=body.input.drug_name,
        requested_sections=body.input.requested_sections,
        request_id=body.request_id,
    )
    return composer.drug_info(result, body)


@router.post(
    "/ai/symptom-guidance",
    response_model=SymptomGuidanceResponse | ErrorResponse,
)
async def symptom_guidance(request: Request, body: SymptomGuidanceRequest) -> SymptomGuidanceResponse | ErrorResponse:
    patient = body.input.patient_context
    result = await _orch(request).run_symptom_guidance(
        symptoms=body.input.symptoms,
        patient_age=patient.age,
        patient_sex=patient.sex,
        known_conditions=patient.known_conditions,
        request_id=body.request_id,
    )
    return composer.symptom_guidance(result, body)
