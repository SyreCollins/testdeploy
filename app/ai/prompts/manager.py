import logging

from app.ai.prompts.builder import PromptBuilder
from app.ai.prompts.registry import PromptRegistry
from app.ai.toon import encode_toon

logger = logging.getLogger("zam-ai-core-api.prompt-manager")

SYSTEM_SECTIONS = [
    "base.system",
    "base.medical_rules",
    "base.safety_rules",
    "base.refusal_rules",
    "base.citation_rules",
    "base.output_rules",
]


class PromptManager:
    def __init__(self, registry: PromptRegistry | None = None) -> None:
        self._registry = registry or PromptRegistry()
        self._registry.load_all()

    def build_medical_qa_prompt(
        self,
        question: str,
        evidence: list[dict],
        patient_context: dict | None = None,
        safety_requirements: str = "Retrieved evidence must support every medical claim.",
    ) -> tuple[str, str | None]:
        builder = PromptBuilder(self._registry)

        for key in SYSTEM_SECTIONS:
            builder.add(key)

        builder.add(
            "workflows.patient.medication_info",
            question=question,
            evidence=evidence,
            patient_context=patient_context,
            safety_requirements=safety_requirements,
            evidence_toon=encode_toon(evidence),
            patient_context_toon=encode_toon(patient_context or {}),
        )

        return builder.build(), None

    def build_interaction_check_prompt(
        self,
        medications: list[dict],
        evidence: list[dict],
        patient_context: dict | None = None,
        safety_requirements: str = "Never invent interactions or severity. Only use retrieved evidence.",
    ) -> tuple[str, str | None]:
        builder = PromptBuilder(self._registry)

        for key in SYSTEM_SECTIONS:
            builder.add(key)

        builder.add(
            "workflows.patient.interaction_checker",
            medications=medications,
            evidence=evidence,
            patient_context=patient_context,
            safety_requirements=safety_requirements,
            medications_toon=encode_toon(medications),
            evidence_toon=encode_toon(evidence),
            patient_context_toon=encode_toon(patient_context or {}),
        )

        return builder.build(), None

    def build_drug_info_prompt(
        self,
        drug_name: str,
        evidence: list[dict],
        requested_sections: list[str] | None = None,
        safety_requirements: str = "Never invent drug information. Only use retrieved evidence.",
    ) -> tuple[str, str | None]:
        builder = PromptBuilder(self._registry)

        for key in SYSTEM_SECTIONS:
            builder.add(key)

        builder.add(
            "workflows.patient.drug_info",
            drug_name=drug_name,
            evidence=evidence,
            requested_sections=requested_sections or [],
            safety_requirements=safety_requirements,
            evidence_toon=encode_toon(evidence),
        )

        return builder.build(), None

    def build_symptom_guidance_prompt(
        self,
        symptoms: str,
        patient_context: dict | None = None,
        safety_requirements: str = "Emergency symptoms must be escalated immediately. Never diagnose.",
    ) -> tuple[str, str | None]:
        builder = PromptBuilder(self._registry)

        for key in SYSTEM_SECTIONS:
            builder.add(key)

        builder.add(
            "workflows.patient.symptom_checker",
            symptoms=symptoms,
            patient_context=patient_context,
            safety_requirements=safety_requirements,
            patient_context_toon=encode_toon(patient_context or {}),
        )

        return builder.build(), None

    def build_contraindication_check_prompt(
        self,
        medications: list[dict],
        evidence: list[dict],
        patient_context: dict | None = None,
        safety_requirements: str = "Never invent contraindications. Only use retrieved evidence.",
    ) -> tuple[str, str | None]:
        builder = PromptBuilder(self._registry)
        for key in SYSTEM_SECTIONS:
            builder.add(key)
        builder.add(
            "workflows.patient.contraindication_checker",
            medications=medications,
            evidence=evidence,
            patient_context=patient_context,
            safety_requirements=safety_requirements,
            medications_toon=encode_toon(medications),
            evidence_toon=encode_toon(evidence),
            patient_context_toon=encode_toon(patient_context or {}),
        )
        return builder.build(), None

    def build_dosage_verify_prompt(
        self,
        medication: dict,
        evidence: list[dict],
        patient_context: dict | None = None,
        safety_requirements: str = "Never invent dosage ranges. Only use retrieved evidence.",
    ) -> tuple[str, str | None]:
        builder = PromptBuilder(self._registry)
        for key in SYSTEM_SECTIONS:
            builder.add(key)
        builder.add(
            "workflows.patient.dosage_verifier",
            medication=medication,
            evidence=evidence,
            patient_context=patient_context,
            safety_requirements=safety_requirements,
            medication_toon=encode_toon(medication),
            evidence_toon=encode_toon(evidence),
            patient_context_toon=encode_toon(patient_context or {}),
        )
        return builder.build(), None

    def build_prescription_explain_prompt(
        self,
        prescription_text: str,
        evidence: list[dict],
        patient_context: dict | None = None,
        safety_requirements: str = "Never assume a diagnosis. Only use retrieved evidence for drug information.",
    ) -> tuple[str, str | None]:
        builder = PromptBuilder(self._registry)
        for key in SYSTEM_SECTIONS:
            builder.add(key)
        builder.add(
            "workflows.patient.prescription_explainer",
            prescription_text=prescription_text,
            evidence=evidence,
            patient_context=patient_context,
            safety_requirements=safety_requirements,
            evidence_toon=encode_toon(evidence),
            patient_context_toon=encode_toon(patient_context or {}),
        )
        return builder.build(), None

    def build_system_prompt(self) -> str | None:
        builder = PromptBuilder(self._registry)
        for key in SYSTEM_SECTIONS:
            builder.add(key)
        return builder.build()

    def get_workflow_version(self, workflow: str) -> str:
        template_key = _WORKFLOW_TEMPLATES.get(workflow)
        if template_key is None:
            return "0.0.0"
        try:
            template = self._registry.get(template_key)
            return template.version
        except KeyError:
            return "0.0.0"

    def list_templates(self) -> list[str]:
        return self._registry.list_templates()

    def reload(self) -> None:
        self._registry.reload()


_WORKFLOW_TEMPLATES: dict[str, str] = {
    "medical_qa": "workflows.patient.medication_info",
    "drug_info": "workflows.patient.drug_info",
    "interaction_check": "workflows.patient.interaction_checker",
    "symptom_guidance": "workflows.patient.symptom_checker",
    "contraindication_check": "workflows.patient.contraindication_checker",
    "dosage_verify": "workflows.patient.dosage_verifier",
    "prescription_explain": "workflows.patient.prescription_explainer",
}
