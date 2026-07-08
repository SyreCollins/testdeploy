from typing import Any

from pydantic import BaseModel


class AuditEventSummary(BaseModel):
    event_type: str
    timestamp: str
    data: dict[str, Any]


class AuditTraceInfo(BaseModel):
    trace_id: str
    workflow: str
    started_at: str
    completed_at: str | None = None
    event_count: int
    events: list[AuditEventSummary] = []


class ListAuditTracesResponse(BaseModel):
    traces: list[AuditTraceInfo]
    total: int


class GetAuditTraceResponse(BaseModel):
    trace: AuditTraceInfo