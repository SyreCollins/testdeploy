import logging

from fastapi import APIRouter, Request

from app.ai.orchestrator import ConversationOrchestrator
from app.api.composer import ResponseComposer
from app.api.schemas.ai import (
    ChatRequest,
    ChatResponse,
    ContraindicationCheckRequest,
    ContraindicationCheckResponse,
    DosageVerifyRequest,
    DosageVerifyResponse,
    DrugInfoRequest,
    DrugInfoResponse,
    ErrorResponse,
    InteractionCheckRequest,
    InteractionCheckResponse,
    MedicalQARequest,
    MedicalQAResponse,
    PrescriptionExplainRequest,
    PrescriptionExplainResponse,
    SymptomGuidanceRequest,
    SymptomGuidanceResponse,
)

logger = logging.getLogger("zam-ai-core-api.ai-routes")
router = APIRouter()

composer = ResponseComposer()


def _orch(request: Request) -> ConversationOrchestrator:
    return request.app.state.orchestrator


def _org_id(request: Request) -> int | None:
    return getattr(request.state, "org_id", None) or getattr(request.state, "organization_id", None)


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
        organization_id=_org_id(request),
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
        organization_id=_org_id(request),
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
        organization_id=_org_id(request),
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
        organization_id=_org_id(request),
    )
    return composer.symptom_guidance(result, body)


@router.post(
    "/ai/contraindications/check",
    response_model=ContraindicationCheckResponse | ErrorResponse,
)
async def contraindication_check(
    request: Request, body: ContraindicationCheckRequest
) -> ContraindicationCheckResponse | ErrorResponse:
    patient = body.input.patient_context
    medications = [{"name": m.name} for m in body.input.medications]
    result = await _orch(request).run_contraindication_check(
        medications=medications,
        patient_age=patient.age,
        known_conditions=patient.known_conditions,
        allergies=patient.allergies,
        current_medications=patient.current_medications,
        request_id=body.request_id,
        organization_id=_org_id(request),
    )
    return composer.contraindication_check(result, body)


@router.post(
    "/ai/dosage/verify",
    response_model=DosageVerifyResponse | ErrorResponse,
)
async def dosage_verify(
    request: Request, body: DosageVerifyRequest
) -> DosageVerifyResponse | ErrorResponse:
    patient = body.input.patient_context
    medication = {
        "name": body.input.medication.name,
        "strength": body.input.medication.strength,
        "instructions": body.input.medication.instructions,
    }
    result = await _orch(request).run_dosage_verify(
        medication=medication,
        patient_age=patient.age,
        known_conditions=patient.known_conditions,
        current_medications=patient.current_medications,
        request_id=body.request_id,
        organization_id=_org_id(request),
    )
    return composer.dosage_verify(result, body)


@router.post(
    "/ai/prescriptions/explain",
    response_model=PrescriptionExplainResponse | ErrorResponse,
)
async def prescription_explain(
    request: Request, body: PrescriptionExplainRequest
) -> PrescriptionExplainResponse | ErrorResponse:
    patient = body.input.patient_context
    result = await _orch(request).run_prescription_explain(
        prescription_text=body.input.prescription_text,
        patient_age=patient.age,
        known_conditions=patient.known_conditions,
        current_medications=patient.current_medications,
        request_id=body.request_id,
        organization_id=_org_id(request),
    )
    return composer.prescription_explain(result, body)


@router.post(
    "/ai/chat",
    response_model=ChatResponse | ErrorResponse,
)
async def chat(request: Request, body: ChatRequest) -> ChatResponse | ErrorResponse:
    orch = _orch(request)
    patient = body.input.patient_context
    intent, confidence = orch.classify_intent(body.input.message)
    result = await orch.run_workflow(
        message=body.input.message,
        intent=intent,
        patient_context={
            "age": patient.age,
            "sex": patient.sex,
            "known_conditions": patient.known_conditions,
            "allergies": patient.allergies,
            "current_medications": patient.current_medications,
        },
        request_id=body.request_id,
        organization_id=_org_id(request),
    )
    return composer.chat(result, body.request_id, intent.value, confidence)
