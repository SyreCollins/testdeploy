import re

from app.ai.safety.base import RiskLevel, SafetyAction, SafetyContext, SafetyDecision

EMERGENCY_KEYWORDS: list[str] = [
    "chest pain",
    "chest tightness",
    "difficulty breathing",
    "shortness of breath",
    "cannot breathe",
    "unconscious",
    "passing out",
    "fainted",
    "seizure",
    "convulsing",
    "stroke",
    "facial droop",
    "slurred speech",
    "severe bleeding",
    "uncontrollable bleeding",
    "poisoning",
    "overdose",
    "anaphylaxis",
    "swollen tongue",
    "throat closing",
    "head injury",
    "car accident",
    "suicide",
    "kill myself",
    "want to die",
    "self-harm",
    "hurting myself",
]

HIGH_RISK_PATTERNS: list[tuple[str, str]] = [
    (r"\bpregnant\b", "pregnancy"),
    (r"\bpregnancy\b", "pregnancy"),
    (r"\bbreastfeeding\b", "breastfeeding"),
    (r"\blactating\b", "breastfeeding"),
    (r"\b(?:child|infant|neonate|pediatric|baby)\b", "pediatric"),
    (r"\boverdose\b", "overdose"),
    (r"\ballergic reaction\b", "allergic_reaction"),
    (r"\banaphylaxis\b", "anaphylaxis"),
    (r"\b(?:cancer|chemotherapy|oncology)\b", "cancer"),
    (r"\bkidney disease\b", "renal_impairment"),
    (r"\bliver disease\b", "hepatic_impairment"),
]


def check_emergency(ctx: SafetyContext) -> SafetyDecision | None:
    query_lower = ctx.query.lower()
    for kw in EMERGENCY_KEYWORDS:
        if kw in query_lower:
            return SafetyDecision(
                risk_level=RiskLevel.EMERGENCY,
                action=SafetyAction.ESCALATED,
                requires_escalation=True,
                triggered_rules=["emergency_keyword_detected"],
                message="Emergency symptoms detected. Immediate escalation required.",
            )
    return None


def check_high_risk(ctx: SafetyContext) -> SafetyDecision | None:
    query_lower = ctx.query.lower()
    triggered: list[str] = []
    for pattern, label in HIGH_RISK_PATTERNS:
        if re.search(pattern, query_lower):
            triggered.append(f"high_risk_{label}")

    if ctx.pregnancy_status is True:
        triggered.append("high_risk_pregnancy_context")

    if ctx.patient_age is not None and ctx.patient_age < 2:
        triggered.append("high_risk_neonatal_context")

    if triggered:
        return SafetyDecision(
            risk_level=RiskLevel.HIGH,
            action=SafetyAction.ANSWERED,
            requires_escalation=True,
            requires_human_review=False,
            triggered_rules=triggered,
            message="High-risk context detected. Stricter retrieval and safer language required.",
        )
    return None


def check_retrieval_required(ctx: SafetyContext) -> SafetyDecision | None:
    if ctx.has_retrieval_failed:
        return SafetyDecision(
            risk_level=RiskLevel.HIGH,
            action=SafetyAction.REFUSED,
            triggered_rules=["retrieval_failed"],
            message="No reliable medical evidence was found for this request.",
        )
    return None


def check_unsafe_request(ctx: SafetyContext) -> SafetyDecision | None:
    query_lower = ctx.query.lower()
    unsafe_patterns = [
        r"how to (make|create|prepare) (a |an )?(drug|medicine|painkiller|medication)",
        r"where to buy illegal",
        r"how to get high",
        r"bypass.*prescription",
        r"fake.*prescription",
        r"sell.*(my |the )?prescription",
        r"abuse.*(drug|medication|prescription)",
    ]
    for pattern in unsafe_patterns:
        if re.search(pattern, query_lower):
            return SafetyDecision(
                risk_level=RiskLevel.HIGH,
                action=SafetyAction.REFUSED,
                triggered_rules=["unsafe_request"],
                message="I cannot provide instructions for unsafe or illegal medical activities.",
            )
    return None
