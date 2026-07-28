# zam-ai-core-api — Handoff

## Project
Python 3.11+ FastAPI medical RAG backend for Zamda Health. Core rule: no LLM response from model internal knowledge, must be grounded in retrieved evidence (except `interaction_check` which can use LLM knowledge + disclaimer).

---

## State (~281 tests pass, 0 lint errors)

### ✅ Completed (this session — 2026-07-28)

| Area | Details |
|---|---|
| **TS types synced with ENDPOINTS.ts** | Created missing request/response types for all 40 endpoint keys — OCR, reminders, doctor assist, pharmacy assist, auth webhook, organizations, projects (CRUD + API key mgmt), admin (keys, evals, orgs, users, audit, usage). 4 new `.ts` files, barrel export updated. |
| **Clerk JWT org auth path fixed** | `_get_org()` in `organizations.py` now falls back to `request.state.organization_id` (set by ClerkAuthMiddleware from JWT's `org_id` claim), so Clerk-authenticated users can hit org routes. |
| **Middleware ordering bug fixed** | `InternalApiKeyMiddleware` was rejecting Clerk JWT requests before `ClerkAuthMiddleware` could validate them — it checked `clerk_user_id` on state that hadn't been set yet. Now simply passes through when no `x-zam-ai-key` is present, letting the JWT flow work end-to-end. |
| **`X-Caller-Organization` header passthrough** | Admin keys can now override their org context via `X-Caller-Organization` header. Useful for superadmin keys acting on behalf of any org. `InternalApiKeyMiddleware` also sets `request.state.organization_id` for consistency. |
| **Admin key creation accepts `organization_id`** | `CreateApiKeyRequest.organization_id` is now **required** on `POST /v1/admin/keys` — every key must be tied to an org. |
| **Bootstrap keys tied to org** | New `ZAM_AI_BOOTSTRAP_ORGANIZATION_ID` env var. Bootstrap keys (`ZAM_AI_INTERNAL_API_KEYS`) now get `organization_id` set from this var. |

### ✅ Completed (this session — 2026-07-27)

| Area | Details |
|---|---|
| **Render deploy & testing** | Deployed to `testdeploy-pyb7.onrender.com`. Neon DB connected via `postgresql+psycopg://`. Fixed DB URL scheme (`postgresql://` → `postgresql+psycopg://` for psycopg v3). Installed `psycopg[binary]` in venv. Added `WEB_CONCURRENCY=1` for Render free tier. |
| **CI lint fixes** | Removed unused `NullPool` import in `engine.py` and `registry.py`. Fixed import ordering in `admin.py` (starlette grouped with third-party). Fixed E402 in `service.py` (logger placed between import blocks). |
| **Bootstrap key hash mismatch** | `bootstrap_static_keys` only checked `label == "bootstrap"` — if a key from a previous deployment had a different value, it was never replaced. Now compares hash sets: deletes stale bootstrap keys and recreates with current env var value. |
| **Clerk webhook signature verification** | Two bugs fixed: (1) Svix signatures are base64-encoded, code was using `hexdigest()` — changed to `base64.b64encode(hmac.digest())`. (2) Svix secret is base64-encoded after `whsec_` prefix — now strips prefix and `base64.b64decode`s before using as HMAC key. |
| **Webhook `user.created` foreign key error** | Hardcoded `organization_id=1` in `user.created` handler, but no org with id 1 might exist. Now looks up first org in DB; if none exists, auto-creates a "Default Organization" before inserting the user. |
| **Clerk webhook tested** | All events (`organization.created`, `organization_membership.created`) processed cleanly. Org `testorg` (clerk id: `org_3H6OlY0Ed2JTKlw9FseJzCH2YZn`) created in Neon with id=2. |

### ✅ Completed (this session — 2026-07-24)

| Area | Details |
|---|---|
| **`_org_id()` fallback for internal API keys** | `_org_id()` in `app/api/routes/ai.py` only read `request.state.organization_id` (set by ClerkAuthMiddleware). Internal API key requests set `request.state.org_id` instead — so `organization_id` was never passed to audit traces for internal-key-authed requests. Now falls back to `org_id` matching the `UsageTracker` pattern. |
| **Superadmin — ApiKey `is_admin` flag** | Added `is_admin: bool = False` to `ApiKey` model. Bootstrap keys auto-tagged `is_admin=True`. All CRUD methods (`create_key`, `validate_key`, `get_key`, `list_keys`, `rotate_key`) propagate `is_admin` in their return dicts. |
| **Superadmin — middleware `is_admin` flag** | `InternalApiKeyMiddleware` now sets `request.state.is_admin` from the validated key entry, enabling admin routes to check auth. |
| **Superadmin — admin routes** | New `app/api/routes/admin.py` — routes under `/v1/admin/` with `_require_admin` guard. `GET /v1/admin/orgs` — all orgs with member/project counts. `GET /v1/admin/orgs/{id}` — single org detail. `GET /v1/admin/orgs/{id}/users` and `/projects` — org-scoped lists. `GET /v1/admin/users?org_id=` — all users. `GET /v1/admin/audit/traces` and `/{trace_id}` — cross-org audit. `GET /v1/admin/usage?org_id=&from=&to=` — aggregated usage across orgs. |
| **Neon migration prep** | Added `pool_pre_ping=True` for Postgres connections in `app/db/engine.py` and `app/rag/registry.py`. Updated `.env.example` with `ZAM_AI_DATABASE_URL` (Neon) and Clerk credentials as commented-out templates. `psycopg[binary]` already in deps. When ready: fill in `.env` values, remove `check_same_thread`, migrate data. |

### ✅ Completed (this session — 2026-07-23)

| Area | Details |
|---|---|
| **Phase 4 — Clerk auth, orgs, projects, API key CRUD** | New `app/api/routes/auth.py` — webhook handler for Clerk user/org sync (HMAC SHA-256 verified). New `app/api/routes/organizations.py` — org CRUD, project CRUD, org-scoped API key CRUD (create, list, rotate, revoke), project-scoped API key CRUD. New `app/core/middleware/auth.py` — `ClerkAuthMiddleware` validates Bearer JWT against Clerk JWKS, sets `clerk_user_id`, `organization_id` on state; skips if `api_key_entry` already present (internal key fallback). New `app/db/models/platform.py` — `Organization` (plan-based tiers), `Project`, `ApiKey` (DB-backed with SHA-256 hashing), `User` tables. DB-backed `ApiKeyStore` replaces in-memory store; `bootstrap_static_keys` seeds from `ZAM_AI_INTERNAL_API_KEYS`. `InternalApiKeyMiddleware` re‑ordered as outermost middleware so internal key check runs first, letting `ClerkAuth` skip JWT when `api_key_entry` is set. |
| **Phase 5 — Rate limiting, usage tracking** | New `app/core/middleware/rate_limit.py` — plan-based rate limiting via `Settings.get_plan_rate_limit()`. New `app/core/middleware/usage_tracker.py` — `UsageTracker` records per-request `UsageRecord` rows (org, api_key, endpoint, prompt/completion tokens). Rate limit window moved to in-memory `_rate_cache` dict (DB-backed columns removed from model to avoid schema drift with `checkfirst=True`). |
| **Phase 4–5 test suite** | `tests/test_phase4.py` — webhook auth, org creation, project CRUD, org/project-scoped API key CRUD, audit exposure. `tests/test_phase5.py` — rate limit exceeding, per-key independence, pro-plan higher limits, usage record persistence. All 31 phase4+phase5 tests pass. |
| **Lint sweep** | Fixed all 27 ruff violations: F401 unused imports (engine.get_engine, get_settings, unused imports across 6 files), E501 line length in organizations.py, SIM114 `match` bare-name capture pattern in config.py, unused `resp` in test_phase5.py. |
| **Middleware ordering fix** | `Starlette.add_middleware` wraps outward — last added = outermost = runs first. Re‑ordered so `InternalApiKeyMiddleware` is outermost (runs before `ClerkAuth`), enabling internal-key-first auth. Fixed double‑prefix bug (`/v1/v1/auth/webhook` and `/v1/v1/organizations/me`) by removing redundant `prefix="/v1"` from `include_router` calls for routers that already self‑prefix. |
| **State attribute alignment** | `_get_org` in `organizations.py` was checking `request.state.organization_id` but middleware set `request.state.org_id`. Standardised all 12 references to `org_id`. `validate_key` was returning `org_id: getattr(entry, 'org_id', None)` — model field is `organization_id`. `UsageTracker` checked `organization_id`, now falls back to `org_id`. |
| **DB schema drift fixed** | `rate_limit_window`/`rate_limit_count` columns removed from `ApiKey` model. Rate limit tracking moved to in-memory `ApiKeyStore._rate_cache` dict. `SQLModel.create_all(checkfirst=True)` does not alter existing tables, so adding DB columns was silently ignored — the in-memory approach avoids the problem entirely. |

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

### ✅ Completed (prior sessions)

| Area | Details |
|---|---|
| **18 endpoint markdown docs** | `docs/endpoints/` — one `.md` per endpoint (13 built + 5 planned). Full request/response JSON, field tables, safety rules, code examples in 6 languages |
| **Tier 1 — Foundation** | Health endpoints, API key middleware, RAG ingestion, `.env` configured |
| **Tier 2 — Endpoints** | 7 AI workflows with full stack: `medical-qa`, `interactions/check`, `drug-info`, `symptom-guidance`, `contraindications/check`, `dosage/verify`, `prescriptions/explain` |
| **Tier 2 — Modules** | Citation Engine, Grounding Verifier, Audit Trace Writer |
| **Tier 3 — Safety** | Safety engine with 4 rule checks (emergency, unsafe request, prompt injection, retrieval required, high risk). 45 tests |
| **Prompt templates** | 13 `.md` files (6 base + 7 workflow) |
| **API key management** | CRUD endpoints for API keys — SHA-256 hashed, in-memory store (legacy, replaced by DB store) |
| **Rate limiting middleware** | 60 req/60s per key, docs/health exempt (legacy, replaced by plan-based) |
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
- SaaS model (ADR 6): Partners route through main backend. Zam AI called with single internal key. New plan adds direct partner keys as second tier.
- **Middleware ordering**: Starlette `add_middleware` wraps outward — last added runs first. `InternalApiKeyMiddleware` passes through when no `x-zam-ai-key` is present, letting `ClerkAuthMiddleware` handle JWT. Current order (outermost → innermost): RequestLogging → RequestId → UsageTracker → InternalApiKey → RateLimit → ClerkAuth → Route.
- **Auth flow**: Internal API key → `InternalApiKeyMiddleware` validates, sets `org_id` + `organization_id` + `is_admin`. Clerk JWT → passes through `InternalApiKeyMiddleware`, validated by `ClerkAuthMiddleware` which sets `organization_id` from JWT `org_id` claim. Both paths ultimately set `request.state.organization_id`.
- **Every key tied to an org**: Bootstrap keys use `ZAM_AI_BOOTSTRAP_ORGANIZATION_ID`. Admin key creation requires `organization_id`. Org-scoped key creation infers org from auth context. Ensure the org exists in DB before bootstrapping on PostgreSQL (FK constraint).
- **`X-Caller-Organization` header**: Admin keys can override their org per-request via this header. Useful for superadmin acting on behalf of different orgs.
- **DB schema drift on SQLite**: `SQLModel.metadata.create_all(checkfirst=True)` does not `ALTER TABLE` — new columns are silently ignored on existing tables. Always create tables from scratch in tests (`reset_engine()` drops all) or use explicit migrations.
- **State attribute convention**: `InternalApiKeyMiddleware` sets `request.state.org_id` and `request.state.organization_id`; `ClerkAuthMiddleware` sets `request.state.organization_id`. Route helpers should fall back: `getattr(request.state, "org_id", None) or getattr(request.state, "organization_id", None)` (see `_org_id()` in `ai.py`, `_get_org()` in `organizations.py`, and `UsageTracker`).
- **Rate limit persistence**: Rate limit windows are ephemeral (in-memory `_rate_cache` dict). Lost on restart — acceptable for v1, consider Redis for production.

### ❌ Remaining Gaps

| Priority | Area | What to do |
|---|---|---|
| **MEDIUM** | OCR pipeline | `POST /v1/ai/prescriptions/ocr-jobs` + `GET .../{job_id}` — completely absent, no code at all |
| **MEDIUM** | Doctor assistant endpoint | `POST /v1/ai/doctor/assist` — stub returns "not implemented" |
| **MEDIUM** | Pharmacy assistant endpoint | `POST /v1/ai/pharmacy/assist` — stub returns "not implemented" |
| **MEDIUM** | Reminder schedule parsing | `POST /v1/ai/reminders/parse-schedule` — stub returns "not implemented" |
| **LOW** | 13 prompt templates not created | Various workflow prompts |
| **LOW** | 17 empty domain/integration scaffolds | `app/domains/*` and `app/integrations/*` — just `__init__.py` |
| **LOW** | `tests/__init__.py` | Add package init |
| **LOW** | `test_admin_api.py` | Source file missing |
| **LOW** | Type checking | No mypy/pyright in dev deps |
