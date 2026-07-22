export interface ErrorDetail {
  code: string;
  message: string;
  retryable: boolean;
  details: Record<string, unknown> | null;
}

export interface ApiErrorResponse {
  request_id: string | null;
  status: "error";
  error: ErrorDetail;
  safety?: SafetyMetadata | null;
}

export interface SafetyMetadata {
  risk_level: string;
  action: string;
  requires_escalation: boolean;
  requires_human_review: boolean;
}
