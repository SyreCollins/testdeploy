export interface AuditEventSummary {
  event_type: string;
  timestamp: string;
  data: Record<string, unknown>;
}

export interface AuditTraceInfo {
  trace_id: string;
  workflow: string;
  started_at: string;
  completed_at: string | null;
  event_count: number;
  events: AuditEventSummary[];
}

export interface ListAuditTracesResponse {
  traces: AuditTraceInfo[];
  total: number;
}

export interface GetAuditTraceResponse {
  trace: AuditTraceInfo;
}
