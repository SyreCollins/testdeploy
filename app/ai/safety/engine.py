import logging

from app.ai.safety.base import RiskLevel, SafetyAction, SafetyContext, SafetyDecision
from app.ai.safety.rules import (
    check_emergency,
    check_high_risk,
    check_retrieval_required,
    check_unsafe_request,
)

logger = logging.getLogger("zam-ai-core-api.safety-engine")

RULE_CHECKS = [
    check_emergency,
    check_unsafe_request,
    check_retrieval_required,
    check_high_risk,
]


def evaluate_safety(ctx: SafetyContext) -> SafetyDecision:
    for rule_fn in RULE_CHECKS:
        result = rule_fn(ctx)
        if result is not None:
            if result.action in (SafetyAction.ESCALATED, SafetyAction.REFUSED):
                logger.info(
                    f"Safety block: {result.triggered_rules} → {result.action.value}"
                )
                return result
            if result.risk_level == RiskLevel.HIGH:
                logger.info(
                    f"Safety flag: {result.triggered_rules} → {result.risk_level.value}"
                )
                return result
    return SafetyDecision(
        risk_level=RiskLevel.LOW,
        action=SafetyAction.ANSWERED,
        triggered_rules=[],
        message="",
    )
