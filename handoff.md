# zam-ai-core-api — Handoff

## Project
Python 3.11+ FastAPI medical RAG backend for Zamda Health. Core rule: no LLM response from model internal knowledge, must be grounded in retrieved evidence.

---

## State (~175 tests pass, 0 lint errors)

### ✅ Completed (this session — 2026-07-14)

| Area | Details |
|---|---|
| **3 stubbed endpoint outputs fixed** | `contraindications/check`, `dosage/verify`, `prescriptions/explain` — added `_parse_json_from_response()` helper; updated prompt templates with JSON output schemas; orchestrator now parses LLM output instead of hardcoded stubs |
| **End-to-end integration tests** | `tests/test_ai_integration.py` — 16 tests covering all 7 AI endpoints via FastAPI `TestClient` with mocked orchestrator. Added `tests/conftest.py` with shared fixtures, env cleanup, and key store reset |
| **Missing workflow unit tests** | `tests/test_orchestrator_workflows.py` — 21 tests for `run_medical_qa`, `run_interaction_check`, `run_drug_info`, `run_symptom_guidance` with mocked dependencies |
| **Intent classifier expanded** | Added 6 new intents to `Intent` enum + `IntentClassifier.PATTERNS`: `CONTRAINDICATION_CHECK`, `DOSAGE_VERIFY`, `PRESCRIPTION_EXPLAIN`, `DOCTOR_ASSIST`, `PHARMACY_ASSIST`, `REMINDERS`. Updated `run_workflow` routing — existing 3 route to real `run_*` methods, new 3 return placeholder. Test file expanded from 14 to 25 tests |
| **`asyncio_mode = auto`** | Configured in `pyproject.toml` so async tests work without `--asyncio-mode=auto` flag |
| **TOON format for LLM prompts** | Switched structured data in prompts to TOON (Token-Oriented Object Notation) — ~30-40% token reduction. New `app/ai/toon/` module with `encode_toon`, `decode_toon`, `parse_response`. All 7 workflow templates TOON-encode evidence/patient_context/medications. 3 templates (contraindication, dosage, prescription) ask for TOON output; orchestrator's `_parse_json_from_response` replaced with TOON-first `parse_response()`. |

### ✅ Completed (prior sessions)

| Area | Details |
|---|---|
| **Tier 1 — Foundation** | Health endpoints, API key middleware (validate only, no CRUD), RAG ingestion, `.env` configured |
| **Tier 2 — Endpoints** | 7 AI workflows with full stack (schema → prompt template → manager → orchestrator → composer → route): `medical-qa`, `interactions/check`, `drug-info`, `symptom-guidance`, `contraindications/check`, `dosage/verify`, `prescriptions/explain` |
| **Tier 2 — Modules** | Citation Engine (`app/ai/citation/`), Grounding Verifier (`app/ai/grounding/`), Audit Trace Writer (`app/ai/audit/`) |
| **Tier 3 — Safety** | Safety engine (`app/ai/safety/`) with 4 rule checks (emergency, unsafe request, prompt injection, retrieval required, high risk). Prompt injection detection covers 18 patterns. |
| **Prompt templates** | 13 `.md` files (6 base + 7 workflow), all fixed with correct YAML frontmatter (`---`) |
| **Safety engine tests** | 45 tests covering all risk levels, actions, rule ordering, emergency keywords, high-risk patterns, unsafe requests, retrieval failures, edge cases |
| **Prompt injection detection** | `app/ai/safety/injection.py` — 18 patterns (ignore instructions, jailbreak, system prompt leak, delimiter injection), wired into `evaluate_safety()` as 3rd rule |
| **API key management** | `POST/GET /v1/admin/keys`, `POST .../{id}/rotate`, `POST .../{id}/revoke` — SHA-256 hashed, in-memory store, auto-bootstraps from `ZAM_AI_INTERNAL_API_KEYS` config |
| **Rate limiting middleware** | `app/core/middleware/rate_limit.py` — 60 req/60s per key, 429 response, docs/health exempt |
| **Audit query endpoints** | `GET /v1/audit/traces` + `GET /v1/audit/traces/{trace_id}` — reads from in-memory AuditTraceWriter ring buffer |
| **Model gateway tests** | 20 tests — `ModelResponse`, `StreamEvent`, `MockModelProvider` (generate + stream), factory auto-detect, Claude/Gemini instantiation with/without keys |

### ❌ Remaining Gaps

| Priority | Area | What to do |
|---|---|---|
| **MEDIUM** | OCR pipeline | `POST /v1/ai/prescriptions/ocr-jobs` + `GET .../{job_id}` — need OCR provider, worker queue, schema, routes |
| **MEDIUM** | Doctor assistant endpoint | `POST /v1/ai/doctor/assist` — medication review, patient summary, interaction/contraindication review, patient education draft. Intent classifier has `DOCTOR_ASSIST` pattern (returns placeholder) |
| **MEDIUM** | Pharmacy assistant endpoint | `POST /v1/ai/pharmacy/assist` — drug explanation, interaction review, alternative review, inventory contextualization. Intent classifier has `PHARMACY_ASSIST` pattern (returns placeholder) |
| **MEDIUM** | Reminder schedule parsing | `POST /v1/ai/reminders/parse-schedule` — route, prompt, orchestrator. Intent classifier has `REMINDERS` pattern (returns placeholder) |
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
- 7 pre-existing test failures: 4 in `test_model_gateway.py` (env has `ZAM_AI_MODEL_PROVIDER=claude` so factory tests expecting Mock fail) and 3 in `test_health.py` (no Pinecone DNS in this env)
- `.env` has real keys for Jina embeddings, Pinecone, Voyage, and Claude
- Architecture docs define 8 phases; Phases 2-3 complete, Phases 4-8 not started
