# Zam AI Engineering Guidelines

## 1. Purpose

This document defines engineering standards for building Zam AI.

The goal is to keep the codebase safe, maintainable, auditable, and easy for new
engineers to understand. Zam AI is a medical AI platform, so engineering quality
directly affects product safety.

## 2. Core Engineering Principles

- Medical safety before speed.
- Retrieval before generation.
- Explicit contracts over hidden assumptions.
- Provider abstraction over vendor lock-in.
- Structured outputs over unparseable prose.
- Evaluation before release.
- Auditability by default.
- Minimal patient context.
- Conservative failure behavior.
- Small modules with clear ownership.

## 3. Repository Structure

Recommended implementation structure:

```text
app/
  api/
    routes/
    schemas/
    middleware/
  core/
    config/
    errors/
    security/
    telemetry/
  domains/
    medical_qa/
    symptom_guidance/
    drug_information/
    interactions/
    contraindications/
    dosage/
    prescriptions/
    reminders/
    doctor_assistant/
    pharmacy_assistant/
  ai/
    orchestration/
    prompts/
    model_gateway/
    safety/
    citations/
    confidence/
  rag/
    ingestion/
    normalization/
    chunking/
    embeddings/
    retrieval/
    reranking/
  workers/
  integrations/
    llm/
    ocr/
    storage/
    queue/
    vector_store/
  evaluation/
  db/
tests/
  unit/
  integration/
  evaluation/
scripts/
docs/
```

## 4. Coding Standards

Python standards:

- Use type hints.
- Use Pydantic models for external request and response schemas.
- Keep route handlers thin.
- Keep business logic in services.
- Keep provider SDK calls behind adapters.
- Avoid global mutable state.
- Prefer explicit errors.
- Avoid broad exception swallowing.

Medical AI standards:

- Do not call LLMs directly from routes.
- Do not generate medical answers without retrieval or approved tool evidence.
- Do not hide safety logic in prompts only.
- Log prompt versions.
- Log model versions.
- Log source versions.
- Return structured safety metadata.

## 5. Naming Conventions

Use names that communicate domain intent.

Examples:

- `MedicalQaOrchestrator`
- `RiskClassifier`
- `GroundingVerifier`
- `CitationEngine`
- `MedicationNormalizer`
- `InteractionCheckResult`
- `PrescriptionOcrJob`

Avoid vague names:

- `Helper`
- `Processor`
- `Manager`
- `Thing`
- `AIUtil`

## 6. Dependency Injection

Use dependency injection for:

- Model providers.
- Embedding providers.
- Vector store clients.
- OCR providers.
- Queue clients.
- Storage clients.
- Safety policies.
- Evaluation scorers.

Benefits:

- Easier testing.
- Easier provider swapping.
- Cleaner local development.
- Reduced vendor lock-in.

## 7. Provider Adapters

Provider-specific code belongs in integration adapters.

Rules:

- Business logic uses internal interfaces.
- Adapters normalize provider responses.
- Adapters capture latency, usage, and errors.
- Provider model versions are recorded.
- Provider exceptions are mapped to internal errors.

## 8. Prompt Management

Prompts are production artifacts.

Prompt requirements:

- Versioned.
- Reviewed.
- Tested.
- Linked to workflows.
- Stored in a predictable location.
- Logged in audit traces.

Prompt changes should trigger evaluation runs.

Prompts should not contain:

- Secrets.
- Hidden business logic that belongs in code.
- Unreviewed medical policy.
- Assumptions about unavailable patient data.

## 9. Testing Strategy

### 9.1 Unit Tests

Unit test:

- Validators.
- Classifiers.
- Safety policy functions.
- Tool routers.
- Context builders.
- Citation formatters.
- Provider adapters with mocks.

### 9.2 Integration Tests

Integration test:

- API request validation.
- Internal API-key middleware.
- Retrieval service.
- Queue dispatch.
- OCR job lifecycle.
- Audit writes.

### 9.3 Evaluation Tests

Evaluation tests cover:

- Groundedness.
- Citation accuracy.
- Emergency escalation.
- Refusal behavior.
- Prompt injection resistance.
- Retrieval relevance.

High-risk AI changes should not deploy without evaluation.

## 10. Error Handling

Use structured internal errors.

Error fields:

- Code.
- Message.
- Retryable.
- Safe user-facing message where applicable.
- Debug metadata for internal logs.

Do not leak:

- Secrets.
- Raw provider errors if sensitive.
- System prompts.
- Unredacted patient data.

## 11. Logging Standards

Use structured logs.

Required fields:

- Timestamp.
- Environment.
- Service.
- Request ID.
- Trace ID.
- Endpoint.
- Workflow.
- Status.
- Latency.
- Error code.

Sensitive values should be redacted.

## 12. Audit Standards

Every medical response should create an audit trace.

Audit traces should capture:

- Request ID.
- Workflow.
- Context categories used.
- Intent.
- Risk.
- Source IDs and versions.
- Tool calls.
- Prompt version.
- Model provider and version.
- Safety result.
- Final action.

## 13. Documentation Standards

Every significant subsystem should document:

- Purpose.
- Responsibilities.
- Inputs and outputs.
- Failure modes.
- Safety considerations.
- Test strategy.

Architecture decisions should be recorded in `docs/12_DECISION_LOG.md`.

## 14. Git Workflow

Recommended workflow:

- Use feature branches.
- Keep PRs focused.
- Include tests.
- Include evaluation results for AI changes.
- Avoid unrelated refactors in safety-critical PRs.
- Require review for prompts, retrieval, safety policy, and provider changes.

Branch naming:

```text
feature/<short-name>
fix/<short-name>
docs/<short-name>
experiment/<short-name>
```

## 15. Pull Request Standards

PRs should include:

- Summary.
- Why the change is needed.
- Files changed.
- Tests run.
- Evaluation run if AI behavior changed.
- Safety considerations.
- Rollback plan for risky changes.

AI behavior changes should include:

- Prompt version changes.
- Model changes.
- Retrieval changes.
- Before/after evaluation results.
- Known risks.

## 16. Feature Flags

Use feature flags for:

- New workflows.
- Prompt versions.
- Model versions.
- Retrieval strategies.
- OCR providers.
- Source corpus versions.

Flags that affect medical output must be logged in audit traces.

## 17. Security Guidelines

Engineers must:

- Never commit secrets.
- Use managed secret storage.
- Redact sensitive logs.
- Treat user input as untrusted.
- Treat retrieved content as untrusted evidence.
- Validate file inputs.
- Avoid unnecessary patient context.
- Follow internal API-key authentication rules.

## 18. Medical Safety Guidelines

Engineers must not:

- Add medical answer paths without retrieval.
- Add hidden fallback to model knowledge.
- Fabricate citations.
- Use OCR output as fact without confidence checks.
- Treat inventory availability as clinical appropriateness.
- Skip safety checks to reduce latency.

Engineers should:

- Prefer structured medical tools where possible.
- Add regression tests for every safety bug.
- Escalate uncertain high-risk behavior.
- Preserve source version metadata.

## 19. Local Development

Local development should support:

- Running API service.
- Running worker.
- Running unit tests.
- Running evaluation smoke tests.
- Using fake provider adapters.
- Loading sample documents.

Developers should not need production credentials for normal work.

## 20. Review Requirements by Change Type

| Change Type | Required Review |
| --- | --- |
| API schema | Backend and AI engineering |
| Prompt | AI engineering and clinical/safety reviewer for medical workflows |
| Retrieval config | AI engineering |
| Source promotion | AI engineering and clinical/source owner |
| Safety policy | AI engineering and clinical/safety owner |
| Provider change | AI engineering and security review |
| OCR behavior | AI engineering and product/clinical review |

## 21. Open Questions

- Which Python tooling stack should be standardized?
- Which evaluation framework should be adopted?
- What exact PR approval policy will the team use?
- Who owns clinical safety review?
- Which feature flag provider should be used?

## 22. Change Log

| Date | Change | Status |
| --- | --- | --- |
| 2026-06-29 | Initial engineering guidelines created. | Draft |
