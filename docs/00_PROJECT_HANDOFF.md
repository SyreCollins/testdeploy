# Zam AI Project Handoff

**Operational source of truth** — update whenever the platform design, implementation status, risks, or decisions change.


Zam AI is a medical intelligence platform for patients, doctors, pharmacies, and third-party health companies. The highest priority is preventing unsafe, ungrounded, or hallucinated medical responses.

> **Core rule:** No medical response from LLM internal knowledge. Every answer must be grounded in verified medical sources through retrieval, structured clinical logic, or approved tools.

---

## 1. Status at a Glance

| Area | Status |
| --- | --- |
| **Documentation** | ✅ All 12 docs completed (DB design deferred — backend-owned) |
| **Phase 0 — Scaffold** | ✅ Complete (API, middleware, logging, Docker, CI, lint, tests passing) |
| **Phase 1 — Knowledge Platform** | ✅ Complete (ingestion + retrieval + 19 tests passing) |
| **Phase 2+ — AI Core & User Workflows** | 🔄 In progress (Model Gateway done) |

---

## 2. Current Project State

### 2.1 Repository State

The repo has both the full architecture documentation set and a working Phase 0 scaffold.

**Docs (12 of 13 planned):**
- `README.md` — project landing page
- `docs/00_PROJECT_HANDOFF.md` — this file
- `docs/01_PRODUCT_REQUIREMENTS.md` through `docs/12_DECISION_LOG.md`
- `docs/05_DATABASE_DESIGN.md` — **deferred** (backend owns the application DB)

**Code:**
- `app/main.py` — FastAPI application factory
- `app/core/` — config, errors, logging, middleware (API key, request ID)
- `app/api/routes/health.py` — `GET /v1/health` and `GET /v1/ready`
- `app/api/routes/admin.py` — `POST /v1/admin/sources`, `POST /v1/admin/documents/ingest`
- `app/api/routes/retrieval.py` — `POST /v1/retrieval/search`
- `app/api/schemas/retrieval.py` — request/response models for search
- `app/api/schemas/admin.py` — request/response models for admin endpoints
- `app/rag/` — parsers (PDF, TXT, JSON, CSV, XLSX), normalizer, chunker, embeddings, vector store, registry (SQLModel), schemas (trust_tier, drug_entity_id), service.py (ingestion orchestrator)
- `app/ai/gateway/` — Model Gateway (base ABC + Claude + Gemini + Mock providers + factory)
- `app/ai/prompts/` — Prompt Manager (registry + builder + manager; loads YAML-frontmatter templates from `prompts/`)
- `app/ai/safety/` — Safety Policy Engine (risk classification + rules + evaluator)
- `prompts/` — 7 prompt template files (base components + medication info workflow + JSON schema)
- `app/ai/`, `app/domains/`, `app/integrations/`, `app/evaluation/`, `app/workers/` — empty scaffolds
- `tests/test_health.py` — 3 health endpoint tests
- `tests/test_parsers.py` — 5 parser tests (CSV, XLSX, auto-selection, encoding)
- `tests/test_ingestion.py` — 5 service tests (ingest, dedup, search, filters, entity ID)
- `tests/test_admin_api.py` — 6 API tests (register, ingest, auth, search, filters, errors)
- `.github/workflows/ci.yml` — lint + test + Docker build
- `Dockerfile`, `pyproject.toml`, `.env.example`

### 2.2 Engineering State

```
Phase 0: ████████████████████ 100%
Phase 1: ████████████████████ 100%  (All 7 steps complete — 19 tests, 0 lint errors)
Phase 2: ██████████░░░░░░░░░░  45%  (Model Gateway + Safety Engine + Medical QA + Prompt Manager + Symptom Guidance done — 6 of 11 items remaining)
Phase 3+: ░░░░░░░░░░░░░░░░░░░░   0%
```

**Stack in place:**
- Python 3.11+, FastAPI, Pydantic, SQLModel, uvicorn
- Ruff (lint), pytest (test)
- Docker (containerisation)
- Provider-abstraction patterns for parsers, embeddings, vector stores
- Embedding providers backed by **LlamaIndex** (`llama-index-embeddings-*`)
- Vector stores backed by **LlamaIndex** (`llama-index-vector-stores-*`)

**Stack decisions made:**
- Embedding providers: ✅ **Voyage** (`voyage-3`, 1024-dim), **Jina** (`jina-embeddings-v3`, 1024-dim), **Gemini** (`embedding-001`, 768-dim) — all via LlamaIndex
- Vector database: ✅ **Pinecone** (serverless) via LlamaIndex
- Provider selection: ✅ Config-driven (`EMBEDDING_PROVIDER`, `VECTOR_STORE`) with auto-detect fallback

**Stack decisions made:**
- LLM providers: ✅ **Claude** (default, `claude-sonnet-4-20250514`), **Gemini** (fallback, `gemini-2.0-flash`) — via Model Gateway abstraction

**Stack decisions pending:**
- OCR provider
- Queue technology (RQ / Celery / Cloud Tasks)
- Object storage

### 2.3 Product State

Zam AI is planned for four audiences via internal APIs called by the main backend:

| Audience | Capabilities |
| --- | --- |
| **Patients** | Symptom triage, drug info, interaction/contraindication checks, prescription OCR & explanation, reminders, health recommendations |
| **Doctors** | Medication review, patient summaries, evidence-linked decision support, education draft generation |
| **Pharmacies** | Medication intelligence, substitutions, interaction/contraindication warnings, inventory-aware guidance |
| **Partners** | Mediated AI capabilities through the main backend (drug info, OCR, interactions) |

---

## 3. Milestone: Phase 0 Setup

**Status: ✅ Complete**

### Deliverables

| Item | Status |
| --- | --- |
| FastAPI project scaffold | ✅ |
| Configuration system (pydantic-settings + .env) | ✅ |
| Internal API-key middleware | ✅ |
| Request ID middleware (with latency logging) | ✅ |
| Structured JSON logging | ✅ |
| Common error handling (ApiError + global handlers) | ✅ |
| `GET /v1/health` endpoint | ✅ |
| `GET /v1/ready` endpoint | ✅ |
| Dockerfile | ✅ |
| ruff linting (120 char line length) | ✅ |
| pytest baseline tests (3 passing) | ✅ |
| GitHub Actions CI (lint + test + Docker build) | ✅ |

### What's Included Beyond Pure Scaffold

While delivering Phase 0, foundational RAG building blocks were also implemented as reusable libraries. They are **not yet wired into the API** but are ready for Phase 1:

- Parsers: `BaseParser`, `PdfParser`, `TxtParser`, `JsonParser` (with drug structure extraction)
- `Normalizer`: whitespace/dosage-unit cleaning, brand→generic resolution
- `Chunker`: section-aware chunking with overlap and sentence-boundary detection
- `EmbeddingProvider` ABC + `MockEmbeddingProvider` (deterministic pseudo-random vectors)
- `VectorStore` ABC + `MemoryVectorStore` (cosine similarity + hybrid keyword boost)
- `RagRegistry` (SQLModel + SQLite): CRUD for sources, documents, chunks with dedup
- `MedicalSource`, `SourceDocument`, `DocumentChunk`, `Citation` schemas

---

## 4. Upcoming Work

### Phase 1 Complete ✅

The medical knowledge platform is built and wired into the API:
- 4 source files ingested (Nigeria EML PDF, Medicine Details CSV, NAFDAC CSV, ATC XLSX)
- Source registration + document ingestion via `POST /v1/admin/*`
- Hybrid retrieval (cosine similarity + keyword boost) via `POST /v1/retrieval/search`
- Trust tier filtering, chunk type filtering, drug entity ID resolution
- 19 tests, 0 lint errors

### Phase 2 — AI Core

Status: 🔄 In progress

| # | Component | Status |
|---|-----------|--------|
| 1 | **Conversation orchestrator** — intent routing, state management, response composition | ❌ Not started |
| 2 | **Intent classifier** — detect medical intent vs general vs emergency | ❌ Not started |
| 3 | **Risk classifier** — flag high-risk queries (pregnancy, paediatric, interactions) | ❌ Not started |
| 4 | **Safety policy engine** — enforce retrieval-required, refusal, escalation rules | ✅ Complete |
| 5 | **Context builder** — assemble retrieved chunks + patient context into prompt context | ❌ Not started |
| 6 | **Prompt manager** — versioned prompt templates with model-specific overrides | ✅ Complete |
| 7 | **Model gateway** — abstract LLM provider with retry, fallback, logging | ✅ Complete |
| 8 | **Citation engine** — format citations from retrieved chunks | ❌ Not started |
| 9 | **Grounding verifier** — verify response aligns with retrieved evidence | ❌ Not started |
| 10 | **Confidence scorer** — score answer confidence from grounding + source tier | ❌ Not started |
| 11 | **Audit trace writer** — log every request, response, model call, and decision | ❌ Not started |

### Prerequisites for Phase 2
- ✅ LLM provider decision (Claude default, Gemini fallback)
- Prompt policy document
- AI metadata storage decision
- First golden evaluation dataset
- Pinecone index provisioned and Voyage API key set in environment

### Recommended Build Order

| Phase | Focus | Depends On |
| --- | --- | --- |
| **1** | Medical knowledge platform — ingestion, retrieval, citations, grounding | Source licensing, vector DB, embedding provider |
| **2** | AI core — orchestrator, safety engine, model gateway, prompts | Phase 1 |
| **3** | Patient MVP — medical Q&A, drug info, symptom guidance | Phase 1 + 2 |
| **4** | Prescription intelligence — OCR, interactions, dosage check | Phase 1 + 2 |
| **5** | Personalisation & reminders | Phase 3 + 4 |
| **6** | Doctor & pharmacy workflows | Phase 3 + 4 |
| **7** | Advanced AI — voice, multilingual, predictive | Phase 5 + 6 |
| **8** | Public SaaS platform | Everything above |

---

## 5. Architecture Decisions

### ADR 1: Modular Monolith + Workers
**Decision:** Start with a modular FastAPI service and separate background workers, not microservices.
**Why:** Faster development, easier tracing, clear module boundaries. Modules can be extracted later when contracts stabilise.

### ADR 2: Retrieval-Required Medical Answers
**Decision:** Every medical answer requires retrieved evidence or approved tools.
**Why:** Core safety mechanism. No fabricated clinical facts.

### ADR 3: Provider Abstraction
**Decision:** Abstract LLMs, embeddings, OCR, and vector stores behind internal interfaces.
**Why:** Avoid vendor lock-in, support testing and fallback.

### ADR 4: Evaluation as Infrastructure
**Decision:** Build evaluation datasets and release gates before production launch.
**Why:** Medical AI cannot be managed through manual testing alone.

### ADR 5: Separate Medical Knowledge from User Data
**Decision:** Canonical medical references, operational data (pharmacy inventory), and patient context are stored separately.
**Why:** Different trust, freshness, privacy, and retention requirements.

### ADR 6: Partners Behind Main Backend
**Decision:** Partners access AI capabilities through the main backend, not directly.
**Why:** Backend owns partner identity, billing, access control.

---

## 6. Current Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| **Medical hallucination** | Harm from fabricated answers | Retrieval-required policy, grounding checks, refusal thresholds |
| **Source licensing delays** | Can't start ingestion | Track license status per source; start with any approved source |
| **Clinical scope creep** | Drift into ungoverned diagnosis | Clear PRD scope, triage/escalation policies, disclaimers |
| **Privacy compliance** | NDPA exposure | Privacy-by-design, encryption, consent tracking, audit logs |
| **Evaluation blind spots** | Strong demos, weak real-world perf | Nigeria-specific datasets, misspellings, multilingual, adversarial tests |
| **Operational reliability** | Provider failures | Provider abstraction, retries, circuit breakers, graceful degradation |

---

## 7. Known Blockers (Pre-Production)

- [ ] Licensing for NAFDAC, EMDEX, BNF, MIMS, WHO ATC, Nigeria Essential Medicines List
- [ ] Initial country scope: Nigeria only or multi-country?
- [ ] Clinical governance model: who reviews safety policy and evaluation sets?
- [ ] EHR integration: store records directly or integrate with external systems?
- [ ] Regulatory requirements beyond NDPA
- [ ] Symptom checking scope: educational triage vs diagnosis support?
- [ ] Launch surface: mobile, web, WhatsApp, API, or all?
- [ ] Budget for LLMs, OCR, vector DB, monitoring, cloud infra

---

## 8. Technical Debt to Avoid

- Don't ship chat before retrieval and evaluation are reliable
- Don't treat source ingestion as a one-time import — version everything
- Don't mix patient data with canonical medical knowledge
- Don't let prompts become undocumented business logic
- Don't add public APIs before rate limits, audit, and usage tracking
- Don't add OCR without human review pathways

---

## 9. Infrastructure Direction

| Component | Target | Status |
| --- | --- | --- |
| API runtime | Google Cloud Run | Dockerfile ready, CI building |
| Background workers | Cloud Run jobs or separate service | Not implemented |
| Cache / queue / rate limits | Redis | Configured in design, not deployed |
| Object storage | Cloud Storage | Not implemented |
| Secrets | Secret Manager | Not implemented |
| Database (AI metadata) | Postgres or backend-shared schema | TBD with backend team |
| Vector store | pgvector / Qdrant / Pinecone (TBD) | MemoryVectorStore for local dev |

---

## 10. API Direction

Zam AI exposes internal HTTP endpoints consumed by the main backend:

- **Implemented:** `GET /v1/health`, `GET /v1/ready`
- **Built:** `POST /v1/ai/medical-qa`, `POST /v1/ai/symptom-guidance`, `POST /v1/ai/drug-info`, `POST /v1/ai/interactions/check`
- **Specified (not built):** `/v1/ai/contraindications/check`, `/v1/ai/dosage/verify`, `/v1/ai/prescriptions/ocr-jobs`, `/v1/ai/prescriptions/explain`, `/v1/ai/reminders/parse-schedule`, `/v1/ai/doctor/assist`, `/v1/ai/pharmacy/assist`, `/v1/admin/evaluations/run`

Auth: Internal API key via `X-Zam-AI-Key` header. User auth owned by the main backend.

---

## 11. AI Direction

The AI system will be a controlled reasoning layer, not a raw LLM wrapper. Required components (none built yet):

**Pre-generation:** Intent classifier → Risk classifier → Safety policy engine → Retrieval planner → Context builder → Prompt manager → Model gateway
**Post-generation:** Grounding verifier → Citation engine → Confidence scorer → Response composer → Audit logger

High-risk intents (emergency, pregnancy, paediatric, interactions, contraindications, dosage changes, self-harm) require stricter retrieval, safer language, and escalation guidance.

---

## 12. Open Questions

### Product
- First launch market? First user surface? First MVP persona?
- Educational guidance only, or clinician decision support from the start?
- What emergency escalation language is acceptable?

### Data
- Which sources are licensed today? What formats?
- What patient context will the backend provide in MVP?
- What data is the AI API allowed to store?

### Technical
- pgvector or dedicated vector DB?
- Which embedding provider for medical retrieval quality?
- Which OCR provider handles Nigerian prescriptions best?
- RQ, Celery, or Cloud Tasks for background jobs?

---

## 13. Decision History

| Date | Decision | Status |
| --- | --- | --- |
| 2026-06-29 | Architecture documentation before code | Accepted |
| 2026-06-29 | Medical hallucination prevention = highest constraint | Accepted |
| 2026-06-29 | Docs as multiple markdown files under `docs/` | Accepted |
| 2026-06-29 | Zam AI = internal service called by main backend via API key | Accepted |
| 2026-06-29 | User auth & primary DB owned by main backend | Accepted |
| 2026-06-29 | Full DB design deferred (backend-owned) | Accepted |
| 2026-06-29 | Documentation pass completed (excl. deferred DB design) | Accepted |
| 2026-06-30 | Phase 0 scaffold + RAG building blocks completed | Accepted |
| 2026-07-01 | Phase 1 complete — ingestion pipeline + retrieval API + 19 tests | Accepted |
| 2026-07-01 | Added CSV and XLSX parsers for NAFDAC, ATC, Medicine Details sources | Accepted |
| 2026-07-01 | Trust tier ranking system for cross-source conflict resolution | Accepted |
| 2026-07-01 | Shared app state pattern for services (registry, embeddings, vector store) | Accepted |
| 2026-07-02 | Voyage voyage-3 as embedding provider (replaced initial OpenAI pick) | Accepted |
| 2026-07-02 | Pinecone (serverless) as vector database | Accepted |
| 2026-07-02 | Real providers auto-selected when API keys present; mock fallback for local dev | Accepted |
| 2026-07-03 | LlamaIndex integration: embedding providers (Voyage, Jina, Gemini) and vector stores (Pinecone) use LlamaIndex under the hood | Accepted |
| 2026-07-03 | Provider factory pattern: `EMBEDDING_PROVIDER` and `VECTOR_STORE` env vars select active provider; auto-detect based on available API keys | Accepted |
| 2026-07-03 | Jina AI and Google Gemini added as embedding provider options | Accepted |
| 2026-07-03 | Qdrant added as vector store option (via direct qdrant-client SDK) | Accepted |
| 2026-07-06 | Phase 2 started — Model Gateway built (base ABC + Claude + Gemini + Mock + factory) | Accepted |
| 2026-07-06 | Claude selected as default LLM provider (`claude-sonnet-4-20250514`); Gemini as fallback (`gemini-2.0-flash`) | Accepted |
| 2026-07-06 | Safety Policy Engine built — emergency keyword detection, high-risk classification, retrieval-required policy, unsafe request refusal | Accepted |
| 2026-07-06 | `POST /v1/ai/medical-qa` endpoint built — full pipeline: safety check → RAG retrieval → LLM generation → structured response with citations | Accepted |
| 2026-07-06 | Prompt Manager built — file-based template registry (YAML frontmatter + Markdown), PromptBuilder for composable assembly, PromptManager for workflow orchestration; refactored medical-qa endpoint to use templates | Accepted |
| 2026-07-06 | Prompt templates created — 8 template files under `prompts/` (system, medical_rules, safety_rules, refusal_rules, citation_rules, output_rules, medication_info workflow, symptom_checker workflow) | Accepted |
| 2026-07-06 | `POST /v1/ai/symptom-guidance` endpoint built — safety check → LLM triage → structured response with triage level | Accepted |

---

## 14. Next Action

Review this handoff with the backend engineer and confirm the backend-to-AI integration contract:

- API key format and header conventions
- Request/response envelope design (see `docs/06_API_SPECIFICATION.md`)
- What context the backend will pass (patient fields, consent flags, role)
- Whether Zam AI gets its own metadata store
- How AI audit traces are retained
- First medical source to ingest
- First MVP AI workflow
