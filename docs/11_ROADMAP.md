# Zam AI Roadmap

## 1. Purpose

This roadmap organizes Zam AI development by engineering dependencies rather
than user type. The safest path is to build the medical knowledge, retrieval,
safety, evaluation, and deployment foundations before shipping user-facing AI
features.

## 2. Roadmap Principles

- Build safety infrastructure before broad product features.
- Build retrieval before generation.
- Build evaluation before launch.
- Keep the AI API internal behind the main backend.
- Do not assume ownership of the main application database.
- Add high-risk workflows only after source grounding and review paths exist.

## Phase 0: Project Setup

### Objectives

Create the basic engineering foundation for the Zam AI service.

### Deliverables

- FastAPI project scaffold.
- Dockerfile.
- Local development environment.
- Configuration system.
- Internal API-key middleware.
- Health and readiness endpoints.
- CI pipeline.
- Formatting, linting, and test setup.
- Basic structured logging.
- Initial deployment skeleton.

### Dependencies

- Agreement with backend team on internal API integration.
- Secret management decision.
- Environment naming convention.

### Acceptance Criteria

- API starts locally.
- Health endpoint works.
- Internal API-key authentication works.
- CI runs on every change.
- Docker image builds.
- Basic logs include request IDs.

### Testing Requirements

- Unit tests for API-key middleware.
- Integration test for health and readiness endpoints.
- Docker build test.

### Risks

- Starting product workflows before service boundaries are stable.
- Hardcoding secrets or provider config.

## Phase 1: Medical Knowledge Platform

### Objectives

Build the source ingestion and retrieval foundation.

### Deliverables

- Source registry.
- Raw document storage.
- Source license/status tracking.
- Document parsing pipeline.
- Normalization pipeline.
- Chunking pipeline.
- Metadata schema.
- Embedding interface.
- Vector store integration.
- Hybrid retrieval prototype.
- Citation metadata model.
- Corpus versioning.

### Dependencies

- First approved medical source.
- Vector database decision.
- Embedding provider decision.
- Object storage decision.

### Acceptance Criteria

- At least one approved source can be ingested.
- Chunks preserve source, version, and section metadata.
- Retrieval returns relevant chunks for known test queries.
- Source versions are auditable.
- Corpus can be rebuilt.

### Testing Requirements

- Parser tests.
- Chunking tests.
- Retrieval benchmark.
- Citation metadata tests.
- Source versioning tests.

### Risks

- Source licensing delays.
- Poor PDF extraction quality.
- Bad chunking causing unsafe retrieval.

## Phase 2: AI Core

### Objectives

Build the controlled AI orchestration layer.

### Deliverables

- Conversation orchestrator.
- Intent classifier.
- Risk classifier.
- Safety policy engine.
- Context builder.
- Prompt manager.
- Model gateway.
- Citation engine.
- Grounding verifier.
- Confidence scorer.
- Audit trace writer.

### Dependencies

- RAG retrieval prototype.
- Initial prompt policy.
- LLM provider decision.
- AI metadata storage decision.

### Acceptance Criteria

- Medical answer generation requires retrieved evidence.
- Prompt versions are logged.
- Model versions are logged.
- Grounding failures produce refusal.
- Audit traces are written.

### Testing Requirements

- Unit tests for orchestration branches.
- Safety refusal tests.
- Grounding tests.
- Prompt injection baseline tests.
- Model gateway mock tests.

### Risks

- Hidden business logic accumulating in prompts.
- LLM provider behavior changes.
- Overly permissive fallback behavior.

## Phase 3: Patient MVP

### Objectives

Expose safe patient-facing AI capabilities through the main backend.

### Deliverables

- Medical Q&A endpoint.
- Drug information endpoint.
- Symptom guidance endpoint.
- Emergency escalation behavior.
- Backend integration contract.
- Citation response format.
- Basic user-facing response metadata.

### Dependencies

- Backend API integration.
- Approved patient safety language.
- Medical Q&A evaluation dataset.
- Emergency escalation dataset.

### Acceptance Criteria

- Patient medical Q&A is grounded.
- Drug info answers cite approved sources.
- Emergency symptoms escalate.
- Unsupported medical questions refuse safely.
- Backend can call AI API with internal key.

### Testing Requirements

- End-to-end backend-to-AI integration tests.
- Golden medical Q&A tests.
- Emergency escalation tests.
- Latency tests.

### Risks

- Users treating guidance as diagnosis.
- Missing source coverage.
- False reassurance in symptom guidance.

## Phase 4: Prescription Intelligence

### Objectives

Add OCR, parsing, medication explanation, interaction checks, and dosage review
support.

### Deliverables

- OCR job API.
- OCR worker.
- Prescription field parser.
- Field-level confidence.
- Prescription explanation workflow.
- Interaction checking workflow.
- Dosage verification support.
- Human review flags.

### Dependencies

- OCR provider decision.
- Prescription image storage pattern.
- Medication normalization.
- Interaction data source.
- Dosage reference source.

### Acceptance Criteria

- OCR jobs are asynchronous and idempotent.
- Low-confidence fields require review.
- Prescription explanations use verified drug sources.
- Interaction checks do not invent severity.
- Dosage verification refuses when context/evidence is insufficient.

### Testing Requirements

- OCR sample dataset.
- Parser tests.
- Interaction tests.
- Dosage safety tests.
- Low-confidence handling tests.

### Risks

- Handwriting OCR errors.
- Misread dosages.
- Unsafe confidence in ambiguous prescriptions.

## Phase 5: Patient Personalization

### Objectives

Use authorized backend-provided patient context for safer personalized guidance.

### Deliverables

- Patient context schema.
- Consent-aware context validation.
- Allergy-aware medication guidance.
- Current medication-aware interaction checks.
- Reminder schedule parser.
- Health summary support.
- Personalization audit metadata.

### Dependencies

- Backend patient context contract.
- Consent flag contract.
- Retention policy.
- Personalization safety policy.

### Acceptance Criteria

- AI only personalizes when context is authorized.
- Missing context is clearly reported.
- Reminder schedule suggestions are structured.
- Personalization inputs are logged by category.

### Testing Requirements

- Consent validation tests.
- Missing-context tests.
- Allergy and medication interaction tests.
- Reminder parser tests.

### Risks

- Over-personalization from incomplete context.
- Privacy violations through excessive context.

## Phase 6: Doctor and Pharmacy

### Objectives

Add clinician and pharmacy assistant workflows.

### Deliverables

- Doctor assistant endpoint.
- Pharmacy assistant endpoint.
- Medication review workflow.
- Patient education draft workflow.
- Inventory-context workflow.
- Alternative medication support.
- Pharmacist/clinician review metadata.

### Dependencies

- Backend role context.
- Pharmacy inventory context contract.
- Clinical review policy.
- Alternative medication source data.

### Acceptance Criteria

- Doctor outputs distinguish facts, context, and AI synthesis.
- Pharmacy outputs separate availability from clinical appropriateness.
- Alternatives require source-backed rationale.
- High-risk results indicate review requirements.

### Testing Requirements

- Clinician-reviewed golden cases.
- Pharmacy substitution tests.
- Role-context tests.
- Safety review tests.

### Risks

- AI appearing to replace clinician judgment.
- Unsafe substitution guidance.
- Inventory data misused as clinical evidence.

## Phase 7: Advanced AI

### Objectives

Add advanced interfaces and predictive capabilities only after the core platform
is safe and observable.

### Deliverables

- Voice interface architecture.
- Multilingual support.
- Translation safety checks.
- Predictive analytics prototypes.
- Outbreak detection prototype.
- Demand forecasting prototype.
- Drug shortage prediction prototype.

### Dependencies

- Mature evaluation framework.
- Voice provider decision.
- Multilingual medical evaluation set.
- Predictive model governance.
- Clinical validation process.

### Acceptance Criteria

- Voice confirms medication names and dosages.
- Translation preserves clinical meaning.
- Predictive models are evaluated separately from generative AI.
- Predictive outputs do not feed patient advice without approval.

### Testing Requirements

- Speech recognition tests.
- Translation fidelity tests.
- Bias/fairness tests.
- Predictive validation tests.

### Risks

- Misheard medication names.
- Translation errors.
- Unsupported predictive claims.
- Bias in risk scoring.

## Phase 8: Public SaaS Platform

### Objectives

Expose selected Zam AI capabilities to third-party companies through the main
backend and partner platform.

### Deliverables

- Partner capability catalog.
- Usage tracking.
- Billing integration.
- Developer portal.
- API documentation.
- Partner rate limits.
- Partner audit logs.
- Load testing.
- Production hardening.

### Dependencies

- Backend partner platform.
- Billing system.
- Legal terms.
- Compliance review.
- Mature observability.
- Stable capability APIs.

### Acceptance Criteria

- Partner access is mediated by backend.
- Usage and billing are tracked.
- Rate limits are enforced.
- Partner APIs return safety and citation metadata.
- Load tests meet production targets.

### Testing Requirements

- Contract tests.
- Load tests.
- Abuse tests.
- Partner sandbox tests.
- Security tests.

### Risks

- Partners hiding safety metadata.
- API abuse.
- Scaling costs.
- Compliance obligations expanding by partner market.

## Cross-Phase Requirements

Every phase should maintain:

- Structured logging.
- Audit traces.
- Evaluation coverage.
- Security review for sensitive changes.
- Documentation updates.
- Decision log updates.

## Change Log

| Date | Change | Status |
| --- | --- | --- |
| 2026-06-29 | Initial engineering dependency roadmap created. | Draft |
