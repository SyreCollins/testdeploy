export const API_PREFIX = "/v1";

export const ENDPOINTS = {
  SYSTEM: {
    HEALTH: "/v1/health",
    READY: "/v1/ready",
  } as const,

  RETRIEVAL: {
    SEARCH: "/v1/retrieval/search",
  } as const,

  AI: {
    MEDICAL_QA: "/v1/ai/medical-qa",
    INTERACTIONS_CHECK: "/v1/ai/interactions/check",
    DRUG_INFO: "/v1/ai/drug-info",
    SYMPTOM_GUIDANCE: "/v1/ai/symptom-guidance",
    CONTRAINDICATIONS_CHECK: "/v1/ai/contraindications/check",
    DOSAGE_VERIFY: "/v1/ai/dosage/verify",
    PRESCRIPTIONS_EXPLAIN: "/v1/ai/prescriptions/explain",
    CHAT: "/v1/ai/chat",

    PRESCRIPTIONS_OCR_CREATE: "/v1/ai/prescriptions/ocr-jobs",
    PRESCRIPTIONS_OCR_POLL: "/v1/ai/prescriptions/ocr-jobs/{job_id}",
    REMINDERS_PARSE_SCHEDULE: "/v1/ai/reminders/parse-schedule",
    DOCTOR_ASSIST: "/v1/ai/doctor/assist",
    PHARMACY_ASSIST: "/v1/ai/pharmacy/assist",
  } as const,

  AUDIT: {
    TRACES: "/v1/audit/traces",
    TRACE: "/v1/audit/traces/{trace_id}",
  } as const,

  AUTH: {
    CLERK_WEBHOOK: "/v1/auth/webhook",
  } as const,

  ORGANIZATIONS: {
    ME: "/v1/organizations/me",
    USAGE: "/v1/organizations/me/usage",
    API_KEYS: "/v1/organizations/me/api-keys",
    API_KEY_ROTATE: "/v1/organizations/me/api-keys/{key_id}/rotate",
    API_KEY_REVOKE: "/v1/organizations/me/api-keys/{key_id}/revoke",
  } as const,

  PROJECTS: {
    LIST: "/v1/organizations/me/projects",
    CREATE: "/v1/organizations/me/projects",
    DETAIL: "/v1/organizations/me/projects/{project_id}",
    UPDATE: "/v1/organizations/me/projects/{project_id}",
    DELETE: "/v1/organizations/me/projects/{project_id}",
    API_KEYS: "/v1/organizations/me/projects/{project_id}/api-keys",
    API_KEY_ROTATE: "/v1/organizations/me/projects/{project_id}/api-keys/{key_id}/rotate",
    API_KEY_REVOKE: "/v1/organizations/me/projects/{project_id}/api-keys/{key_id}/revoke",
  } as const,

  ADMIN: {
    KEYS: "/v1/admin/keys",
    KEY_ROTATE: "/v1/admin/keys/{key_id}/rotate",
    KEY_REVOKE: "/v1/admin/keys/{key_id}/revoke",
    EVALUATIONS_RUN: "/v1/admin/evaluations/run",
  } as const,
} as const;

export function buildPath(
  path: string,
  params?: Record<string, string | number>,
): string {
  if (!params) return path;
  return Object.entries(params).reduce(
    (result, [key, value]) => result.replace(`{${key}}`, String(value)),
    path,
  );
}
