export enum Intent {
  MEDICAL_QA = "medical_qa",
  SYMPTOM_GUIDANCE = "symptom_guidance",
  DRUG_INFO = "drug_info",
  INTERACTION_CHECK = "interaction_check",
  CONTRAINDICATION_CHECK = "contraindication_check",
  DOSAGE_VERIFY = "dosage_verify",
  PRESCRIPTION_EXPLAIN = "prescription_explain",
  DOCTOR_ASSIST = "doctor_assist",
  PHARMACY_ASSIST = "pharmacy_assist",
  REMINDERS = "reminders",
  EMERGENCY = "emergency",
  GENERAL = "general",
  UNKNOWN = "unknown",
}

export interface Message {
  text: string;
  role: string;
  metadata: Record<string, unknown>;
}

export interface ConversationState {
  conversation_id: string;
  messages: Message[];
  metadata: Record<string, unknown>;
  current_intent: Intent | null;
}

export interface WorkflowResult {
  success: boolean;
  response_text: string;
  workflow: string;
  citations: Record<string, unknown>[];
  safety_metadata: Record<string, unknown>;
  confidence_metadata: Record<string, unknown>;
  audit_metadata: Record<string, unknown>;
  structured_result: Record<string, unknown> | null;
  error: string | null;
  error_code: string | null;
  retryable: boolean;
}
