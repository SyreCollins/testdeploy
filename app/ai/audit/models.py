from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class AuditEvent:
    event_type: str
    timestamp: str
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditTrace:
    trace_id: str
    workflow: str
    started_at: str
    events: list[AuditEvent] = field(default_factory=list)
    completed_at: str | None = None

    def add_event(self, event_type: str, data: dict[str, Any] | None = None) -> AuditEvent:
        event = AuditEvent(
            event_type=event_type,
            timestamp=datetime.now(UTC).isoformat(),
            data=data or {},
        )
        self.events.append(event)
        return event

    def complete(self) -> None:
        self.completed_at = datetime.now(UTC).isoformat()
