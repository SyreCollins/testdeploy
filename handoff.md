# zam-ai-core-api — Handoff

## Project
Python 3.11+ FastAPI medical RAG backend for Zamda Health. Core rule: no LLM response from model internal knowledge, must be grounded in retrieved evidence (except `interaction_check` which can use LLM knowledge + disclaimer).

---

## State (~222 tests pass, 0 lint errors, CI/CD active)

### ✅ Completed (this session — 2026-07-22)

| Area | Details |
|---|---|
| **Follow-up questions extended to all workflows** | `drug_info`, `symptom_guidance`, `interaction_check`, `contraindication_check`, `dosage_verify`, `prescription_explain` — each prompt template now instructs LLM to optionally include `## Follow-up Questions`; orchestrator extracts, strips from answer, adds to `structured_result`; composer passes to response; TS types synced |
| **Fixed broken TOON output prompts** | `contraindication_checker.md` and `dosage_verifier.md` instructed LLM to output TOON format, but the `toon-format` library decoder is a stub (`NotImplementedError`). Changed to JSON output format — `_parse_json_from_response` already handles JSON |

### ✅ Completed (this session — 2026-07-21)

| Area | Details |
|---|---|
| **Citation metadata null fixed** | `RagRegistry.get_chunk_metadata_batch()` rewritten with explicit SQL joins instead of chained `selectinload` — `source_name`, `document_title`, `source_version` now populate correctly |
| **Low confidence scores tuned** | `app/ai/scoring/confidence.py` — None-tier weight 0.5→0.8, coverage factor now starts at 0.5 floor. `app/ai/grounding/verifier.py` — threshold 25%→20%, tokenizer includes numbers + bigrams for phrase-level overlap |
| **Interaction check uses LLM knowledge** | `prompts/workflows/patient/interaction_checker.md` v1.0.0→v1.1.0 — now allows LLM to use its own knowledge for interactions (not just retrieved evidence). Mandatory disclaimer added. `app/ai/prompts/manager.py` — default `safety_requirements` updated |
| **Unused dep identified** | `httpx` in dev dependencies — never imported anywhere. Tests use FastAPI's `TestClient` |
| **TypeScript types generated** | `types/` folder — 16 `.ts` files covering all API request/response schemas, AI models (Intent, Safety, Grounding, Citations, Audit, Gateway), RAG schemas, and config. Barrel export via `types/index.ts` |
| **Sample request bodies** | `body.json` now has all 10 endpoint request bodies (8 AI workflows + retrieval + create API key) |
| **SaaS platform plan** | `docs/saas-platform-plan.md` — full 5-phase plan: Neon migration, Clerk auth, orgs/users/api_keys tables, audit persistence, usage tracking, rate limiting. Decisions: Neon DB, Clerk auth (GitHub/Google/magic link), "Both" access model (internal key + direct partner keys), Full v1 scope |
| **Handoff cleanup** | Deduplicated repeated sections in this file |

### ✅ Completed (this session — 2026-07-20)

| Area | Details |
|---|---|
| **Detailed request logging** | New `RequestLoggingMiddleware` logs full request body, headers, response body, latency for every request |
| **Startup env audit log** | `main.py` now logs which env vars are present at startup |
| **Fixed Dockerfile** | Added `COPY prompts ./prompts` — prompts were missing in Docker image |
| **Cleaner claim formatting** | `CitationEngine._clean_claim()` normalizes newlines/whitespace in claim text |
| **Conversational tone** | Updated `system.md` and `medication_info.md` prompts to be warm, empathetic, natural |
| **Follow-up questions** | `_extract_follow_up_questions()` parses model response, strips from answer text, populates `follow_up_questions` field |

### ✅ Completed (prior sessions)

| Area | Details |
|---|---|
| **18 endpoint markdown docs** | `docs/endpoints/` — one `.md` per endpoint (13 built + 5 planned). Full request/response JSON, field tables, safety rules, code examples in 6 languages |
| **Tier 1 — Foundation** | Health endpoints, API key middleware, RAG ingestion, `.env` configured |
| **Tier 2 — Endpoints** | 7 AI workflows with full stack: `medical-qa`, `interactions/check`, `drug-info`, `symptom-guidance`, `contraindications/check`, `dosage/verify`, `prescriptions/explain` |
| **Tier 2 — Modules** | Citation Engine, Grounding Verifier, Audit Trace Writer |
| **Tier 3 — Safety** | Safety engine with 4 rule checks (emergency, unsafe request, prompt injection, retrieval required, high risk). 45 tests |
| **Prompt templates** | 13 `.md` files (6 base + 7 workflow) |
| **API key management** | CRUD endpoints for API keys — SHA-256 hashed, in-memory store |
| **Rate limiting middleware** | 60 req/60s per key, docs/health exempt |
| **Audit query endpoints** | `GET /v1/audit/traces` + `GET /v1/audit/traces/{trace_id}` |
| **`/v1/ai/chat` endpoint** | Full chat endpoint with intent classification + routing |
| **Parallel multi-drug retrieval** | `asyncio.gather()` in interaction + contraindication checks |
| **N+1 query eliminated** | `get_chunk_metadata_batch()` with single batch query |
| **LLM timeout + retry** | Configurable timeout + retry in `_call_model()` |

### 🧠 Architecture notes / Tips

- **Intent classifier improvement:** Current regex-based classifier (`app/ai/orchestrator/intent_classifier.py`) misses common queries like "Can I take ibuprofen?" or "What is amoxicillin?" because drug names aren't in the patterns. Consider switching to a small LLM call (Claude Haiku / Gemini Flash) for classification — tiny prompt, single-token output, ~200ms latency, understands any phrasing naturally.

### 🧠 Architecture notes

- `ConversationOrchestrator` is stored in `app.state.orchestrator`. Routes retrieve via `_orch(request)` and call `run_*` methods directly.
- Routes at `app/api/routes/` prefixed `/v1` via `app/main.py`
- Ingestion in `app/rag/service.py` (not standalone `app/ingest/`)
- 0 TODO/FIXME/HACK/XXX comments in codebase
- `.env` has real keys for Jina, Pinecone, Voyage, and Claude
- Arch docs define 8 phases; Phases 2-3 complete, Phases 4-8 not started
- SaaS model (ADR 6): Partners route through main backend. Zam AI called with single internal key. New plan adds direct partner keys as second tier.

### ❌ Remaining Gaps

| Priority | Area | What to do |
|---|---|---|
| **HIGH** | Pass `organization_id` through to audit traces | `actor_context.organization_id` exists in request schema but audit writer doesn't log it. Needed for billing |
| **HIGH** | Persist audit traces to database | Currently in-memory `OrderedDict` (gone on restart). Add `audit_traces` table + query by org/date |
| **HIGH** | Add `X-Caller-Organization` header passthrough | Let backend tag which org each request is for |
| **HIGH** | Move API keys to DB | Replace in-memory `ApiKeyStore` with `api_keys` table |
| **HIGH** | Neon migration | SQLite → PostgreSQL, add `psycopg` dep, update `database_url`, remove `check_same_thread` |
| **MEDIUM** | Clerk auth integration | Webhook sync for users/orgs, JWT validation middleware |
| **MEDIUM** | Usage tracking | `usage_records` table populated per-request, rate limiting from DB |
| **MEDIUM** | SaaS org/usage endpoints | `GET /v1/organizations/me`, `GET /v1/organizations/me/usage`, per-org key management |
| **MEDIUM** | OCR pipeline | `POST /v1/ai/prescriptions/ocr-jobs` + `GET .../{job_id}` |
| **MEDIUM** | Doctor assistant endpoint | `POST /v1/ai/doctor/assist` — currently placeholder |
| **MEDIUM** | Pharmacy assistant endpoint | `POST /v1/ai/pharmacy/assist` — currently placeholder |
| **MEDIUM** | Reminder schedule parsing | `POST /v1/ai/reminders/parse-schedule` — currently placeholder |
| **LOW** | 13 prompt templates not created | Various workflow prompts |
| **LOW** | 17 empty domain/integration scaffolds | `app/domains/*` and `app/integrations/*` — just `__init__.py` |
| **LOW** | `tests/__init__.py` | Add package init |
| **LOW** | `test_admin_api.py` | Source file missing |
| **LOW** | Type checking | No mypy/pyright in dev deps |
