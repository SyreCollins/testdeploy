export interface AuditEvent {
  event_type: string;
  timestamp: string;
  data: Record<string, unknown>;
}

export interface AuditTrace {
  trace_id: string;
  workflow: string;
  started_at: string;
  events: AuditEvent[];
  completed_at: string | null;
  addEvent(event_type: string, data?: Record<string, unknown>): AuditEvent;
  complete(): void;
}

export interface AuditTraceWriter {
  startTrace(trace_id: string, workflow: string, metadata: Record<string, unknown>): void;
  recordEvent(trace_id: string, event_type: string, data: Record<string, unknown>): void;
  endTrace(trace_id: string, summary: Record<string, unknown>): void;
  getTrace(trace_id: string): AuditTrace | null;
  getRecentTraces(limit: number): AuditTrace[];
}
