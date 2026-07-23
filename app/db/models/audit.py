from datetime import UTC, datetime

from sqlmodel import JSON, Field, Relationship, SQLModel


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class AuditTrace(SQLModel, table=True):
    __tablename__ = "audit_traces"

    id: int | None = Field(default=None, primary_key=True)
    trace_id: str = Field(unique=True, index=True)
    organization_id: int | None = Field(default=None, foreign_key="organizations.id", index=True)
    workflow: str
    started_at: datetime = Field(default_factory=_utcnow)
    completed_at: datetime | None = None
    duration_ms: int | None = None
    outcome: str | None = None
    request_id: str | None = None
    api_key_id: str | None = None

    events: list["AuditEvent"] = Relationship(back_populates="trace")


class AuditEvent(SQLModel, table=True):
    __tablename__ = "audit_events"

    id: int | None = Field(default=None, primary_key=True)
    trace_id: str = Field(foreign_key="audit_traces.trace_id", index=True)
    event_type: str
    timestamp: datetime = Field(default_factory=_utcnow)
    data: dict = Field(default_factory=dict, sa_type=JSON)

    trace: AuditTrace = Relationship(back_populates="events")
