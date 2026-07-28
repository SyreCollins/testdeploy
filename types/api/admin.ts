// ──────────────────────────────────────────────
// Admin - Keys
// ──────────────────────────────────────────────

export interface AdminApiKeyInfo {
  id: string;
  label: string;
  prefix: string;
  organization_id: string | null;
  created_at: string;
  expires_at: string | null;
  is_active: boolean;
  last_used_at: string | null;
}

export interface ListAdminKeysResponse {
  keys: AdminApiKeyInfo[];
}

export interface RotateAdminKeyResponse {
  id: string;
  new_key: string;
}

export interface RevokeAdminKeyResponse {
  id: string;
  revoked: boolean;
}

// ──────────────────────────────────────────────
// Admin - Evaluations
// ──────────────────────────────────────────────

export interface RunEvaluationResponse {
  run_id: string;
  status: string;
  started_at: string;
}

// ──────────────────────────────────────────────
// Admin - Organizations
// ──────────────────────────────────────────────

export interface AdminOrganizationInfo {
  id: string;
  name: string;
  slug: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
  user_count: number;
  project_count: number;
}

export interface ListAdminOrganizationsResponse {
  organizations: AdminOrganizationInfo[];
  total: number;
}

export interface AdminOrganizationDetailResponse {
  organization: AdminOrganizationInfo;
}

export interface AdminOrgUserInfo {
  id: string;
  email: string;
  name: string | null;
  role: string;
  joined_at: string;
}

export interface ListAdminOrgUsersResponse {
  users: AdminOrgUserInfo[];
  total: number;
}

export interface AdminOrgProjectInfo {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  is_active: boolean;
}

export interface ListAdminOrgProjectsResponse {
  projects: AdminOrgProjectInfo[];
  total: number;
}

// ──────────────────────────────────────────────
// Admin - Users
// ──────────────────────────────────────────────

export interface AdminUserInfo {
  id: string;
  email: string;
  name: string | null;
  organization_id: string | null;
  organization_name: string | null;
  role: string;
  created_at: string;
  is_active: boolean;
}

export interface ListAdminUsersResponse {
  users: AdminUserInfo[];
  total: number;
}

// ──────────────────────────────────────────────
// Admin - Audit
// ──────────────────────────────────────────────

export interface AdminAuditEventSummary {
  event_type: string;
  timestamp: string;
  data: Record<string, unknown>;
  organization_id: string | null;
  actor_id: string | null;
}

export interface AdminAuditTraceInfo {
  trace_id: string;
  workflow: string;
  organization_id: string | null;
  started_at: string;
  completed_at: string | null;
  event_count: number;
  events: AdminAuditEventSummary[];
}

export interface ListAdminAuditTracesResponse {
  traces: AdminAuditTraceInfo[];
  total: number;
}

export interface GetAdminAuditTraceResponse {
  trace: AdminAuditTraceInfo;
}

// ──────────────────────────────────────────────
// Admin - Usage
// ──────────────────────────────────────────────

export interface AdminUsageRecord {
  organization_id: string;
  organization_name: string;
  period_start: string;
  period_end: string;
  total_requests: number;
  total_tokens: number;
  cost: number;
}

export interface AdminUsageResponse {
  usage: AdminUsageRecord[];
}