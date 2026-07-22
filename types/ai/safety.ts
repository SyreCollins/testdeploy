export enum RiskLevel {
  EMERGENCY = "emergency",
  HIGH = "high",
  MEDIUM = "medium",
  LOW = "low",
}

export enum SafetyAction {
  ANSWERED = "answered",
  REFUSED = "refused",
  ESCALATED = "escalated",
  CLARIFICATION = "clarification",
}

export interface SafetyDecision {
  risk_level: RiskLevel;
  action: SafetyAction;
  requires_escalation: boolean;
  requires_human_review: boolean;
  triggered_rules: string[];
  message: string;
}

export interface SafetyContext {
  query: string;
  patient_age: number | null;
  pregnancy_status: boolean | null;
  known_conditions: string[];
  has_retrieved_evidence: boolean;
  has_retrieval_failed: boolean;
  workflow: string;
}
