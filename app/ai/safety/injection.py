import re

from app.ai.safety.base import RiskLevel, SafetyAction, SafetyContext, SafetyDecision

INJECTION_PATTERNS: list[tuple[str, str]] = [
    (r"ignore\s+(all\s+)?(your\s+)?(previous|prior)\s+(instructions|directives|commands)", "ignore_instructions"),
    (r"forget\s+(all\s+)?(your\s+)?(previous|prior)\s+(instructions|directives|commands)", "forget_instructions"),
    (r"disregard\s+(all\s+)?(your\s+)?(previous|prior)\s+(instructions|directives|commands)", "disregard_instructions"),
    (r"you\s+(are\s+)?(now|are\s+now)\s+", "persona_switch"),
    (r"act\s+as\s+if", "persona_switch"),
    (r"from\s+now\s+on\s*,\s*you\s+are", "persona_switch"),
    (r"do\s+anything\s+now", "jailbreak_dan"),
    (r"you\s+have\s+no\s+(restrictions|limits|boundaries|constraints)", "jailbreak_norules"),
    (r"output\s+the\s+(system|initial)\s+prompt", "system_prompt_leak"),
    (r"repeat\s+(the\s+)?(words\s+)?(above|before|earlier|previous)", "prompt_leak"),
    (r"print\s+(your\s+)?(system\s+)?prompt", "system_prompt_leak"),
    (r"reveal\s+(your\s+)?(system\s+)?instructions", "system_prompt_leak"),
    (r"show\s+(me\s+)?(your\s+)?(system\s+)?prompt", "system_prompt_leak"),
    (r"</?(system|user|assistant|instruction)", "delimiter_injection"),
    (r"\[\/?system", "delimiter_injection"),
    (r"\{\/?system", "delimiter_injection"),
]


def check_prompt_injection(ctx: SafetyContext) -> SafetyDecision | None:
    query_lower = ctx.query.lower()
    triggered: list[str] = []
    for pattern, label in INJECTION_PATTERNS:
        if re.search(pattern, query_lower):
            triggered.append(f"injection_{label}")
    if triggered:
        return SafetyDecision(
            risk_level=RiskLevel.HIGH,
            action=SafetyAction.REFUSED,
            triggered_rules=triggered,
            message="Prompt injection attempt detected. Request blocked.",
        )
    return None
