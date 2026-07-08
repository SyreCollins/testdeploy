import logging

from fastapi import APIRouter, HTTPException, Request
from starlette import status

from app.api.schemas.audit import (
    AuditEventSummary,
    AuditTraceInfo,
    GetAuditTraceResponse,
    ListAuditTracesResponse,
)

logger = logging.getLogger("zam-ai-core-api.audit-routes")
router = APIRouter()


@router.get(
    "/audit/traces",
    response_model=ListAuditTracesResponse,
)
def list_traces(request: Request, limit: int = 50) -> ListAuditTracesResponse:
    writer = request.app.state.audit_writer
    traces = writer.get_recent_traces(limit)
    return ListAuditTracesResponse(
        traces=[
            AuditTraceInfo(
                trace_id=t.trace_id,
                workflow=t.workflow,
                started_at=t.started_at,
                completed_at=t.completed_at,
                event_count=len(t.events),
                events=[
                    AuditEventSummary(
                        event_type=e.event_type,
                        timestamp=e.timestamp,
                        data=e.data,
                    )
                    for e in t.events
                ],
            )
            for t in traces
        ],
        total=len(traces),
    )


@router.get(
    "/audit/traces/{trace_id}",
    response_model=GetAuditTraceResponse,
)
def get_trace(request: Request, trace_id: str) -> GetAuditTraceResponse:
    writer = request.app.state.audit_writer
    trace = writer.get_trace(trace_id)
    if trace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trace not found")
    return GetAuditTraceResponse(
        trace=AuditTraceInfo(
            trace_id=trace.trace_id,
            workflow=trace.workflow,
            started_at=trace.started_at,
            completed_at=trace.completed_at,
            event_count=len(trace.events),
            events=[
                AuditEventSummary(
                    event_type=e.event_type,
                    timestamp=e.timestamp,
                    data=e.data,
                )
                for e in trace.events
            ],
        )
    )