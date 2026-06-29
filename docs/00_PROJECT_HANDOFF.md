# Zam AI Project Handoff

## 1. Purpose

This document is the operational source of truth for the Zam AI engineering project.
It should be updated whenever the platform design, implementation status, risks, or
architectural decisions change.

Zam AI is a medical intelligence platform for patients, doctors, pharmacies, and
third-party health companies. Because the product operates in a medical context,
the highest priority is preventing unsafe, ungrounded, or hallucinated medical
responses.

The central engineering rule is:

> No medical response should ever come from an LLM's internal knowledge. Every
> medical answer must be grounded in verified medical sources through retrieval,
> structured clinical logic, or approved tools.

This rule affects every part of the platform: product requirements, data
modeling, AI orchestration, retrieval, evaluation, monitoring, API design,
security, compliance, and deployment.

## 2. Current Project State

### 2.1 Repository State

The repository is currently in the documentation and architecture planning phase.
There is not yet a production application implementation.

Current known files:

- `README.md`
- `zamai.md`
- `ZamAI.docx`
- `Zam_AI_Master_Working_Document (1).pdf`

The `zamai.md` file defines the full documentation assignment and should be
treated as the initial architecture brief.

### 2.2 Product State

Zam AI is planned as a production-grade healthcare AI platform serving four major
audiences:

- Patients
- Doctors
- Pharmacies
- Third-party health companies through public APIs

The intended capabilities include:

- Symptom checking
- Medication guidance
- Drug information
- Drug interaction checking
- Contraindication detection
- Dosage verification
- Prescription explanation
- Prescription OCR
- Medication reminders
- Personalized health recommendations
- Pharmacy intelligence
- Clinical decision support
- Predictive analytics
- Public API access

### 2.3 Engineering State

The platform has not yet been implemented. The immediate engineering priority is
to produce a complete architecture and implementation specification before code
is written.

The expected stack from the project brief is:

- Backend: FastAPI and Python
- Primary application database: owned by the main backend team and to be
  confirmed as that design matures
- User authentication and authorization: owned by the main backend team
- AI API authentication: internal API key used by the backend when calling the
  AI API
- Deployment: Google Cloud Run
- Containerization: Docker
- Cache and job coordination: Redis
- LLM providers: Claude and Gemini, with provider abstraction
- Vector search: to be selected and justified in the RAG architecture
- Embeddings: to be selected and justified in the RAG architecture
- OCR: to be selected and justified in the prescription intelligence design
- Monitoring: production-grade observability stack to be selected and justified

## 3. Current Milestone

### Milestone: Architecture Documentation Foundation

Status: Completed for the current architecture planning pass.

The current documentation set defines the product, system architecture, AI
architecture, RAG architecture, internal API contracts, security posture,
evaluation framework, deployment architecture, engineering standards, roadmap,
and decision log.

The original request included a full database design document. That document is
intentionally deferred because the main backend engineer owns the primary
application database. Zam AI should not design patient, doctor, pharmacy,
prescription, auth, reminder, or partner database tables unless ownership
changes.

Required documentation files:

- `README.md`
- `docs/00_PROJECT_HANDOFF.md`
- `docs/01_PRODUCT_REQUIREMENTS.md`
- `docs/02_SYSTEM_ARCHITECTURE.md`
- `docs/03_AI_ARCHITECTURE.md`
- `docs/04_RAG_ARCHITECTURE.md`
- `docs/05_DATABASE_DESIGN.md` - deferred; backend-owned database
- `docs/06_API_SPECIFICATION.md`
- `docs/07_SECURITY_AND_COMPLIANCE.md`
- `docs/08_AI_EVALUATION.md`
- `docs/09_DEPLOYMENT_ARCHITECTURE.md`
- `docs/10_ENGINEERING_GUIDELINES.md`
- `docs/11_ROADMAP.md`
- `docs/12_DECISION_LOG.md`

## 4. Completed Work

The following work has been completed:

- Initial project brief captured in `zamai.md`.
- Documentation structure defined.
- Safety-first product direction established.
- Initial handoff document created.
- `README.md` rewritten as the project landing page.
- `docs/01_PRODUCT_REQUIREMENTS.md` created.
- `docs/02_SYSTEM_ARCHITECTURE.md` created.
- `docs/03_AI_ARCHITECTURE.md` created.
- `docs/04_RAG_ARCHITECTURE.md` created.
- `docs/06_API_SPECIFICATION.md` created.
- `docs/07_SECURITY_AND_COMPLIANCE.md` created.
- `docs/08_AI_EVALUATION.md` created.
- `docs/09_DEPLOYMENT_ARCHITECTURE.md` created.
- `docs/10_ENGINEERING_GUIDELINES.md` created.
- `docs/11_ROADMAP.md` created.
- `docs/12_DECISION_LOG.md` created.
- Supabase/Auth/RLS assumptions removed from the documentation after the
  backend ownership boundary was clarified.
- `docs/05_DATABASE_DESIGN.md` intentionally deferred because the main backend
  owns the application database design.

## 5. In-Progress Work

The following work is currently in progress:

- Review and refinement of the architecture documentation with backend, product,
  security, and clinical stakeholders.
- Clarifying backend-to-AI data contracts.
- Confirming source licensing, model providers, vector database, OCR provider,
  and deployment details.

## 6. Upcoming Work

The next work should be:

1. Review the documentation with the backend engineer and confirm the
   backend-to-AI request/response contracts.
2. Decide whether Zam AI needs a separate AI metadata store or an approved
   backend-owned schema for traces, jobs, source metadata, and evaluations.
3. Confirm the first licensed medical source set.
4. Benchmark embedding and vector database options.
5. Select the initial OCR provider and prescription review workflow.
6. Define the first golden evaluation datasets.
7. Scaffold the FastAPI internal AI service.
8. Implement internal API-key middleware, health checks, structured logging, and
   request IDs.
9. Build the first source ingestion and retrieval prototype.

The documentation phase intentionally started with product and system context
before lower-level implementation details. The implementation phase should now
start with service boundaries, source ingestion, retrieval, evaluation, and
internal API security before user-facing AI workflows.

## 7. Architecture Decisions

This section records the current architectural direction. Detailed decision
records should later be expanded in `docs/12_DECISION_LOG.md`.

### 7.1 Use a Modular Monolith Before Microservices

Decision: Start with a modular monolith implemented in FastAPI, with clearly
separated domain modules.

Rationale:

- The product has complex safety requirements that benefit from a single,
  inspectable codebase during early development.
- A modular monolith reduces distributed system complexity while preserving
  clean service boundaries.
- Medical safety, auditability, and evaluation require consistent request
  tracing across retrieval, orchestration, tools, and response generation.
- Premature microservices would increase deployment, observability, and
  cross-service consistency risks.

Expected modules:

- Identity and access
- User profiles
- Medical knowledge ingestion
- Retrieval
- AI orchestration
- Conversation management
- Prescription intelligence
- Medication intelligence
- Reminders
- Pharmacy intelligence
- Doctor assistant
- Partner API
- Billing and usage
- Audit and compliance
- Evaluation

Future implication:

Modules that later require independent scaling can be extracted into services
after their contracts are stable.

### 7.2 Require Retrieval for Medical Answers

Decision: Medical answers must be generated only after the system retrieves
approved clinical context or invokes approved deterministic tools.

Rationale:

- LLMs can produce fluent but incorrect medical content.
- Medical source grounding is the core product safety mechanism.
- Citations, confidence scoring, and groundedness checks require traceable
  source documents.

Implication:

The AI orchestrator must refuse, redirect, or escalate when no reliable source
context is available.

### 7.3 Use Provider-Abstraction for LLMs

Decision: The application should support multiple LLM providers behind a stable
internal interface.

Rationale:

- Medical AI products should avoid being tightly coupled to one model vendor.
- Different tasks may require different model characteristics: latency, context
  length, tool calling quality, cost, multilingual performance, or reasoning
  depth.
- Provider fallback is useful for reliability.

Initial likely providers:

- Claude for high-quality medical explanation, instruction following, and
  safety-sensitive generation.
- Gemini for long-context and Google Cloud ecosystem alignment.

Implementation implication:

The internal `ModelProvider` interface should support:

- Chat completion
- Structured output
- Tool calling
- Streaming
- Safety metadata
- Token usage
- Provider latency
- Model version capture

### 7.4 Treat Evaluation as Product Infrastructure

Decision: AI evaluation must be designed before launch, not added after launch.

Rationale:

- Medical AI quality cannot be managed through anecdotal testing.
- Every model, retrieval, prompt, and source update can create regressions.
- Launch readiness requires measurable groundedness, citation accuracy,
  refusal quality, emergency escalation behavior, and clinical correctness.

Implication:

The platform needs golden datasets, automated regression tests, human review
queues, and production monitoring from the beginning.

### 7.5 Separate Medical Knowledge From User Data

Decision: Verified medical knowledge, user health records, pharmacy inventory,
and conversation data should be modeled separately.

Rationale:

- Each data category has different trust, freshness, privacy, and retention
  requirements.
- Medical source documents require versioning and citation metadata.
- Patient data requires strict consent, access control, and audit logging.
- Pharmacy inventory changes frequently and should not be treated as canonical
  clinical knowledge.

Implication:

Retrieval must be source-aware and must distinguish between:

- Canonical medical references
- Regulatory drug data
- Local formulary and inventory data
- Patient-specific context
- Conversation memory

## 8. Current Risks

### 8.1 Medical Hallucination Risk

Risk:

The system could generate a medical answer not supported by verified sources.

Mitigation:

- Retrieval-required generation policy
- Citation validation
- Groundedness scoring
- Refusal behavior when evidence is weak
- Human review for high-risk workflows
- Regression tests for unsafe answer patterns

### 8.2 Source Quality and Licensing Risk

Risk:

Medical sources such as BNF, MIMS, EMDEX, and NAFDAC may have licensing,
availability, freshness, or format constraints.

Mitigation:

- Track every source's license, owner, update cadence, and ingestion method.
- Preserve source versions.
- Store document provenance.
- Do not ingest restricted sources until licensing is confirmed.

### 8.3 Clinical Scope Creep

Risk:

The product could accidentally move from educational support into diagnosis,
treatment decisions, or emergency medical decision-making without appropriate
clinical governance.

Mitigation:

- Define medical scope clearly in the PRD.
- Add explicit triage and escalation policies.
- Require disclaimers and emergency guidance.
- Establish clinician review for clinical workflows.

### 8.4 Privacy and Compliance Risk

Risk:

The platform will process sensitive health information, personally identifiable
information, prescriptions, and possibly doctor-patient interactions.

Mitigation:

- Privacy-by-design architecture
- NDPA-aligned data governance
- Encryption at rest and in transit
- Row-level security
- Consent tracking
- Audit logging
- Role-based access control
- Data retention rules

### 8.5 Evaluation Blind Spots

Risk:

The system may appear strong in demos but fail under real-world user behavior,
local drug naming conventions, multilingual queries, incomplete prescriptions,
or adversarial prompts.

Mitigation:

- Create Nigerian healthcare-specific evaluation datasets.
- Test generic names, brand names, misspellings, abbreviations, and local
  prescription formats.
- Include low-resource and multilingual queries.
- Include prompt injection and jailbreak scenarios.

### 8.6 Operational Reliability Risk

Risk:

Cloud services, LLM providers, OCR providers, vector search, or background jobs
may fail during critical user workflows.

Mitigation:

- Provider abstraction
- Retries with idempotency keys
- Circuit breakers
- Graceful degradation
- Queue-based ingestion and OCR processing
- Status tracking for long-running workflows
- Production observability

## 9. Known Blockers

The following blockers must be resolved before production implementation:

- Confirm licensing and access terms for NAFDAC, EMDEX, BNF, MIMS, WHO ATC, and
  Nigeria Essential Medicines List.
- Confirm whether the platform will initially support only Nigeria or multiple
  countries.
- Confirm clinical governance model: who reviews medical safety policy,
  evaluation sets, and high-risk responses.
- Confirm whether Zamda Health will store patient health records directly or
  integrate with external EHR systems.
- Confirm the initial regulatory compliance requirements beyond NDPA.
- Confirm product scope for symptom checking: educational triage only versus
  diagnosis support.
- Confirm target launch surface: mobile app, web app, API, WhatsApp, or all.
- Confirm budget constraints for LLM, OCR, vector database, monitoring, and
  cloud infrastructure.

## 10. Technical Debt

There is no implementation yet, so there is no code-level technical debt.

Architecture-level debt to avoid:

- Building chat before retrieval and evaluation are ready.
- Treating medical source ingestion as a one-time import instead of a versioned
  pipeline.
- Mixing patient data with canonical medical knowledge.
- Allowing prompts to become undocumented business logic.
- Adding public APIs before rate limits, audit logs, and usage tracking exist.
- Adding OCR without a human review and correction pathway.
- Treating reminders as simple notifications without medication schedule
  semantics.

## 11. Database Status

Current status: Deferred to the main backend owner.

Expected direction:

- Treat the primary application database as backend-owned.
- Do not assume the AI API directly owns patient, doctor, pharmacy, appointment,
  or authentication tables.
- Define explicit data contracts for how the backend provides authorized
  patient, doctor, pharmacy, medication, prescription, and conversation context
  to the AI API.
- Store AI-specific metadata in AI-owned tables or schemas where appropriate.
- Store clinical knowledge metadata in relational tables controlled by the AI
  knowledge platform or exposed to the AI service through a backend-approved
  access pattern.
- Store embeddings either in a dedicated vector database or Postgres with
  `pgvector`, depending on the final retrieval architecture decision.
- Store audit logs in append-only tables with strict access controls.

The original documentation plan included `docs/05_DATABASE_DESIGN.md`. That
file should not be used to design the main application database unless ownership
changes. If created later, it should be limited to AI-owned metadata, retrieval
storage, evaluation records, audit traces, and backend-to-AI data contracts.

Database design must include:

- Patients
- Doctors
- Pharmacies
- Organizations
- Roles and permissions
- Conversations
- Messages
- Medical source documents
- Document chunks
- Embeddings
- Medications
- Drug interactions
- Contraindications
- Prescriptions
- Prescription line items
- OCR jobs
- Reminder schedules
- Appointments
- API keys
- Usage records
- Audit logs
- Evaluations
- Feature flags

## 12. Infrastructure Status

Current status: Not implemented.

Expected direction:

- Google Cloud Run for API services
- Docker for packaging
- Backend-owned database and auth services, with integration details to be
  confirmed by the backend team
- Redis for caching, rate limits, and job coordination
- Cloud scheduler or queue service for recurring jobs
- Object storage for source documents, prescription images, and OCR artifacts
- Centralized logging, tracing, metrics, and alerting

Infrastructure design must include:

- Development, staging, and production environments
- Secrets management
- CI/CD
- Database migrations
- Rollback strategy
- Disaster recovery
- Backup and restore testing
- Observability
- Security monitoring

## 13. API Status

Current status: Not implemented.

Expected direction:

- REST API using FastAPI for the AI service.
- Internal AI APIs called by the main backend.
- Streaming support for AI responses where appropriate.
- Strong JSON schemas for request and response validation.
- Internal API-key authentication for backend-to-AI requests.
- User authentication, partner authentication, and role-aware access are owned
  by the main backend.
- The AI API should receive authenticated and authorized user context from the
  backend rather than authenticating end users directly.

API design must include:

- Internal patient-context AI endpoints
- Internal doctor-assistant AI endpoints
- Internal pharmacy-assistant AI endpoints
- Internal partner-facing AI capability endpoints called through the backend
- Internal API-key verification endpoints or middleware
- Conversation endpoints
- Prescription OCR endpoints
- Drug information endpoints
- Drug interaction endpoints
- Reminder endpoints
- Evaluation and admin endpoints
- Usage and billing endpoints

## 14. AI Status

Current status: Not implemented.

Expected direction:

The AI system should be built as a controlled medical reasoning and response
orchestration layer, not as a raw chat wrapper around an LLM.

Required AI components:

- Conversation orchestrator
- Intent classifier
- Risk classifier
- Retrieval planner
- Context builder
- Tool router
- Prompt manager
- Safety policy engine
- Citation engine
- Grounding verifier
- Confidence scorer
- Response generator
- Refusal and escalation handler
- Memory manager
- Evaluation logger

The orchestrator should decide whether a request requires:

- Canonical medical retrieval
- Patient-specific context
- Medication interaction checks
- Contraindication checks
- Dosage verification
- OCR
- Emergency escalation
- Human review
- Refusal

## 15. Deployment Status

Current status: Not implemented.

Expected direction:

Deploy containerized FastAPI services to Google Cloud Run with managed
environment variables, secrets, autoscaling, and structured observability.

Deployment requirements:

- Separate dev, staging, and production projects or environments
- Automated CI checks
- Automated test runs
- Migration gates
- Health checks
- Readiness checks
- Rollback procedure
- Alerting for latency, errors, cost, and safety events

## 16. Evaluation Status

Current status: Not implemented.

Expected direction:

AI evaluation must cover:

- Groundedness
- Faithfulness
- Citation accuracy
- Source relevance
- Medical correctness
- Emergency escalation quality
- Contraindication detection
- Drug interaction detection
- Dosage verification accuracy
- Refusal quality
- Prompt injection resistance
- Latency
- Cost
- Multilingual robustness
- Regression stability

Evaluation should run in:

- Local development
- Pull requests
- Staging
- Scheduled production shadow tests
- Post-deployment monitoring

## 17. Open Questions

### Product Questions

- What is the initial launch market: Nigeria only, Africa-first, or global?
- What user surface launches first: mobile, web, WhatsApp, partner API, or
  internal dashboard?
- Which user persona is the first MVP: patient, pharmacy, doctor, or partner?
- Will Zam AI provide only educational guidance, or will it support clinician
  decision workflows from the start?
- What emergency escalation language is legally and clinically acceptable?

### Medical Governance Questions

- Who approves medical safety policies?
- Who reviews golden datasets?
- Who reviews high-risk AI failures?
- What clinical specialties are in scope at launch?
- What medical claims is the company willing to make?

### Data Questions

- Which medical sources are licensed and available immediately?
- What formats are source documents provided in?
- What update cadence does each source require?
- Will patient records be manually entered, uploaded, or integrated?
- Will pharmacy inventory be real-time or periodically synchronized?

### Technical Questions

- Should vector search start with Postgres `pgvector`, a managed vector database,
  or a hybrid approach?
- Which embedding provider gives the best combination of medical retrieval
  quality, cost, latency, and provider reliability?
- Which OCR provider best handles Nigerian prescriptions, handwriting,
  abbreviations, and image quality issues?
- Should background jobs use Celery, Dramatiq, RQ, Cloud Tasks, or another queue
  architecture?
- What observability stack is preferred for budget, compliance, and team
  experience?

## 18. Engineering Notes

### 18.1 Safety-First Implementation Order

The safest implementation order is:

1. Source ingestion and provenance
2. Retrieval and citation infrastructure
3. Evaluation datasets and test harness
4. AI orchestration with refusal behavior
5. Patient-facing chat or Q&A
6. Prescription OCR and medication intelligence
7. Personalization and reminders
8. Doctor, pharmacy, and partner workflows

This order prevents the team from shipping impressive but unsafe AI features
before the grounding and evaluation layers are mature.

### 18.2 Medical Response Policy

Every medical response should include enough metadata for internal audit:

- User ID or anonymous session ID
- Request ID
- Conversation ID
- Intent classification
- Risk classification
- Retrieved source IDs
- Source versions
- Chunk IDs
- Retrieval scores
- Model provider
- Model version
- Prompt version
- Tool calls
- Safety checks
- Groundedness score
- Confidence score
- Final response
- Refusal or escalation decision

### 18.3 High-Risk Intents

The following intents should be treated as high-risk by default:

- Emergency symptoms
- Pregnancy medication questions
- Pediatric medication questions
- Medication dosage changes
- Drug interaction questions
- Contraindication questions
- Chronic disease medication management
- Mental health crisis language
- Severe allergic reactions
- Chest pain, stroke symptoms, seizures, severe bleeding, poisoning, or
  breathing difficulty

High-risk intents should require stricter retrieval, safer language, escalation
guidance, and more conservative confidence thresholds.

### 18.4 Documentation Quality Bar

Each architecture document should:

- Explain the purpose of the subsystem.
- Define responsibilities and non-responsibilities.
- Show diagrams where useful.
- Explain alternatives considered.
- Justify selected approaches.
- Describe operational risks.
- Define acceptance criteria.
- Include implementation guidance.
- Include observability and evaluation needs.

## 19. Decision History

| Date | Decision | Status |
| --- | --- | --- |
| 2026-06-29 | Begin with architecture documentation before code implementation. | Accepted |
| 2026-06-29 | Treat medical hallucination prevention as the highest-priority engineering constraint. | Accepted |
| 2026-06-29 | Create documentation as multiple markdown files under `docs/`. | Accepted |
| 2026-06-29 | Build documentation one file at a time to preserve quality and reviewability. | Accepted |
| 2026-06-29 | Define Zam AI as an internal AI service called by the main backend using an internal API key. | Accepted |
| 2026-06-29 | Keep user authentication, authorization, and primary application database ownership with the main backend. | Accepted |
| 2026-06-29 | Defer full application database design because the backend engineer owns it. | Accepted |
| 2026-06-29 | Complete the current architecture documentation pass, excluding deferred database design. | Accepted |

## 20. Immediate Next Action

The next recommended action is to review this documentation set with the backend
engineer and confirm the backend-to-AI integration contract.

Priority review items:

- Internal API-key authentication format.
- Request and response envelopes.
- Which patient, prescription, medication, pharmacy, and conversation context
  the backend will pass to Zam AI.
- Whether Zam AI gets a separate metadata store.
- How AI audit traces are stored and retained.
- First medical sources available for ingestion.
- First MVP AI workflow to implement.
