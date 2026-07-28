// ──────────────────────────────────────────────
// Organization - Me
// ──────────────────────────────────────────────

export interface OrganizationInfo {
  id: string;
  name: string;
  slug: string;
  created_at: string;
  updated_at: string;
}

export interface OrganizationMeResponse {
  organization: OrganizationInfo;
}

// ──────────────────────────────────────────────
// Organization - Usage
// ──────────────────────────────────────────────

export interface UsageRecord {
  period_start: string;
  period_end: string;
  total_requests: number;
  total_tokens: number;
  cost: number;
}

export interface OrganizationUsageResponse {
  usage: UsageRecord[];
}