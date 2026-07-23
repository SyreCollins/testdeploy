import logging
from datetime import UTC, datetime
from typing import Any

from sqlmodel import Session, select

from app.ai.audit.models import AuditEvent as AuditEventDTO
from app.ai.audit.models import AuditTrace as AuditTraceDTO
from app.db.engine import get_engine
from app.db.models.audit import AuditEvent as AuditEventModel
from app.db.models.audit import AuditTrace as AuditTraceModel

logger = logging.getLogger("zam-ai-core-api.audit-trace")


def _now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class AuditTraceWriter:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url
        self._engine = get_engine(database_url)

    def start_trace(
        self,
        trace_id: str,
        workflow: str,
        metadata: dict[str, Any] | None = None,
        organization_id: int | None = None,
    ) -> AuditTraceDTO:
        now = _now()
        with Session(self._engine) as session:
            trace = AuditTraceModel(
                trace_id=trace_id,
                organization_id=organization_id,
                workflow=workflow,
                started_at=now,
            )
            session.add(trace)

            event = AuditEventModel(
                trace_id=trace_id,
                event_type="trace_started",
                timestamp=now,
                data=metadata or {},
            )
            session.add(event)
            session.commit()

        return AuditTraceDTO(
            trace_id=trace_id,
            workflow=workflow,
            started_at=now.isoformat(),
            events=[AuditEventDTO(event_type="trace_started", timestamp=now.isoformat(), data=metadata or {})],
        )

    def record_event(
        self,
        trace_id: str,
        event_type: str,
        data: dict[str, Any] | None = None,
    ) -> AuditEventDTO | None:
        now = _now()
        with Session(self._engine) as session:
            trace = session.exec(
                select(AuditTraceModel).where(AuditTraceModel.trace_id == trace_id)
            ).first()
            if trace is None:
                logger.warning(f"No active trace for {trace_id}, creating ephemeral")
                trace = AuditTraceModel(
                    trace_id=trace_id,
                    workflow="unknown",
                    started_at=now,
                )
                session.add(trace)

            event = AuditEventModel(
                trace_id=trace_id,
                event_type=event_type,
                timestamp=now,
                data=data or {},
            )
            session.add(event)
            session.commit()

        return AuditEventDTO(event_type=event_type, timestamp=now.isoformat(), data=data or {})

    def end_trace(
        self,
        trace_id: str,
        summary: dict[str, Any] | None = None,
    ) -> None:
        now = _now()
        with Session(self._engine) as session:
            trace = session.exec(
                select(AuditTraceModel).where(AuditTraceModel.trace_id == trace_id)
            ).first()
            if trace is None:
                return

            started = trace.started_at
            duration_ms = int((now - started).total_seconds() * 1000) if started else None

            trace.completed_at = now
            trace.duration_ms = duration_ms
            if summary and "outcome" in summary:
                trace.outcome = summary["outcome"]

            event = AuditEventModel(
                trace_id=trace_id,
                event_type="trace_completed",
                timestamp=now,
                data=summary or {},
            )
            session.add(event)
            session.commit()

    def get_trace(self, trace_id: str) -> AuditTraceDTO | None:
        with Session(self._engine) as session:
            trace = session.exec(
                select(AuditTraceModel).where(AuditTraceModel.trace_id == trace_id)
            ).first()
            if trace is None:
                return None

            events = session.exec(
                select(AuditEventModel)
                .where(AuditEventModel.trace_id == trace_id)
                .order_by(AuditEventModel.id)
            ).all()

            return AuditTraceDTO(
                trace_id=trace.trace_id,
                workflow=trace.workflow,
                started_at=trace.started_at.isoformat() if trace.started_at else "",
                completed_at=trace.completed_at.isoformat() if trace.completed_at else None,
                events=[
                    AuditEventDTO(
                        event_type=e.event_type,
                        timestamp=e.timestamp.isoformat(),
                        data=e.data,
                    )
                    for e in events
                ],
            )

    def get_recent_traces(
        self,
        limit: int = 50,
        organization_id: int | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> list[AuditTraceDTO]:
        with Session(self._engine) as session:
            query = select(AuditTraceModel)

            if organization_id is not None:
                query = query.where(AuditTraceModel.organization_id == organization_id)
            if from_date:
                query = query.where(AuditTraceModel.started_at >= from_date)
            if to_date:
                query = query.where(AuditTraceModel.started_at <= to_date)

            query = query.order_by(AuditTraceModel.id.desc()).limit(limit)
            traces = session.exec(query).all()

            result: list[AuditTraceDTO] = []
            for t in traces:
                events = session.exec(
                    select(AuditEventModel)
                    .where(AuditEventModel.trace_id == t.trace_id)
                    .order_by(AuditEventModel.id)
                ).all()
                result.append(
                    AuditTraceDTO(
                        trace_id=t.trace_id,
                        workflow=t.workflow,
                        started_at=t.started_at.isoformat() if t.started_at else "",
                        completed_at=t.completed_at.isoformat() if t.completed_at else None,
                        events=[
                            AuditEventDTO(
                                event_type=e.event_type,
                                timestamp=e.timestamp.isoformat(),
                                data=e.data,
                            )
                            for e in events
                        ],
                    )
                )

            return result
