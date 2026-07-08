import json
import logging
from collections import OrderedDict
from datetime import UTC, datetime
from typing import Any

from app.ai.audit.models import AuditEvent, AuditTrace

logger = logging.getLogger("zam-ai-core-api.audit-trace")

_MAX_TRACES = 1000


class AuditTraceWriter:
    def __init__(self, max_traces: int = _MAX_TRACES) -> None:
        self._trace_log = logging.getLogger("zam-ai-core-api.audit-trace")
        self._traces: OrderedDict[str, AuditTrace] = OrderedDict()
        self._max_traces = max_traces

    def start_trace(
        self,
        trace_id: str,
        workflow: str,
        metadata: dict[str, Any] | None = None,
    ) -> AuditTrace:
        trace = AuditTrace(
            trace_id=trace_id,
            workflow=workflow,
            started_at=datetime.now(UTC).isoformat(),
        )
        trace.add_event("trace_started", metadata)
        self._traces[trace_id] = trace
        if len(self._traces) > self._max_traces:
            self._traces.popitem(last=False)

        self._emit(trace_id, "trace_started", metadata)
        return trace

    def record_event(
        self,
        trace_id: str,
        event_type: str,
        data: dict[str, Any] | None = None,
    ) -> AuditEvent | None:
        trace = self._traces.get(trace_id)
        if trace is None:
            logger.warning(f"No active trace for {trace_id}, creating ephemeral")
            trace = AuditTrace(
                trace_id=trace_id,
                workflow="unknown",
                started_at=datetime.now(UTC).isoformat(),
            )
        event = trace.add_event(event_type, data)
        self._emit(trace_id, event_type, data)
        return event

    def end_trace(
        self,
        trace_id: str,
        summary: dict[str, Any] | None = None,
    ) -> None:
        trace = self._traces.get(trace_id)
        if trace is None:
            return
        trace.complete()
        trace.add_event("trace_completed", summary)
        self._emit(trace_id, "trace_completed", summary)

    def get_trace(self, trace_id: str) -> AuditTrace | None:
        return self._traces.get(trace_id)

    def get_recent_traces(self, limit: int = 50) -> list[AuditTrace]:
        return list(self._traces.values())[-limit:]

    def _emit(
        self,
        trace_id: str,
        event_type: str,
        data: dict[str, Any] | None = None,
    ) -> None:
        self._trace_log.info(
            "audit_event",
            extra={
                "_trace_id": trace_id,
                "_event_type": event_type,
                "_data": json.dumps(data, default=str) if data else None,
            },
        )
