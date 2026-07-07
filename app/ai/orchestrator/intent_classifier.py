import logging
import re

from app.ai.orchestrator.models import Intent

logger = logging.getLogger("zam-ai-core-api.intent-classifier")


class IntentClassifier:
    PATTERNS: dict[Intent, list[str]] = {
        Intent.EMERGENCY: [
            r"\b(emergency|chest pain|difficulty breathing|unconscious|heart attack|stroke|suicide|overdose)\b",
            r"\b(severe bleeding|head injury|poisoning|seizure|choking|not breathing)\b",
        ],
        Intent.INTERACTION_CHECK: [
            r"\b(interact|interaction|combine|mixing?)\b.*\b(drug|medication|medicine|prescription)",
            r"\btake\b.*\b(and|with)\b.*\b(together|same time|concurrently)\b",
            r"\bdrug interaction\b",
        ],
        Intent.DRUG_INFO: [
            r"\b(tell me about|what is|information on|details about)\b"
            r".*\b(drug|medication|medicine|tablet|antibiotic|painkiller|injection)\b",
            r"\bdrug (info|information|details|monograph)\b",
            r"\b(side effects?|dosage|uses?|warnings?|indications?)\b.*\b(of|for)\b",
        ],
        Intent.SYMPTOM_GUIDANCE: [
            r"\b(symptom|feel(ing)?|pain|ache|hurt(s|ing)?|sick|nausea|fever|cough|headache|dizzy|vomit)\b",
            r"\b(i have|i'm feeling|i feel)\b.*\b(pain|ache|symptom|problem|issue|discomfort|sick|nausea)\b",
        ],
        Intent.MEDICAL_QA: [
            r"\b(what|how|why|when|can|could|should|would|does|is|are)\b.*\b(medication|medicine|drug|treatment|condition|disease|health|prescription|therapy)\b",
            r"\b(is it safe|are there|do i need|should i take|could this be)\b",
        ],
    }

    # Weights to resolve conflicts when multiple patterns match
    PRIORITY: dict[Intent, float] = {
        Intent.EMERGENCY: 1.0,
        Intent.INTERACTION_CHECK: 0.9,
        Intent.DRUG_INFO: 0.85,
        Intent.SYMPTOM_GUIDANCE: 0.8,
        Intent.MEDICAL_QA: 0.7,
        Intent.GENERAL: 0.3,
        Intent.UNKNOWN: 0.0,
    }

    def classify(self, message: str) -> tuple[Intent, float]:
        if not message or not message.strip():
            return Intent.UNKNOWN, 0.0

        message_lower = message.lower().strip()

        best_intent = Intent.UNKNOWN
        best_score = 0.0

        for intent, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    score = self.PRIORITY.get(intent, 0.5)
                    if score > best_score:
                        best_score = score
                        best_intent = intent

        if best_intent == Intent.UNKNOWN:
            best_intent = Intent.GENERAL
            best_score = 0.3

        logger.debug(f"Classified intent={best_intent.value} score={best_score:.2f} for message={message[:60]!r}")
        return best_intent, best_score
