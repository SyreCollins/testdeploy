import logging

from app.ai.prompts.builder import PromptBuilder
from app.ai.prompts.registry import PromptRegistry

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
        )

        return builder.build(), None

    def build_system_prompt(self) -> str | None:
        builder = PromptBuilder(self._registry)
        for key in SYSTEM_SECTIONS:
            builder.add(key)
        return builder.build()

    def list_templates(self) -> list[str]:
        return self._registry.list_templates()

    def reload(self) -> None:
        self._registry.reload()
