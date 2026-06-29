# Zam AI Decision Log

## 1. Purpose

This document records architectural and product engineering decisions for Zam AI.

Every significant decision should include:

- Problem.
- Alternatives.
- Chosen solution.
- Reasoning.
- Tradeoffs.
- Future implications.

The decision log should be updated continuously as the platform evolves.

## Decision 001: Build Documentation Before Code

Date: 2026-06-29

Status: Accepted

### Problem

Zam AI is a medical AI platform with high safety, compliance, retrieval,
evaluation, and operational requirements. Starting with code before defining the
architecture would create hidden assumptions and unsafe shortcuts.

### Alternatives

- Start coding the FastAPI service immediately.
- Build a proof of concept chatbot first.
- Create full engineering documentation before implementation.

### Chosen Solution

Create the engineering documentation set before implementation begins.

### Reasoning

Medical AI requires clarity around source grounding, refusal behavior, audit,
evaluation, and service boundaries. Documentation provides a shared operating
model for the backend, AI, product, clinical, and compliance teams.

### Tradeoffs

- Slower initial visible development.
- Better long-term safety and maintainability.

### Future Implications

Implementation should follow the documented architecture unless a decision
record updates the design.

## Decision 002: Zam AI Is an Internal AI Service

Date: 2026-06-29

Status: Accepted

### Problem

The system needs clear ownership between the main backend and Zam AI. Earlier
assumptions incorrectly implied Zam AI might own the primary database and user
auth.

### Alternatives

- Zam AI owns user auth and application database.
- Zam AI directly reads backend database tables.
- Main backend owns auth/database and calls Zam AI through internal APIs.

### Chosen Solution

The main backend owns user authentication, authorization, application database,
sessions, and product-facing APIs. Zam AI is an internal service called by the
backend using an internal API key.

### Reasoning

This keeps user data ownership clear and avoids duplicating backend
responsibilities. Zam AI can focus on AI orchestration, retrieval, safety,
citations, audit traces, and evaluation.

### Tradeoffs

- AI workflows depend on backend-supplied context.
- Integration contracts must be well designed.
- Zam AI cannot independently fetch missing context without a future decision.

### Future Implications

Any direct database access by Zam AI requires a new architecture decision.

## Decision 003: Defer Full Application Database Design

Date: 2026-06-29

Status: Accepted

### Problem

The original documentation plan requested a full database design for patients,
doctors, pharmacies, prescriptions, reminders, and other application entities.
The main backend engineer owns that database design.

### Alternatives

- Write the full database design anyway.
- Create a limited AI metadata database design.
- Defer database design until backend ownership is clarified.

### Chosen Solution

Defer `docs/05_DATABASE_DESIGN.md` for now. If created later, it should focus
only on AI-owned metadata, retrieval storage, evaluation records, audit traces,
and backend-to-AI data contracts.

### Reasoning

Writing the application database design from the AI side would create conflicts
with backend ownership and could mislead future engineers.

### Tradeoffs

- The documentation set intentionally skips one originally requested file.
- AI-owned storage details remain open until implementation planning.

### Future Implications

Backend and AI teams should jointly define context contracts before
implementation.

## Decision 004: Use Retrieval-Required Medical Generation

Date: 2026-06-29

Status: Accepted

### Problem

LLMs can produce fluent but unsupported medical content. In healthcare, this can
cause harm.

### Alternatives

- Let the model answer from its internal knowledge.
- Ask the model to cite sources but do not enforce retrieval.
- Require retrieved evidence or approved tools for medical answers.

### Chosen Solution

Medical answers require verified retrieved evidence, approved structured tools,
or authorized structured context.

### Reasoning

This is the core safety mechanism for Zam AI.

### Tradeoffs

- Some questions will be refused when sources are unavailable.
- Retrieval quality becomes product-critical infrastructure.
- More engineering work is required before user-facing launch.

### Future Implications

RAG, evaluation, source licensing, and citation systems must be built before
full medical Q&A launch.

## Decision 005: Start With Modular Monolith Plus Workers

Date: 2026-06-29

Status: Accepted

### Problem

Zam AI needs multiple components: API, orchestration, retrieval, tools, workers,
evaluation, and audit. The team needs a scalable design without premature
distributed system complexity.

### Alternatives

- One unstructured monolith.
- Full microservices from day one.
- Modular FastAPI service plus background workers.

### Chosen Solution

Start with a modular FastAPI service and separate background workers.

### Reasoning

This supports fast development, simpler tracing, and clear module boundaries.
Components can later be extracted when contracts stabilize.

### Tradeoffs

- Requires discipline to prevent module coupling.
- Some workloads may later need extraction.

### Future Implications

Maintain clear boundaries around RAG, AI orchestration, tools, safety, and
evaluation from the start.

## Decision 006: Use Provider Abstractions

Date: 2026-06-29

Status: Accepted

### Problem

The platform may use different providers for LLMs, embeddings, OCR, vector
search, and monitoring. Tight coupling would create vendor lock-in and make
testing harder.

### Alternatives

- Call provider SDKs directly from business logic.
- Build provider abstractions around external services.

### Chosen Solution

Use provider adapters and internal interfaces.

### Reasoning

Provider abstraction supports testing, fallback, evaluation, and future
migration.

### Tradeoffs

- More initial interface design.
- Some provider-specific capabilities may need careful normalization.

### Future Implications

Business logic should not import provider SDKs directly.

## Decision 007: Treat Evaluation as Release Infrastructure

Date: 2026-06-29

Status: Accepted

### Problem

Medical AI behavior can regress when prompts, models, retrieval, sources, or
tools change.

### Alternatives

- Rely on manual testing.
- Add evaluation after launch.
- Build evaluation gates before production release.

### Chosen Solution

Build evaluation datasets, metrics, and release gates before launch.

### Reasoning

Safety cannot be managed through demos and anecdotes. Evaluation is required to
measure groundedness, citation accuracy, emergency escalation, refusal behavior,
and prompt injection resistance.

### Tradeoffs

- Slower release cycles.
- Requires clinical review and dataset maintenance.

### Future Implications

AI behavior changes should include evaluation results in pull requests.

## Decision 008: Keep Partner Access Behind Main Backend

Date: 2026-06-29

Status: Accepted

### Problem

Third-party companies will eventually use Zam AI capabilities. Direct partner
access to the AI service would expand auth, billing, abuse, and compliance
surface area.

### Alternatives

- Partners call Zam AI directly.
- Partners call the main backend, which mediates AI access.

### Chosen Solution

Partners should access AI capabilities through the main backend.

### Reasoning

The backend owns partner identity, billing, access control, usage limits, and
product contracts.

### Tradeoffs

- Backend must expose partner-facing capability APIs.
- Zam AI remains internal and less directly reusable.

### Future Implications

Direct partner access would require a new decision and stronger gateway,
auth, billing, and abuse controls.

## Decision 009: Use Cloud Run as Target Deployment

Date: 2026-06-29

Status: Proposed

### Problem

Zam AI needs a managed deployment target for the FastAPI service and workers.

### Alternatives

- Google Cloud Run.
- Kubernetes.
- Compute Engine.
- Serverless functions.

### Chosen Solution

Use Google Cloud Run as the target deployment architecture unless later
constraints require otherwise.

### Reasoning

Cloud Run fits containerized FastAPI services, supports autoscaling, revision
rollouts, and keeps operations manageable for an early team.

### Tradeoffs

- Less control than Kubernetes.
- Cold starts may need tuning.
- Long-running workloads may need Cloud Run jobs or separate workers.

### Future Implications

Deployment design should keep API and worker runtimes containerized and
environment-configurable.

## Decision 010: Do Not Finalize Vector Database Before Benchmarks

Date: 2026-06-29

Status: Accepted

### Problem

The vector database choice affects retrieval quality, cost, metadata filtering,
scalability, and operations.

### Alternatives

- Choose `pgvector` immediately.
- Choose a managed vector database immediately.
- Evaluate options against Zam AI retrieval needs.

### Chosen Solution

Do not finalize the vector database until the RAG benchmark and operational
requirements are clearer.

### Reasoning

Medical retrieval has exact matching, metadata filtering, source versioning, and
latency needs. The decision should be evidence-based.

### Tradeoffs

- Leaves one implementation decision open.
- Requires benchmark work before final build.

### Future Implications

`pgvector`, Qdrant, Weaviate, Pinecone, and Vertex AI Vector Search remain
candidates.

## Change Log

| Date | Change | Status |
| --- | --- | --- |
| 2026-06-29 | Initial decision log created. | Draft |
