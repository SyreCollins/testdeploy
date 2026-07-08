# zam-ai-core-api — Handoff

## Project
Python 3.11+ FastAPI medical RAG backend for Zamda Health. Core rule: no LLM response from model internal knowledge, must be grounded in retrieved evidence.

---

## State (130 tests, 0 lint errors)

### ✅ Completed

| Area | Details |
|---|---|
| **Tier 1 — Foundation** | Health endpoints, API key middleware (validate only, no CRUD), RAG ingestion, `.env` configured |
| **Tier 2 — Endpoints** | 7 AI workflows with full stack (schema → prompt template → manager → orchestrator → composer → route): `medical-qa`, `interactions/check`, `drug-info`, `symptom-guidance`, `contraindications/check`, `dosage/verify`, `prescriptions/explain` |
| **Tier 2 — Modules** | Citation Engine (`app/ai/citation/`), Grounding Verifier (`app/ai/grounding/`), Audit Trace Writer (`app/ai/audit/`) |
| **Tier 3 — Safety** | Safety engine (`app/ai/safety/`) with 4 rule checks (emergency, unsafe request, prompt injection, retrieval required, high risk). Prompt injection detection covers 18 patterns. |
| **Tests** | 11 test files, 130 tests covering: health, ingestion, orchestration, composers, parsers, citation, grounding, audit, confidence scoring, safety engine (45 tests including injection) |
| **Prompt templates** | 13 `.md` files (6 base + 7 workflow), all fixed with correct YAML frontmatter (`---`) |

### ❌ Remaining Gaps

| Priority | Area | What to do |
|---|---|---|
| **HIGH** | API key management | Build `app/api/keys/` with routes, schema, service layer for create/rotate/revoke |
| **HIGH** | Gateway tests | Write tests for `app/ai/gateway/claude.py`, `gemini.py`, `factory.py` |
| **MEDIUM** | End-to-end tests | Route-level integration tests using FastAPI `TestClient` for all 7 AI endpoints |
| **MEDIUM** | Missing workflow tests | `test_medical_qa`, `test_interaction_check`, `test_drug_info`, `test_symptom_guidance` — no dedicated tests yet |
| **LOW** | `tests/__init__.py` | Add package init for test imports |
| **LOW** | `test_admin_api.py` | Source file missing (only `__pycache__` remains) — recover or recreate |
| **LOW** | CI/CD | No `.github/workflows/`, no coverage config, no pre-commit |
| **LOW** | Type checking | No mypy/pyright in dev deps or config |

### Notes
- Routes live at `app/api/routes/` (not `app/api/v1/ai/`) and are prefixed `/v1` via `app/main.py`
- Ingestion is embedded in `app/rag/service.py` (not standalone `app/ingest/`)
- 0 TODO/FIXME/HACK/XXX comments in codebase
