from unittest.mock import AsyncMock

from app.ai.orchestrator.models import WorkflowResult

API_PREFIX = "/v1/ai"

_BASE = {
    "caller": {"service": "test", "environment": "test"},
    "locale": {"language": "en", "country": "NG"},
}


def _make_success_result(workflow: str, response_text: str = "Success.", structured: dict | None = None):
    return WorkflowResult(
        success=True,
        response_text=response_text,
        workflow=workflow,
        citations=[{
            "citation_id": "c1",
            "text_content": "Evidence text.",
            "score": 0.85,
            "source_name": "Test Source",
            "source_version": "1.0",
            "source_trust_tier": 1,
        }],
        safety_metadata={"risk_level": "low", "action": "answered"},
        confidence_metadata={"overall": 0.8, "grounding": 0.0, "retrieval": 0.8},
        audit_metadata={"model_provider": "mock", "model_version": "mock-v1"},
        structured_result=structured or {},
    )


def _make_mock(app, workflow: str, structured: dict, response_text: str = "Success."):
    mock = AsyncMock(spec=app.state.orchestrator)
    result = _make_success_result(workflow, response_text, structured)
    getattr(mock, f"run_{workflow}").return_value = result
    app.state.orchestrator = mock
    return mock


ACTOR = {"actor_type": "patient", "actor_id": "t1", "role": "patient"}
AUTH = {"workflow": "test", "consent_flags": {"use_patient_context": True, "store_ai_trace": True}}


class TestMedicalQAIntegration:
    ENDPOINT = f"{API_PREFIX}/medical-qa"

    def test_success(self, client, auth_headers, app):
        _mock_mock(app, "medical_qa", {
            "medical_claims": [{"claim": "NSAIDs increase bleeding risk.", "citation_ids": ["c1"]}],
            "missing_context": [],
            "follow_up_questions": [],
        })
        resp = client.post(self.ENDPOINT, json={
            **_BASE, "actor_context": ACTOR, "authorization_context": AUTH,
            "input": {"question": "Can I take ibuprofen with stomach ulcers?", "patient_context": {"age": 45}},
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert data["workflow"] == "medical_qa"
        assert len(data["result"]["medical_claims"]) == 1

    def test_requires_auth(self, client):
        resp = client.post(self.ENDPOINT, json={
            **_BASE, "actor_context": ACTOR, "authorization_context": AUTH,
            "input": {"question": "test"},
        })
        assert resp.status_code == 401

    def test_invalid_body(self, client, auth_headers):
        resp = client.post(self.ENDPOINT, json={}, headers=auth_headers)
        assert resp.status_code == 422

    def test_empty_question(self, client, auth_headers):
        resp = client.post(self.ENDPOINT, json={
            **_BASE, "actor_context": ACTOR, "authorization_context": AUTH,
            "input": {"question": ""},
        }, headers=auth_headers)
        assert resp.status_code == 422


class TestInteractionCheck:
    ENDPOINT = f"{API_PREFIX}/interactions/check"

    def test_success(self, client, auth_headers, app):
        _mock_mock(app, "interaction_check", {
            "interactions": [{
                "medications": ["warfarin", "ibuprofen"],
                "severity": "moderate",
                "summary": "Increased bleeding risk.",
                "citation_ids": ["c1"],
            }],
            "unknowns": [],
        })
        resp = client.post(self.ENDPOINT, json={
            **_BASE, "actor_context": ACTOR, "authorization_context": AUTH,
            "input": {"medications": [{"name": "warfarin"}, {"name": "ibuprofen"}], "patient_context": {"age": 65}},
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()["result"]["interactions"]) == 1

    def test_requires_two_medications(self, client, auth_headers):
        resp = client.post(self.ENDPOINT, json={
            **_BASE, "actor_context": ACTOR, "authorization_context": AUTH,
            "input": {"medications": [{"name": "warfarin"}]},
        }, headers=auth_headers)
        assert resp.status_code == 422


class TestDrugInfo:
    ENDPOINT = f"{API_PREFIX}/drug-info"

    def test_success(self, client, auth_headers, app):
        _mock_mock(app, "drug_info", {
            "normalized_drug": {"input_name": "Augmentin"},
            "sections": {"uses": "Treats bacterial infections."},
        })
        resp = client.post(self.ENDPOINT, json={
            **_BASE, "actor_context": ACTOR, "authorization_context": AUTH,
            "input": {"drug_name": "Augmentin"},
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["result"]["normalized_drug"]["input_name"] == "Augmentin"

    def test_requires_drug_name(self, client, auth_headers):
        resp = client.post(self.ENDPOINT, json={
            **_BASE, "actor_context": ACTOR, "authorization_context": AUTH,
            "input": {},
        }, headers=auth_headers)
        assert resp.status_code == 422


class TestSymptomGuidance:
    ENDPOINT = f"{API_PREFIX}/symptom-guidance"

    def test_success(self, client, auth_headers, app):
        _mock_mock(app, "symptom_guidance", {
            "triage_level": "non_urgent", "diagnosis_provided": False,
        })
        resp = client.post(self.ENDPOINT, json={
            **_BASE, "actor_context": ACTOR, "authorization_context": AUTH,
            "input": {"symptoms": "I have a headache"},
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["result"]["triage_level"] == "non_urgent"

    def test_requires_symptoms(self, client, auth_headers):
        resp = client.post(self.ENDPOINT, json={
            **_BASE, "actor_context": ACTOR, "authorization_context": AUTH,
            "input": {},
        }, headers=auth_headers)
        assert resp.status_code == 422


class TestContraindicationCheck:
    ENDPOINT = f"{API_PREFIX}/contraindications/check"

    def test_success(self, client, auth_headers, app):
        _mock_mock(app, "contraindication_check", {
            "contraindications": [{
                "medication": "ibuprofen",
                "condition": "peptic ulcer disease",
                "severity": "contraindicated",
                "reason": "Increased bleeding risk.",
                "citation_ids": ["c1"],
            }],
            "missing_context": [],
            "unknowns": [],
        })
        resp = client.post(self.ENDPOINT, json={
            **_BASE, "actor_context": ACTOR, "authorization_context": AUTH,
            "input": {
                "medications": [{"name": "ibuprofen"}],
                "patient_context": {"age": 60, "known_conditions": ["peptic ulcer disease"]},
            },
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["result"]["contraindications"][0]["severity"] == "contraindicated"

    def test_no_contraindications(self, client, auth_headers, app):
        _mock_mock(app, "contraindication_check", {
            "contraindications": [], "missing_context": [], "unknowns": [],
        })
        resp = client.post(self.ENDPOINT, json={
            **_BASE, "actor_context": ACTOR, "authorization_context": AUTH,
            "input": {"medications": [{"name": "paracetamol"}]},
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()["result"]["contraindications"]) == 0


class TestDosageVerify:
    ENDPOINT = f"{API_PREFIX}/dosage/verify"

    def test_success(self, client, auth_headers, app):
        _mock_mock(app, "dosage_verify", {
            "dosages": [{
                "medication_name": "amoxicillin",
                "stated_dosage": "500 mg three times daily",
                "assessment": "verified",
                "typical_range": "250-500 mg three times daily",
                "flags": [],
                "citation_ids": ["c1"],
            }],
            "missing_context": [],
        })
        resp = client.post(self.ENDPOINT, json={
            **_BASE, "actor_context": ACTOR, "authorization_context": AUTH,
            "input": {
                "medication": {"name": "amoxicillin", "strength": "500 mg", "instructions": "three times daily"},
                "patient_context": {"age": 30},
            },
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["result"]["dosages"][0]["assessment"] == "verified"

    def test_with_flags(self, client, auth_headers, app):
        _mock_mock(app, "dosage_verify", {
            "dosages": [{
                "medication_name": "gentamicin",
                "stated_dosage": "240 mg once daily",
                "assessment": "caution",
                "typical_range": "3-5 mg/kg/day",
                "flags": ["missing_weight", "renal_concern"],
                "citation_ids": ["c1"],
            }],
            "missing_context": ["weight", "renal_function"],
        })
        resp = client.post(self.ENDPOINT, json={
            **_BASE, "actor_context": ACTOR, "authorization_context": AUTH,
            "input": {
                "medication": {"name": "gentamicin", "strength": "240 mg", "instructions": "once daily"},
                "patient_context": {"age": 70},
            },
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()["result"]
        assert "missing_weight" in data["dosages"][0]["flags"]
        assert "weight" in data["missing_context"]


class TestPrescriptionExplain:
    ENDPOINT = f"{API_PREFIX}/prescriptions/explain"

    def test_success(self, client, auth_headers, app):
        _mock_mock(app, "prescription_explain", {
            "summary": "This prescription is for an antibiotic.",
            "sections": [{
                "title": "What it is for",
                "content": "Amoxicillin treats bacterial infections.",
                "citation_ids": ["c1"],
            }],
            "warnings": ["Take with food."],
        })
        resp = client.post(self.ENDPOINT, json={
            **_BASE, "actor_context": ACTOR, "authorization_context": AUTH,
            "input": {"prescription_text": "Amoxicillin 500mg three times daily for 7 days"},
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert len(data["result"]["sections"]) == 1
        assert len(data["result"]["warnings"]) == 1

    def test_requires_prescription_text(self, client, auth_headers):
        resp = client.post(self.ENDPOINT, json={
            **_BASE, "actor_context": ACTOR, "authorization_context": AUTH,
            "input": {},
        }, headers=auth_headers)
        assert resp.status_code == 422


class TestChat:
    ENDPOINT = f"{API_PREFIX}/chat"

    def _mock_chat(
        self, app, intent: str, structured: dict | None = None,
        response_text: str = "Chat result.", confidence: float = 0.85,
    ):
        from app.ai.orchestrator.models import Intent
        mock = AsyncMock(spec=app.state.orchestrator)
        mock.classify_intent.return_value = (Intent(intent), confidence)
        result = _make_success_result(intent, response_text, structured or {})
        mock.run_workflow.return_value = result
        app.state.orchestrator = mock
        return mock

    def test_success_medical_qa(self, client, auth_headers, app):
        self._mock_chat(app, "medical_qa", {
            "medical_claims": [{"claim": "NSAIDs increase bleeding risk.", "citation_ids": ["c1"]}],
            "missing_context": [],
            "follow_up_questions": [],
        })
        resp = client.post(self.ENDPOINT, json={
            **_BASE, "actor_context": ACTOR, "authorization_context": AUTH,
            "input": {"message": "Can I take ibuprofen with stomach ulcers?"},
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert data["workflow"] == "chat"
        assert data["result"]["intent"] == "medical_qa"
        assert data["result"]["confidence"] == 0.85
        assert len(data["citations"]) == 1

    def test_success_drug_info(self, client, auth_headers, app):
        self._mock_chat(app, "drug_info", {
            "normalized_drug": {"input_name": "amoxicillin"},
            "sections": {"uses": "Treats infections."},
        })
        resp = client.post(self.ENDPOINT, json={
            **_BASE, "actor_context": ACTOR, "authorization_context": AUTH,
            "input": {"message": "Tell me about amoxicillin"},
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["result"]["intent"] == "drug_info"
        assert data["result"]["answer"] == "Chat result."

    def test_handles_unsupported_intent(self, client, auth_headers, app):
        self._mock_chat(app, "general", response_text="I can only answer medical questions.")
        resp = client.post(self.ENDPOINT, json={
            **_BASE, "actor_context": ACTOR, "authorization_context": AUTH,
            "input": {"message": "What is the weather like?"},
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["result"]["intent"] == "general"

    def test_handles_emergency(self, client, auth_headers, app):
        self._mock_chat(app, "emergency", response_text="Please seek emergency medical care immediately.")
        resp = client.post(self.ENDPOINT, json={
            **_BASE, "actor_context": ACTOR, "authorization_context": AUTH,
            "input": {"message": "I have chest pain"},
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["result"]["intent"] == "emergency"

    def test_with_patient_context(self, client, auth_headers, app):
        self._mock_chat(app, "medical_qa", {
            "medical_claims": [], "missing_context": [], "follow_up_questions": [],
        })
        resp = client.post(self.ENDPOINT, json={
            **_BASE, "actor_context": ACTOR, "authorization_context": AUTH,
            "input": {
                "message": "Is this safe?",
                "patient_context": {"age": 30, "known_conditions": ["asthma"], "allergies": ["sulfa"]},
            },
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"

    def test_requires_auth(self, client, app):
        resp = client.post(self.ENDPOINT, json={
            **_BASE, "actor_context": ACTOR, "authorization_context": AUTH,
            "input": {"message": "test"},
        })
        assert resp.status_code == 401

    def test_invalid_body(self, client, auth_headers):
        resp = client.post(self.ENDPOINT, json={}, headers=auth_headers)
        assert resp.status_code == 422

    def test_empty_message(self, client, auth_headers):
        resp = client.post(self.ENDPOINT, json={
            **_BASE, "actor_context": ACTOR, "authorization_context": AUTH,
            "input": {"message": ""},
        }, headers=auth_headers)
        assert resp.status_code == 422


def _mock_mock(app, workflow: str, structured: dict, response_text: str = "Success."):
    mock = AsyncMock(spec=app.state.orchestrator)
    result = _make_success_result(workflow, response_text, structured)
    getattr(mock, f"run_{workflow}").return_value = result
    app.state.orchestrator = mock