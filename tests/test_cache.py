import time

import pytest

from app.ai.cache import ResponseCache
from app.ai.orchestrator.models import WorkflowResult


class TestResponseCache:
    def test_make_key_deterministic(self):
        cache = ResponseCache()
        key1 = cache.make_key("medical_qa", question="what is amoxicillin", patient_age=30)
        key2 = cache.make_key("medical_qa", question="what is amoxicillin", patient_age=30)
        assert key1 == key2

    def test_make_key_different_inputs(self):
        cache = ResponseCache()
        key1 = cache.make_key("medical_qa", question="what is amoxicillin")
        key2 = cache.make_key("medical_qa", question="what is ibuprofen")
        assert key1 != key2

    def test_make_key_different_workflows(self):
        cache = ResponseCache()
        key1 = cache.make_key("medical_qa", question="what is amoxicillin")
        key2 = cache.make_key("drug_info", question="what is amoxicillin")
        assert key1 != key2

    def test_set_and_get(self):
        cache = ResponseCache(default_ttl=3600)
        result = WorkflowResult(success=True, response_text="test", workflow="medical_qa")
        key = cache.make_key("medical_qa", q="test")
        cache.set(key, result)
        cached = cache.get(key)
        assert cached is not None
        assert cached.response_text == "test"
        assert cached.success is True

    def test_get_returns_deepcopy(self):
        cache = ResponseCache()
        result = WorkflowResult(
            success=True, response_text="original", workflow="test",
            structured_result={"key": "val"},
        )
        key = cache.make_key("test", q="x")
        cache.set(key, result)
        cached = cache.get(key)
        cached.response_text = "changed"
        cached.structured_result["key"] = "modified"
        assert result.response_text == "original"
        assert result.structured_result["key"] == "val"

    def test_miss_returns_none(self):
        cache = ResponseCache()
        assert cache.get("nonexistent") is None

    def test_expiry(self):
        cache = ResponseCache(default_ttl=0)
        result = WorkflowResult(success=True, response_text="test", workflow="test")
        key = cache.make_key("test", q="x")
        cache.set(key, result)
        time.sleep(0.01)
        assert cache.get(key) is None

    def test_invalidate_all(self):
        cache = ResponseCache()
        for i in range(3):
            r = WorkflowResult(success=True, response_text=f"test{i}", workflow=f"wf{i}")
            cache.set(cache.make_key(f"wf{i}", q="x"), r)
        assert cache.size == 3
        cache.invalidate()
        assert cache.size == 0

    def test_invalidate_workflow(self):
        cache = ResponseCache()
        entries = [("medical_qa", "a"), ("medical_qa", "b"), ("drug_info", "x")]
        for wf, q in entries:
            r = WorkflowResult(success=True, response_text="test", workflow=wf)
            cache.set(cache.make_key(wf, q=q), r)
        assert cache.size == 3
        cache.invalidate("medical_qa")
        assert cache.size == 1

    def test_max_size_eviction(self):
        cache = ResponseCache(default_ttl=3600, max_size=3)
        for i in range(4):
            r = WorkflowResult(success=True, response_text=f"test{i}", workflow="wf")
            cache.set(cache.make_key("wf", q=str(i)), r)
        assert cache.size == 3

    def test_make_key_with_dict_param(self):
        cache = ResponseCache()
        key = cache.make_key("dosage_verify", medication={"name": "amoxicillin", "dose": "500mg"})
        assert isinstance(key, str)
        assert key.startswith("dosage_verify_")
        assert len(key) > 64

    def test_make_key_with_list_param(self):
        cache = ResponseCache()
        key = cache.make_key("interaction_check", drug_names=["aspirin", "ibuprofen"])
        assert isinstance(key, str)
        assert key.startswith("interaction_check_")
        assert len(key) > 64

    def test_make_key_ignores_none_values(self):
        cache = ResponseCache()
        key = cache.make_key("test", param=None)
        assert isinstance(key, str)
        assert key.startswith("test_")
        assert len(key) > 64


@pytest.mark.asyncio
async def test_orchestrator_returns_cached_result(app):
    from app.ai.safety.base import RiskLevel, SafetyAction, SafetyDecision
    from app.rag.vector_store.memory import MemoryVectorStore
    orch = app.state.orchestrator
    orch.retrieval.vector_store = MemoryVectorStore()
    orch._cache_enabled = True
    orch._check_safety_post_retrieval = lambda ctx, results: SafetyDecision(
        risk_level=RiskLevel.LOW, action=SafetyAction.ANSWERED,
    )

    real_call_model = orch._call_model

    call_count = 0

    async def counting_call_model(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return await real_call_model(*args, **kwargs)

    orch._call_model = counting_call_model

    orch._cache.invalidate()

    result1 = await orch.run_medical_qa(
        question="What is amoxicillin used for?",
        request_id="req-1",
    )
    assert result1.success is True
    assert call_count == 1

    result2 = await orch.run_medical_qa(
        question="What is amoxicillin used for?",
        request_id="req-2",
    )
    assert result2.success is True
    assert call_count == 1

    assert result1.response_text == result2.response_text
    assert result2.audit_metadata["trace_id"] == "req-2"


@pytest.mark.asyncio
async def test_orchestrator_cache_miss_on_different_input(app):
    from app.ai.safety.base import RiskLevel, SafetyAction, SafetyDecision
    from app.rag.vector_store.memory import MemoryVectorStore
    orch = app.state.orchestrator
    orch.retrieval.vector_store = MemoryVectorStore()
    orch._cache_enabled = True
    orch._check_safety_post_retrieval = lambda ctx, results: SafetyDecision(
        risk_level=RiskLevel.LOW, action=SafetyAction.ANSWERED,
    )

    real_call_model = orch._call_model
    call_count = 0

    async def counting_call_model(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return await real_call_model(*args, **kwargs)

    orch._call_model = counting_call_model
    orch._cache.invalidate()

    await orch.run_medical_qa(question="What is amoxicillin?", request_id="req-1")
    assert call_count == 1

    await orch.run_medical_qa(question="What is ibuprofen?", request_id="req-2")
    assert call_count == 2


@pytest.mark.asyncio
async def test_orchestrator_cache_disabled_works_normally(app):
    from app.ai.safety.base import RiskLevel, SafetyAction, SafetyDecision
    from app.rag.vector_store.memory import MemoryVectorStore
    orch = app.state.orchestrator
    orch.retrieval.vector_store = MemoryVectorStore()
    orch._cache_enabled = False
    orch._check_safety_post_retrieval = lambda ctx, results: SafetyDecision(
        risk_level=RiskLevel.LOW, action=SafetyAction.ANSWERED,
    )

    real_call_model = orch._call_model
    call_count = 0

    async def counting_call_model(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return await real_call_model(*args, **kwargs)

    orch._call_model = counting_call_model

    await orch.run_medical_qa(question="What is amoxicillin?", request_id="req-1")
    assert call_count == 1

    await orch.run_medical_qa(question="What is amoxicillin?", request_id="req-2")
    assert call_count == 2
