# Zam AI API Specification

## 1. Purpose

This document defines the API surface for Zam AI.

Zam AI is an internal medical AI service called by the main Zamda Health backend.
It does not own end-user authentication, user authorization, partner access,
billing, or the primary application database. The main backend authenticates
users, checks permissions, gathers authorized context, and calls Zam AI using an
internal service credential.

The Zam AI API must be designed around safe medical AI workflows:

- Strict request validation.
- Internal API-key authentication.
- Explicit context boundaries.
- Source-grounded medical responses.
- Structured safety metadata.
- Citations and audit traces.
- Conservative refusal and escalation behavior.

## 2. API Design Principles

### 2.1 Internal by Default

All MVP endpoints are internal. They are called by the main backend, not directly
by patients, doctors, pharmacies, or partners.

### 2.2 Backend Owns User Context

The backend must provide only context the user is authorized to use.

Zam AI must not assume it can query the main application database for missing
patient, pharmacy, doctor, or partner data.

### 2.3 Medical Claims Require Evidence

Endpoints that generate medical answers must return source metadata, citations,
safety metadata, or a refusal.

### 2.4 Structured Outputs

Responses should be structured JSON. Free-form text may be included, but it
should not be the only output.

### 2.5 Versioned Contracts

All endpoints should be versioned under `/v1`. Breaking changes require a new
version.

## 3. Base URL and Versioning

Local:

```text
http://localhost:8000/v1
```

Production:

```text
https://<internal-zam-ai-service>/v1
```

Versioning strategy:

- `/v1` for initial stable internal APIs.
- `/v1beta` only for workflows not ready for production dependency.
- New major versions for breaking request or response schema changes.

## 4. Authentication

### 4.1 Internal API Key

The main backend authenticates to Zam AI using an internal API key.

Header:

```http
X-Zam-AI-Key: <secret>
```

Additional recommended headers:

```http
X-Request-ID: <uuid>
X-Caller-Service: zamda-backend
X-Environment: production
```

Rules:

- Missing or invalid API keys return `401`.
- Valid key but unauthorized caller scope returns `403`.
- Raw keys must never be logged.
- Key identity may be logged as a hashed key ID or configured key label.

## 5. Common Request Envelope

All workflow requests should follow a common envelope.

```json
{
  "request_id": "7d9827b8-9f42-4f4f-8e4a-3c4b4fd973a1",
  "caller": {
    "service": "zamda-backend",
    "environment": "production"
  },
  "actor_context": {
    "actor_type": "patient",
    "actor_id": "backend-user-reference",
    "organization_id": null,
    "role": "patient"
  },
  "authorization_context": {
    "workflow": "medical_qa",
    "consent_flags": {
      "use_patient_context": true,
      "store_ai_trace": true
    },
    "context_scope": ["age", "allergies", "current_medications"]
  },
  "locale": {
    "language": "en",
    "country": "NG"
  },
  "input": {}
}
```

Field notes:

- `actor_id` is a backend reference, not necessarily a database primary key.
- `authorization_context` reflects decisions already made by the backend.
- Zam AI validates the presence and shape of context. It does not re-authenticate
  the end user.

## 6. Common Response Envelope

```json
{
  "request_id": "7d9827b8-9f42-4f4f-8e4a-3c4b4fd973a1",
  "status": "success",
  "workflow": "medical_qa",
  "result": {},
  "safety": {
    "risk_level": "medium",
    "action": "answered",
    "requires_escalation": false,
    "requires_human_review": false
  },
  "citations": [],
  "confidence": {
    "overall": 0.82,
    "grounding": 0.9,
    "retrieval": 0.86
  },
  "audit": {
    "trace_id": "ai-trace-123",
    "prompt_version": "medical_qa:v1",
    "model_provider": "provider-name",
    "model_version": "model-version"
  }
}
```

## 7. Common Error Format

```json
{
  "request_id": "7d9827b8-9f42-4f4f-8e4a-3c4b4fd973a1",
  "status": "error",
  "error": {
    "code": "retrieval_no_evidence",
    "message": "No reliable medical evidence was found for this request.",
    "retryable": false,
    "details": {
      "workflow": "medical_qa"
    }
  },
  "safety": {
    "action": "refused",
    "requires_escalation": false
  }
}
```

Common error codes:

- `authentication_failed`
- `authorization_context_invalid`
- `validation_error`
- `missing_required_context`
- `retrieval_unavailable`
- `retrieval_no_evidence`
- `grounding_failed`
- `unsafe_request`
- `emergency_escalation`
- `model_provider_unavailable`
- `tool_unavailable`
- `ocr_low_confidence`
- `rate_limited`
- `internal_error`

## 8. Endpoint Summary

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/v1/health` | Service health check. |
| `GET` | `/v1/ready` | Readiness check including dependencies. |
| `POST` | `/v1/ai/medical-qa` | Grounded medical question answering. |
| `POST` | `/v1/ai/symptom-guidance` | Symptom guidance and escalation. |
| `POST` | `/v1/ai/drug-info` | Drug information. |
| `POST` | `/v1/ai/interactions/check` | Drug interaction checking. |
| `POST` | `/v1/ai/contraindications/check` | Contraindication checking. |
| `POST` | `/v1/ai/dosage/verify` | Dosage verification support. |
| `POST` | `/v1/ai/prescriptions/ocr-jobs` | Create prescription OCR job. |
| `GET` | `/v1/ai/prescriptions/ocr-jobs/{job_id}` | Get OCR job status/result. |
| `POST` | `/v1/ai/prescriptions/explain` | Explain structured prescription data. |
| `POST` | `/v1/ai/reminders/parse-schedule` | Parse reminder schedule from instructions. |
| `POST` | `/v1/ai/doctor/assist` | Doctor assistant workflow. |
| `POST` | `/v1/ai/pharmacy/assist` | Pharmacy assistant workflow. |
| `POST` | `/v1/admin/evaluations/run` | Start evaluation run. |

## 9. Health Endpoints

### 9.1 `GET /v1/health`

Returns process health.

Response:

```json
{
  "status": "ok",
  "service": "zam-ai",
  "version": "0.1.0"
}
```

### 9.2 `GET /v1/ready`

Checks dependencies required to serve traffic.

Response:

```json
{
  "status": "ready",
  "dependencies": {
    "redis": "ok",
    "metadata_store": "ok",
    "vector_store": "ok",
    "model_gateway": "ok"
  }
}
```

## 10. Medical Q&A

### `POST /v1/ai/medical-qa`

Purpose:

Answer a medical question using verified retrieved evidence.

Request input:

```json
{
  "input": {
    "question": "Can I take ibuprofen if I have stomach ulcers?",
    "patient_context": {
      "age": 42,
      "sex": "female",
      "known_conditions": ["peptic ulcer disease"],
      "allergies": [],
      "current_medications": []
    },
    "conversation_context": {
      "conversation_id": "conv_123",
      "recent_messages": []
    }
  }
}
```

Response result:

```json
{
  "result": {
    "answer": "Ibuprofen may not be appropriate for some people with a history of stomach ulcers. Please speak with a clinician or pharmacist before taking it, especially if you have active ulcer symptoms or are taking other medicines that increase bleeding risk.",
    "missing_context": [],
    "follow_up_questions": [],
    "medical_claims": [
      {
        "claim": "Ibuprofen can increase gastrointestinal bleeding or ulcer risk in susceptible patients.",
        "citation_ids": ["cit_1"]
      }
    ]
  }
}
```

Safety requirements:

- Must retrieve approved sources.
- Must cite medical claims.
- Must refuse if evidence is missing.
- Must escalate emergency symptoms.

## 11. Symptom Guidance

### `POST /v1/ai/symptom-guidance`

Purpose:

Provide non-diagnostic symptom guidance and triage support.

Request input:

```json
{
  "input": {
    "symptoms": "I have chest pain and shortness of breath",
    "patient_context": {
      "age": 55,
      "known_conditions": ["hypertension"]
    }
  }
}
```

Emergency response:

```json
{
  "status": "success",
  "workflow": "symptom_guidance",
  "result": {
    "answer": "Chest pain with shortness of breath can be urgent. Please seek emergency medical care now or contact local emergency services.",
    "triage_level": "emergency",
    "diagnosis_provided": false
  },
  "safety": {
    "risk_level": "emergency",
    "action": "escalated",
    "requires_escalation": true
  }
}
```

Rules:

- Do not diagnose.
- Escalate red flags immediately.
- Ask clarifying questions only when not delaying urgent care.

## 12. Drug Information

### `POST /v1/ai/drug-info`

Purpose:

Return source-grounded medication information.

Request input:

```json
{
  "input": {
    "drug_name": "Augmentin",
    "requested_sections": ["uses", "warnings", "side_effects"],
    "country": "NG"
  }
}
```

Response result:

```json
{
  "result": {
    "normalized_drug": {
      "input_name": "Augmentin",
      "generic_name": "amoxicillin/clavulanate",
      "match_confidence": 0.94
    },
    "sections": {
      "uses": "...",
      "warnings": "...",
      "side_effects": "..."
    }
  }
}
```

## 13. Interaction Check

### `POST /v1/ai/interactions/check`

Purpose:

Check interactions between medications or relevant substances.

Request input:

```json
{
  "input": {
    "medications": [
      {"name": "warfarin", "dose": null},
      {"name": "ibuprofen", "dose": null}
    ],
    "patient_context": {
      "age": 68
    }
  }
}
```

Response result:

```json
{
  "result": {
    "interactions": [
      {
        "medications": ["warfarin", "ibuprofen"],
        "severity": "major",
        "summary": "This combination may increase bleeding risk.",
        "recommended_action": "consult_clinician_or_pharmacist",
        "citation_ids": ["cit_1"]
      }
    ],
    "unknowns": []
  }
}
```

Rules:

- Use deterministic interaction data where available.
- Do not invent interaction severity.
- Return `unknowns` when medications cannot be normalized.

## 14. Contraindication Check

### `POST /v1/ai/contraindications/check`

Purpose:

Check whether supplied medications may be contraindicated for supplied patient
context.

Request input:

```json
{
  "input": {
    "medications": [{"name": "ibuprofen"}],
    "patient_context": {
      "known_conditions": ["peptic ulcer disease"],
      "pregnancy_status": null,
      "allergies": []
    }
  }
}
```

Rules:

- Missing patient context must be reported.
- Contraindications require source evidence.
- High-risk findings require escalation or review metadata.

## 15. Dosage Verification

### `POST /v1/ai/dosage/verify`

Purpose:

Compare supplied dosage instructions against approved references where
available.

Request input:

```json
{
  "input": {
    "medication": {
      "name": "amoxicillin",
      "strength": "500 mg",
      "instructions": "Take one capsule three times daily for 7 days"
    },
    "patient_context": {
      "age": 35,
      "weight_kg": null,
      "renal_impairment": null
    }
  }
}
```

Rules:

- Do not prescribe a new dose.
- Flag unusual or unsupported doses.
- Require review when patient-specific parameters are missing.

## 16. Prescription OCR

### `POST /v1/ai/prescriptions/ocr-jobs`

Purpose:

Create an asynchronous OCR job.

Request input:

```json
{
  "input": {
    "image_reference": "backend-storage-ref",
    "prescription_id": "backend-prescription-ref",
    "callback_url": null
  }
}
```

Response:

```json
{
  "result": {
    "job_id": "ocr_job_123",
    "status": "queued"
  }
}
```

### `GET /v1/ai/prescriptions/ocr-jobs/{job_id}`

Response result:

```json
{
  "result": {
    "job_id": "ocr_job_123",
    "status": "completed",
    "fields": [
      {
        "field": "medication_name",
        "value": "amoxicillin",
        "confidence": 0.91,
        "requires_review": false
      }
    ],
    "overall_confidence": 0.84,
    "requires_human_review": true
  }
}
```

## 17. Prescription Explanation

### `POST /v1/ai/prescriptions/explain`

Purpose:

Explain structured prescription information in patient-friendly language.

Rules:

- Use structured prescription data supplied by backend or OCR result.
- Retrieve drug references.
- Do not assume diagnosis unless supplied.
- Warn when OCR confidence is low.

## 18. Reminder Schedule Parsing

### `POST /v1/ai/reminders/parse-schedule`

Purpose:

Convert medication instructions into proposed reminder schedule objects.

Response result:

```json
{
  "result": {
    "schedule": {
      "frequency": "three_times_daily",
      "times_per_day": 3,
      "duration_days": 7
    },
    "confidence": 0.88,
    "requires_clarification": false
  }
}
```

Rules:

- The backend stores and sends reminders.
- Zam AI only parses and suggests schedule structure.
- Ambiguous instructions require clarification.

## 19. Doctor Assistant

### `POST /v1/ai/doctor/assist`

Purpose:

Support clinician-facing workflows.

Supported task types:

- `medication_review`
- `patient_summary`
- `interaction_review`
- `contraindication_review`
- `patient_education_draft`

Doctor responses should distinguish source-backed facts, patient-supplied
context, and AI-generated synthesis.

## 20. Pharmacy Assistant

### `POST /v1/ai/pharmacy/assist`

Purpose:

Support pharmacy-facing medication intelligence.

Supported task types:

- `drug_explanation`
- `interaction_review`
- `alternative_review`
- `inventory_contextualization`

Rules:

- Inventory availability is not clinical equivalence.
- Alternative recommendations require source-backed clinical rationale.
- Pharmacist review metadata should be returned for substitution workflows.

## 21. Streaming

Streaming may be supported for conversational workflows.

Endpoint pattern:

```text
POST /v1/ai/medical-qa?stream=true
```

Streaming requirements:

- Initial event should include `request_id`.
- Final event must include citations and safety metadata.
- Medical content should not stream if pre-generation safety checks fail.
- If post-generation grounding fails, the final event must instruct the backend
  to discard or replace unsafe partial output.

Recommended event types:

- `message.start`
- `message.delta`
- `citation.delta`
- `safety.final`
- `message.final`
- `error`

## 22. Admin and Evaluation APIs

Admin endpoints should be protected by separate internal credentials or stricter
service identity.

### `POST /v1/admin/evaluations/run`

Purpose:

Start an evaluation run.

Request:

```json
{
  "dataset_id": "medical_qa_core_v1",
  "prompt_version": "medical_qa:v1",
  "model_config": "default",
  "run_type": "regression"
}
```

## 23. Idempotency

Long-running or costly endpoints should support:

```http
Idempotency-Key: <uuid>
```

Required for:

- OCR jobs.
- Batch evaluation runs.
- Source ingestion jobs.
- Any future billing-affecting partner workflow.

## 24. Rate Limits

The main backend should enforce product rate limits. Zam AI should enforce
service protection limits.

Limit dimensions:

- Caller service.
- Workflow.
- Environment.
- Organization or partner if supplied.

High-cost workflows should have stricter limits.

## 25. Audit Metadata

Every medical endpoint should write an audit trace containing:

- Request ID.
- Endpoint.
- Workflow.
- Actor context.
- Authorization context.
- Context fields used.
- Intent and risk classification.
- Retrieved source IDs and versions.
- Tool calls.
- Prompt version.
- Model provider and version.
- Safety result.
- Final action.

## 26. Open Questions

- Should the backend use a single internal API key or separate keys per service
  and environment?
- Which endpoints require streaming in MVP?
- Should OCR callbacks be supported in MVP or should backend polling come first?
- What actor identifiers should be passed to avoid exposing unnecessary database
  IDs?
- Which response fields are displayed to users versus retained only for audit?

## 27. Change Log

| Date | Change | Status |
| --- | --- | --- |
| 2026-06-29 | Initial internal API specification created. | Draft |
