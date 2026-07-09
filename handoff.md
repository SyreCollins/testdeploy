# zam-ai-core-api — Handoff

## Project
Python 3.11+ FastAPI medical RAG backend for Zamda Health. Core rule: no LLM response from model internal knowledge, must be grounded in retrieved evidence.

---

# zam-ai-core-api — Handoff

## Project
Python 3.11+ FastAPI medical RAG backend for Zamda Health. Core rule: no LLM response from model internal knowledge, must be grounded in retrieved evidence.

---

## State (150 tests, 0 lint errors)

### ✅ Completed (this session — 2026-07-08)

| Area | Details |
|---|---|
| **Safety engine tests** | 45 tests covering all risk levels, actions, rule ordering, emergency keywords, high-risk patterns, unsafe requests, retrieval failures, edge cases |
| **Prompt injection detection** | `app/ai/safety/injection.py` — 18 patterns (ignore instructions, jailbreak, system prompt leak, delimiter injection), wired into `evaluate_safety()` as 3rd rule |
| **API key management** | `POST/GET /v1/admin/keys`, `POST .../{id}/rotate`, `POST .../{id}/revoke` — SHA-256 hashed, in-memory store, auto-bootstraps from `ZAM_AI_INTERNAL_API_KEYS` config |
| **Rate limiting middleware** | `app/core/middleware/rate_limit.py` — 60 req/60s per key, 429 response, docs/health exempt |
| **Audit query endpoints** | `GET /v1/audit/traces` + `GET /v1/audit/traces/{trace_id}` — reads from in-memory AuditTraceWriter ring buffer |
| **Model gateway tests** | 20 tests — `ModelResponse`, `StreamEvent`, `MockModelProvider` (generate + stream), factory auto-detect, Claude/Gemini instantiation with/without keys |
| **Unused import cleanup** | Removed stale imports across test files |

### ✅ Completed (prior sessions)

| Area | Details |
|---|---|
| **Tier 1 — Foundation** | Health endpoints, API key middleware (validate only, no CRUD), RAG ingestion, `.env` configured |
| **Tier 2 — Endpoints** | 7 AI workflows with full stack (schema → prompt template → manager → orchestrator → composer → route): `medical-qa`, `interactions/check`, `drug-info`, `symptom-guidance`, `contraindications/check`, `dosage/verify`, `prescriptions/explain` |
| **Tier 2 — Modules** | Citation Engine (`app/ai/citation/`), Grounding Verifier (`app/ai/grounding/`), Audit Trace Writer (`app/ai/audit/`) |
| **Tier 3 — Safety** | Safety engine (`app/ai/safety/`) with 4 rule checks (emergency, unsafe request, prompt injection, retrieval required, high risk). Prompt injection detection covers 18 patterns. |
| **Prompt templates** | 13 `.md` files (6 base + 7 workflow), all fixed with correct YAML frontmatter (`---`) |
| **Test total** | 150 passing tests, 14 test files |

### ❌ Remaining Gaps (HIGH first)

| Priority | Area | What to do |
|---|---|---|
| **HIGH** | 3 endpoint outputs stubbed | `contraindications/check` returns "severity: unknown", `dosage/verify` returns "assessment: verified", `prescriptions/explain` returns raw LLM text — none parse real LLM output into structured fields |
| **MEDIUM** | End-to-end tests | Route-level integration tests using FastAPI `TestClient` for all 7 AI endpoints |
| **MEDIUM** | Missing workflow tests | `test_medical_qa`, `test_interaction_check`, `test_drug_info`, `test_symptom_guidance` — no dedicated unit tests |
| **MEDIUM** | OCR pipeline | `POST /v1/ai/prescriptions/ocr-jobs` + `GET .../{job_id}` — need OCR provider, worker queue, schema, routes |
| **MEDIUM** | Doctor assistant endpoint | `POST /v1/ai/doctor/assist` — medication review, patient summary, interaction/contraindication review, patient education draft |
| **MEDIUM** | Pharmacy assistant endpoint | `POST /v1/ai/pharmacy/assist` — drug explanation, interaction review, alternative review, inventory contextualization |
| **MEDIUM** | Intent classifier incomplete | Cannot classify `contraindication_check`, `dosage_verify`, `prescription_explain`, `doctor_assist`, `pharmacy_assist`, `reminders` — falls back to GENERAL or MEDICAL_QA |
| **MEDIUM** | Reminder schedule parsing | `POST /v1/ai/reminders/parse-schedule` — route, prompt, orchestrator |
| **LOW** | 13 prompt templates not created | `medication_schedule.md`, `health_guidance.md`, 3 pharmacy workflow prompts, 3 doctor workflow prompts, 3 JSON response schemas, `examples/` directory |
| **LOW** | 17 empty domain/integration scaffolds | `app/domains/*` (9 directories) and `app/integrations/*` (5 directories) — all just `__init__.py` |
| **LOW** | `tests/__init__.py` | Add package init |
| **LOW** | `test_admin_api.py` | Source file missing (only `__pycache__` remains) |
| **LOW** | CI/CD | No `.github/workflows/`, no coverage config, no pre-commit |
| **LOW** | Type checking | No mypy/pyright in dev deps or config |

### Notes
- Routes live at `app/api/routes/` (not `app/api/v1/ai/`) and are prefixed `/v1` via `app/main.py`
- Ingestion is embedded in `app/rag/service.py` (not standalone `app/ingest/`)
- 0 TODO/FIXME/HACK/XXX comments in codebase
- `.env` has real keys for Jina embeddings, Pinecone, and Voyage — Claude key still needs to be set
- Architecture docs define 8 phases; Phase 2 is complete, Phases 3-8 not started
