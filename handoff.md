# zam-ai-core-api — Handoff

## Project
Python 3.11+ FastAPI medical RAG backend for Zamda Health. Core rule: no LLM response from model internal knowledge, must be grounded in retrieved evidence.

---

## State (~221 tests pass, 0 lint errors, CI/CD active)

### ✅ Completed (this session — 2026-07-15)

| Area | Details |
|---|---|
| **`/v1/ai/chat` endpoint wired up** | New `POST /v1/ai/chat` route — accepts free-text message, runs `classify_intent()` to detect intent, delegates to `orchestrator.run_workflow()`. Returns `ChatResponse` with `intent`, `confidence`, `answer`, safety/citations/confidence/audit metadata. Added `ChatInput`, `ChatRequest`, `ChatResult`, `ChatResponse` schemas + `composer.chat()` method. 8 integration tests + 15 `run_workflow` unit tests covering all 7 intents, emergency, unsupported, patient context, explicit intent, request_id, and placeholder intents |
| **Parallel multi-drug retrieval** | `run_interaction_check` and `run_contraindication_check` use `asyncio.gather()` to search all drugs concurrently instead of sequentially. 3-drug check drops from 3× latency to 1× |
| **N+1 query eliminated** | New `RagRegistry.get_chunk_metadata_batch()` loads chunk + document + source metadata in a single `selectinload`-based query (3 SQL calls total vs 3×N). `RetrievalService.search()` collects chunk IDs, makes one batch call, maps results |
| **LLM timeout + retry** | New `ZAM_AI_MODEL_TIMEOUT` (default 60s) and `ZAM_AI_MODEL_RETRY_COUNT` (default 1) settings. `_call_model()` wraps `generate()` in `asyncio.wait_for()` — hanging API calls no longer stall indefinitely. Configurable retry on timeout/failure |

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

### 🧠 Architecture notes

- `ConversationOrchestrator` is instantiated in `app/main.py:75` and stored in `app.state.orchestrator`. Every route retrieves it via `_orch(request)` and calls specific `run_*` methods directly.
- `IntentClassifier` and `ConversationOrchestrator.classify_intent()` are **dead code in production** — fully tested but NOT wired to any route. Designed for a future `/v1/ai/chat` endpoint that was planned but never created.
- **No `/v1/ai/chat` endpoint exists.** Frontend calls individual workflow endpoints directly.
- Routes live at `app/api/routes/` and are prefixed `/v1` via `app/main.py`
- Ingestion is embedded in `app/rag/service.py` (not standalone `app/ingest/`)
- 0 TODO/FIXME/HACK/XXX comments in codebase
- `.env` has real keys for Jina embeddings, Pinecone, Voyage, and Claude
- Architecture docs define 8 phases; Phases 2-3 complete, Phases 4-8 not started

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
| **LOW** | Type checking | No mypy/pyright in dev deps or config |
