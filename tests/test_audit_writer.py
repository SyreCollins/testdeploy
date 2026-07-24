import uuid

import pytest

from app.ai.audit import AuditTrace, AuditTraceWriter
from app.db.engine import init_db, reset_engine

TEST_DB_URL = "sqlite://"


def _uid() -> str:
    return uuid.uuid4().hex[:12]


@pytest.fixture(autouse=True)
def _db():
    reset_engine()
    init_db(TEST_DB_URL)
    yield
    reset_engine()


@pytest.fixture
def writer() -> AuditTraceWriter:
    return AuditTraceWriter(database_url=TEST_DB_URL)


class TestAuditTrace:
    def test_add_event(self) -> None:
        trace = AuditTrace(trace_id="t1", workflow="test", started_at="now")
        event = trace.add_event("model_call", {"provider": "test"})
        assert event.event_type == "model_call"
        assert event.data["provider"] == "test"
        assert len(trace.events) == 1

    def test_complete(self) -> None:
        trace = AuditTrace(trace_id="t2", workflow="test", started_at="now")
        assert trace.completed_at is None
        trace.complete()
        assert trace.completed_at is not None


class TestAuditTraceWriter:
    def test_start_trace(self, writer: AuditTraceWriter) -> None:
        tid = _uid()
        trace = writer.start_trace(tid, "medical_qa", {"question": "test?"})
        assert trace.trace_id == tid
        assert trace.workflow == "medical_qa"
        assert len(trace.events) == 1
        assert trace.events[0].event_type == "trace_started"

    def test_record_event(self, writer: AuditTraceWriter) -> None:
        tid = _uid()
        writer.start_trace(tid, "test")
        event = writer.record_event(tid, "retrieval", {"count": 5})
        assert event is not None
        assert event.event_type == "retrieval"
        assert event.data["count"] == 5

    def test_record_event_no_trace(self, writer: AuditTraceWriter) -> None:
        tid = _uid()
        event = writer.record_event(tid, "test", {})
        assert event is not None
        assert event.event_type == "test"

    def test_end_trace(self, writer: AuditTraceWriter) -> None:
        tid = _uid()
        writer.start_trace(tid, "test")
        writer.end_trace(tid, {"outcome": "success"})
        trace = writer.get_trace(tid)
        assert trace is not None
        assert trace.completed_at is not None
        assert trace.events[-1].event_type == "trace_completed"

    def test_get_trace_not_found(self, writer: AuditTraceWriter) -> None:
        assert writer.get_trace("nonexistent") is None

    def test_get_recent_traces(self, writer: AuditTraceWriter) -> None:
        ids = [_uid() for _ in range(5)]
        for tid in ids:
            writer.start_trace(tid, "test")
        traces = writer.get_recent_traces(limit=3)
        assert len(traces) == 3

    def test_full_workflow_audit(self, writer: AuditTraceWriter) -> None:
        tid = _uid()
        trace = writer.start_trace(tid, "medical_qa", {"question": "test?"})
        writer.record_event(tid, "safety_check", {"risk": "low"})
        writer.record_event(tid, "retrieval", {"count": 5})
        writer.record_event(tid, "model_call", {"provider": "claude", "model": "sonnet"})
        writer.end_trace(tid, {"outcome": "success"})

        trace = writer.get_trace(tid)
        assert trace is not None
        assert len(trace.events) == 5
        assert trace.events[0].event_type == "trace_started"
        assert trace.events[1].event_type == "safety_check"
        assert trace.events[2].event_type == "retrieval"
        assert trace.events[3].event_type == "model_call"
        assert trace.events[4].event_type == "trace_completed"

    def test_org_id_filtering(self, writer: AuditTraceWriter) -> None:
        t1, t2, t3 = _uid(), _uid(), _uid()
        writer.start_trace(t1, "test", organization_id=1)
        writer.start_trace(t2, "test", organization_id=2)
        writer.start_trace(t3, "test", organization_id=1)

        org1_traces = writer.get_recent_traces(organization_id=1)
        assert len(org1_traces) == 2

        org2_traces = writer.get_recent_traces(organization_id=2)
        assert len(org2_traces) == 1
