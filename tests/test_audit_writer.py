import pytest

from app.ai.audit import AuditTrace, AuditTraceWriter


@pytest.fixture
def writer() -> AuditTraceWriter:
    return AuditTraceWriter(max_traces=10)


class TestAuditTrace:
    def test_add_event(self) -> None:
        trace = AuditTrace(trace_id="t1", workflow="test", started_at="now")
        event = trace.add_event("model_call", {"provider": "test"})
        assert event.event_type == "model_call"
        assert event.data["provider"] == "test"
        assert len(trace.events) == 1

    def test_complete(self) -> None:
        trace = AuditTrace(trace_id="t1", workflow="test", started_at="now")
        assert trace.completed_at is None
        trace.complete()
        assert trace.completed_at is not None


class TestAuditTraceWriter:
    def test_start_trace(self, writer: AuditTraceWriter) -> None:
        trace = writer.start_trace("t1", "medical_qa", {"question": "test?"})
        assert trace.trace_id == "t1"
        assert trace.workflow == "medical_qa"
        assert len(trace.events) == 1
        assert trace.events[0].event_type == "trace_started"

    def test_record_event(self, writer: AuditTraceWriter) -> None:
        writer.start_trace("t1", "test")
        event = writer.record_event("t1", "retrieval", {"count": 5})
        assert event is not None
        assert event.event_type == "retrieval"
        assert event.data["count"] == 5

    def test_record_event_no_trace(self, writer: AuditTraceWriter) -> None:
        event = writer.record_event("nonexistent", "test", {})
        assert event is not None
        assert event.event_type == "test"

    def test_end_trace(self, writer: AuditTraceWriter) -> None:
        writer.start_trace("t1", "test")
        writer.end_trace("t1", {"outcome": "success"})
        trace = writer.get_trace("t1")
        assert trace is not None
        assert trace.completed_at is not None
        assert trace.events[-1].event_type == "trace_completed"

    def test_get_trace_not_found(self, writer: AuditTraceWriter) -> None:
        assert writer.get_trace("nonexistent") is None

    def test_get_recent_traces(self, writer: AuditTraceWriter) -> None:
        for i in range(5):
            writer.start_trace(f"t{i}", "test")
        traces = writer.get_recent_traces(limit=3)
        assert len(traces) == 3

    def test_max_traces_eviction(self) -> None:
        writer = AuditTraceWriter(max_traces=3)
        for i in range(5):
            writer.start_trace(f"t{i}", "test")
        assert len(writer.get_recent_traces(limit=10)) == 3

    def test_full_workflow_audit(self, writer: AuditTraceWriter) -> None:
        trace = writer.start_trace("wf1", "medical_qa", {"question": "test?"})
        writer.record_event("wf1", "safety_check", {"risk": "low"})
        writer.record_event("wf1", "retrieval", {"count": 5})
        writer.record_event("wf1", "model_call", {"provider": "claude", "model": "sonnet"})
        writer.end_trace("wf1", {"outcome": "success"})

        trace = writer.get_trace("wf1")
        assert trace is not None
        assert len(trace.events) == 5
        assert trace.events[0].event_type == "trace_started"
        assert trace.events[1].event_type == "safety_check"
        assert trace.events[2].event_type == "retrieval"
        assert trace.events[3].event_type == "model_call"
        assert trace.events[4].event_type == "trace_completed"
