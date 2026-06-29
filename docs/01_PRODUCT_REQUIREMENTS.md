# Zam AI Product Requirements

## 1. Document Purpose

This product requirements document defines what Zam AI must become, who it
serves, what problems it solves, and what constraints govern the product.

Zam AI is a medical intelligence platform. It must be designed as a safe,
source-grounded AI system, not as a general-purpose chatbot. The platform should
support patients, doctors, pharmacies, and third-party health companies through
AI capabilities exposed primarily as internal APIs to the main Zamda Health
backend.

The main backend owns user authentication, user authorization, application
database access, user sessions, and product-facing API composition. Zam AI owns
AI orchestration, retrieval, grounding, citation, safety checks, medical
reasoning workflows, and AI evaluation.

## 2. Product Vision

Zam AI will be the trusted medical intelligence layer for Zamda Health.

The product vision is to make high-quality medical guidance, medication
intelligence, prescription understanding, and healthcare decision support
available through safe AI systems grounded in verified medical data.

Zam AI should eventually support:

- Patients trying to understand symptoms, medications, prescriptions, and health
  recommendations.
- Pharmacies trying to improve medication access, inventory intelligence,
  substitution guidance, and patient support.
- Doctors and clinical teams needing fast, evidence-linked support for medication
  review, patient summaries, and clinical decision workflows.
- Third-party health companies integrating reliable medical AI capabilities
  through Zamda Health APIs.

The platform should be built for long-term trust. In healthcare, trust comes
from accuracy, restraint, transparency, auditability, and well-designed failure
behavior.

## 3. Mission

Zam AI's mission is to provide medically safer AI assistance by ensuring that
answers are:

- Grounded in verified medical sources.
- Traceable to citations or structured clinical data.
- Conservative when evidence is incomplete.
- Personalized only when authorized patient context is available.
- Clear about uncertainty and limitations.
- Escalated appropriately for emergencies and high-risk scenarios.
- Measured continuously through automated and human evaluation.

## 4. Core Product Principle

No medical response should ever come from an LLM's internal knowledge.

Every medical answer must be based on at least one of the following:

- Retrieved verified medical source content.
- Approved structured clinical data.
- Deterministic medical tools such as interaction checkers or dosage validators.
- Authorized patient, prescription, medication, pharmacy, or clinical context
  provided by the main backend.

If the system cannot ground an answer, it must not fabricate one. It should ask
for clarification, provide non-medical navigation help, refuse to answer, or
escalate to a clinician or emergency service depending on risk.

## 5. Product Scope

### 5.1 In Scope

Zam AI should provide AI capabilities for:

- Symptom guidance and triage support.
- Medication information.
- Drug interaction checking.
- Contraindication detection.
- Dosage guidance and verification support.
- Prescription OCR and explanation.
- Medication schedule understanding.
- Medication reminders support.
- Patient health recommendations.
- Pharmacy intelligence.
- Doctor assistant workflows.
- Clinical decision support.
- Public API capabilities through the main backend.
- AI safety evaluation.
- Medical source ingestion and retrieval.
- Citation generation.
- Grounded response generation.

### 5.2 Out of Scope for Initial Release

The initial release should not attempt to provide:

- Autonomous diagnosis.
- Autonomous treatment prescription.
- Replacement for a licensed clinician.
- Emergency medical dispatch.
- Unsourced medical advice.
- Fully automated high-risk clinical decisions.
- Direct end-user authentication handled inside the AI API.
- Direct ownership of the main application database.
- Billing ownership for partner customers, unless delegated by the main backend.
- Fully autonomous prescription fulfillment.

These capabilities may require additional clinical, legal, operational, and
regulatory review before they can be considered.

## 6. User Personas

### 6.1 Patient

Patients use Zamda Health products to understand symptoms, medications,
prescriptions, and personal health next steps.

Patient goals:

- Understand what a medication is used for.
- Understand how to take a medication safely.
- Check whether two medications may interact.
- Understand a prescription written by a doctor.
- Know when symptoms may require urgent care.
- Receive reminders and health recommendations.
- Ask questions in plain language.

Patient risks:

- Misinterpreting AI guidance as a diagnosis.
- Delaying emergency care.
- Taking medication incorrectly.
- Ignoring contraindications.
- Sharing incomplete or inaccurate medical history.
- Uploading unclear prescription images.

Product requirements for patients:

- Use simple, non-alarming language.
- Provide clear emergency escalation when needed.
- Avoid definitive diagnosis.
- Cite medical sources where medical claims are made.
- Ask clarifying questions when important details are missing.
- Avoid dosage personalization unless authorized patient context and reliable
  source context are available.

### 6.2 Doctor

Doctors use Zam AI to speed up clinical workflows while remaining the final
decision-maker.

Doctor goals:

- Review medication information quickly.
- Check interactions and contraindications.
- Summarize patient context.
- Review prescription issues.
- Generate patient-friendly medication explanations.
- Access evidence-linked clinical support.

Doctor risks:

- Overreliance on AI.
- Missing source limitations.
- Using stale clinical guidance.
- Receiving incomplete patient context.
- Accepting AI-generated explanations without review.

Product requirements for doctors:

- Show source-backed reasoning.
- Preserve audit trails.
- Indicate confidence and evidence quality.
- Distinguish retrieved facts from AI-generated synthesis.
- Allow clinician override and feedback.
- Support structured outputs suitable for clinical review.

### 6.3 Pharmacy

Pharmacies use Zam AI for medication intelligence, customer support, and
inventory-aware recommendations.

Pharmacy goals:

- Understand drug alternatives.
- Check substitutions.
- Identify interaction and contraindication risks.
- Explain medications to patients.
- Match prescriptions to inventory.
- Forecast demand and stock risk in later phases.

Pharmacy risks:

- Suggesting unsafe substitutions.
- Confusing brand names and generic names.
- Providing advice beyond pharmacist scope.
- Using incomplete inventory data.
- Treating local stock availability as medical equivalence.

Product requirements for pharmacies:

- Separate clinical equivalence from inventory availability.
- Require source-backed substitution guidance.
- Show when pharmacist review is required.
- Support local brand and generic name mapping.
- Preserve audit history for recommendations.

### 6.4 Third-Party Health Company

Third-party companies integrate Zam AI capabilities through APIs exposed by the
main Zamda Health backend.

Partner goals:

- Add drug information to their products.
- Use prescription OCR.
- Check interactions.
- Retrieve medication explanations.
- Build patient support flows.
- Access reliable medical AI capabilities without building the whole stack.

Partner risks:

- Misusing AI outputs outside intended context.
- Sending insufficient patient context.
- Abusing APIs.
- Failing to display warnings and disclaimers.
- Hiding citations or uncertainty from end users.

Product requirements for partners:

- Use versioned API contracts.
- Enforce rate limits and usage policies through the main backend.
- Return structured safety metadata.
- Provide citation metadata.
- Support idempotency for long-running jobs such as OCR.
- Require product-level compliance agreements before access to sensitive
  capabilities.

### 6.5 Internal Clinical Reviewer

Clinical reviewers are medical professionals or trained safety reviewers who
inspect AI outputs, evaluation failures, source quality issues, and high-risk
cases.

Reviewer goals:

- Review unsafe or low-confidence responses.
- Approve or reject evaluation datasets.
- Identify source gaps.
- Provide feedback on prompt and retrieval behavior.
- Monitor high-risk medical categories.

Product requirements for reviewers:

- Provide review queues.
- Show full request and response trace.
- Show retrieved sources and citations.
- Show model, prompt, and source versions.
- Allow structured annotations.
- Feed annotations into evaluation and improvement workflows.

## 7. Business Objectives

Zam AI should help Zamda Health:

- Build a differentiated medical intelligence platform.
- Increase patient trust and retention.
- Improve medication safety.
- Support pharmacy operations.
- Enable doctor-facing productivity tools.
- Create a public API business line.
- Build defensible medical knowledge infrastructure.
- Reduce unsafe self-medication and prescription misunderstanding.
- Establish strong AI governance from the beginning.

## 8. Product Goals

### 8.1 Safety Goals

- Ensure medical claims are grounded in approved sources.
- Refuse or escalate when evidence is missing or risk is high.
- Detect emergencies and provide urgent escalation guidance.
- Detect prompt injection and source manipulation attempts.
- Preserve audit trails for every medical answer.

### 8.2 User Experience Goals

- Provide clear, empathetic, and understandable responses.
- Ask concise clarifying questions when needed.
- Avoid overwhelming patients with clinical jargon.
- Provide structured, source-linked detail for clinicians.
- Support fast response times for common questions.

### 8.3 Platform Goals

- Expose reliable internal AI APIs to the main backend.
- Support provider-swappable LLM architecture.
- Support scalable retrieval over verified sources.
- Support evaluation and regression testing.
- Support future partner APIs through backend-owned access control.

### 8.4 Operational Goals

- Monitor quality, latency, cost, and safety events.
- Support safe rollouts through feature flags.
- Support source updates without breaking retrieval quality.
- Support incident investigation through logs and traces.
- Support disaster recovery and rollback procedures.

## 9. Non-Goals

Zam AI should not:

- Act as an independent consumer app backend.
- Own end-user authentication.
- Own all application data.
- Replace clinicians.
- Diagnose users without clinician involvement.
- Prescribe medication.
- Fabricate medical advice when retrieval fails.
- Provide medical claims without citations.
- Optimize for model cleverness over verifiable safety.
- Launch public APIs before governance, rate limits, audit logs, and evaluation
  are mature.

## 10. Product Architecture Boundary

### 10.1 Main Backend Responsibilities

The main Zamda Health backend is responsible for:

- User authentication.
- User authorization.
- Session management.
- Patient, doctor, pharmacy, and partner identity.
- Main application database design.
- Primary product APIs.
- Billing and partner access control unless delegated.
- Enforcing user consent and data access permissions.
- Calling Zam AI using an internal API key.
- Passing only authorized context to Zam AI.

### 10.2 Zam AI Responsibilities

Zam AI is responsible for:

- AI capability endpoints.
- Internal API-key authentication.
- Request validation for AI workflows.
- Intent and risk classification.
- Medical retrieval.
- Source grounding.
- Citation generation.
- Tool routing.
- Prompt construction.
- LLM provider abstraction.
- Safety checks.
- Refusal and escalation decisions.
- Structured response generation.
- AI audit traces.
- AI evaluation.
- Medical source ingestion and indexing where owned by the AI platform.

### 10.3 Integration Principle

The AI API should not assume it can directly read any user data.

The main backend should provide the AI API with the minimum authorized context
required for a task. For example:

- User role
- Requesting organization
- Patient age band or exact age when clinically required
- Pregnancy status when authorized and relevant
- Known allergies when authorized and relevant
- Current medications when authorized and relevant
- Prescription details when authorized and relevant
- Pharmacy inventory details when authorized and relevant
- Conversation history window when authorized and relevant

The AI API should return:

- Final response
- Citations
- Safety metadata
- Confidence metadata
- Retrieved source metadata
- Tool-call metadata
- Refusal or escalation metadata
- Audit identifiers

## 11. Functional Requirements

### 11.1 Medical Question Answering

The system must answer medical questions only using retrieved source context.

Requirements:

- Classify the user's intent.
- Determine whether the question is medical.
- Retrieve relevant approved source content.
- Validate source relevance.
- Generate an answer grounded in the retrieved content.
- Include citations for medical claims.
- Refuse when retrieval fails or confidence is too low.
- Escalate emergency symptoms.

Acceptance criteria:

- Medical answers include source metadata.
- Unsupported claims are blocked by grounding checks.
- Emergency symptoms trigger escalation guidance.
- The system records prompt version, model version, source versions, and
  retrieval metadata.

### 11.2 Symptom Guidance

The system should help users understand possible urgency and next steps for
symptoms without claiming to diagnose.

Requirements:

- Detect emergency red flags.
- Ask clarifying questions when needed.
- Provide general educational guidance.
- Recommend appropriate care level when supported by source context.
- Avoid definitive diagnosis.
- Avoid false reassurance.
- Escalate urgent symptoms immediately.

Acceptance criteria:

- Chest pain, stroke-like symptoms, severe breathing difficulty, seizures,
  severe bleeding, poisoning, and anaphylaxis trigger urgent escalation.
- The system does not diagnose the user.
- The system clearly explains when a clinician should be consulted.

### 11.3 Drug Information

The system should provide medication information using verified drug sources.

Requirements:

- Support generic names.
- Support brand names.
- Support local spelling variations where available.
- Explain uses, common side effects, warnings, contraindications, and basic
  administration guidance.
- Distinguish general drug information from patient-specific advice.
- Include citations.

Acceptance criteria:

- The system can identify whether it is discussing a generic ingredient, brand,
  class, or formulation.
- The system refuses to infer drug information for unknown or ambiguous names
  without clarification.
- The system cites approved drug references.

### 11.4 Drug Interaction Checking

The system should identify potential interactions between medications and other
clinically relevant substances when reliable interaction data is available.

Requirements:

- Accept structured medication lists from the backend.
- Normalize medication names.
- Match medications to known ingredients.
- Check interactions through approved sources or deterministic tools.
- Return severity, explanation, source, and recommended action category.
- Escalate high-severity interactions.

Acceptance criteria:

- Interaction outputs distinguish between minor, moderate, major, and unknown
  severity when the data supports it.
- The system does not invent interaction data.
- The system indicates when interaction data is unavailable.

### 11.5 Contraindication Detection

The system should identify whether a medication may be contraindicated for a
patient context supplied by the backend.

Requirements:

- Use authorized patient context only.
- Consider allergies, pregnancy, age, known conditions, and current medications
  when supplied.
- Use verified contraindication data.
- Indicate missing context.
- Escalate high-risk findings.

Acceptance criteria:

- Contraindication outputs include evidence and source references.
- Missing patient context is explicitly called out.
- The system does not claim safety when patient context is incomplete.

### 11.6 Dosage Verification Support

The system should support dosage review, but with conservative scope.

Requirements:

- Parse dosage instructions from structured input or OCR output.
- Compare against approved dosage references where available.
- Consider patient context only when authorized and reliable.
- Flag unusual, unsupported, or potentially unsafe doses.
- Require clinician or pharmacist review for high-risk cases.

Acceptance criteria:

- The system does not prescribe new medication.
- The system does not recommend dosage changes without clear source support and
  appropriate role context.
- High-risk dosage issues trigger escalation to a clinician or pharmacist.

### 11.7 Prescription OCR

The system should extract medication information from prescription images.

Requirements:

- Accept prescription image references from the backend.
- Run OCR asynchronously when needed.
- Extract medication names, strength, dose, route, frequency, duration, and
  instructions.
- Preserve OCR confidence per field.
- Support human review for low-confidence fields.
- Never treat OCR output as clinically final without validation.

Acceptance criteria:

- OCR results include confidence scores.
- Low-confidence prescription fields are flagged.
- The system distinguishes OCR extraction from medical interpretation.
- Prescription explanation uses verified drug references after extraction.

### 11.8 Prescription Explanation

The system should explain prescriptions in patient-friendly language.

Requirements:

- Use parsed prescription data.
- Retrieve medication references.
- Explain each medication's likely purpose, how it is commonly taken, important
  warnings, and when to seek help.
- Avoid assuming the doctor's diagnosis unless provided.
- Cite sources.

Acceptance criteria:

- Explanations are understandable to non-clinicians.
- The system identifies uncertainty from OCR or missing context.
- The system warns users not to change prescribed treatment without a clinician.

### 11.9 Medication Reminders Support

The system should help transform medication instructions into reminder schedules
where appropriate.

Requirements:

- Parse structured dosage instructions.
- Generate proposed reminder schedules.
- Identify ambiguous instructions.
- Ask for clarification when schedule semantics are unclear.
- Return structured schedule data to the backend.

Acceptance criteria:

- The system does not create reminders from ambiguous or low-confidence
  instructions.
- The backend remains responsible for storing and sending reminders.
- The AI API returns structured schedule suggestions with confidence metadata.

### 11.10 Personalized Health Recommendations

The system may provide personalized recommendations only when authorized patient
context is provided by the backend.

Requirements:

- Use consented patient context.
- Use source-grounded medical recommendations.
- Distinguish general wellness guidance from medical guidance.
- Avoid high-risk personalized recommendations without clinician involvement.
- Log all personalization inputs used.

Acceptance criteria:

- Recommendations cite sources or structured clinical rules.
- The system indicates when more clinical context is needed.
- The system avoids diagnosis and treatment planning unless explicitly designed
  for clinician-supervised workflows.

### 11.11 Doctor Assistant

The system should support doctor-facing clinical assistance while preserving
clinician authority.

Requirements:

- Summarize provided patient context.
- Explain medication risks.
- Support interaction and contraindication review.
- Generate patient-friendly education drafts.
- Provide evidence-linked outputs.
- Avoid replacing clinical judgment.

Acceptance criteria:

- Doctor outputs include evidence and uncertainty.
- The system distinguishes facts from generated suggestions.
- Every high-risk output is traceable.

### 11.12 Pharmacy Assistant

The system should support pharmacy-facing medication intelligence.

Requirements:

- Explain medications.
- Support interaction and contraindication review.
- Identify possible alternatives only when clinically supported.
- Distinguish inventory availability from clinical appropriateness.
- Support pharmacist review.

Acceptance criteria:

- Alternative medication guidance includes source and safety constraints.
- The system does not imply two products are interchangeable without evidence.
- Inventory-driven suggestions require pharmacy review.

### 11.13 Partner AI Capabilities

The system should support partner-facing capabilities through the main backend.

Requirements:

- Provide versioned internal capability endpoints.
- Return structured JSON.
- Include safety and citation metadata.
- Support rate-limit metadata from the backend where needed.
- Support async jobs for OCR and long-running workflows.

Acceptance criteria:

- Partner-facing outputs are mediated by the backend.
- The AI service does not authenticate partners directly unless explicitly
  delegated in a future architecture decision.
- Capability outputs are stable and versioned.

## 12. Non-Functional Requirements

### 12.1 Safety

- Medical answers must be grounded.
- Unsupported claims must be blocked.
- High-risk categories must have stricter thresholds.
- Emergency symptoms must trigger escalation.
- The system must preserve audit traces.

### 12.2 Reliability

- The AI API should degrade gracefully when providers fail.
- Retrieval failures should produce safe refusals.
- Long-running jobs should be idempotent.
- Background processing should support retries.
- Critical workflows should be observable.

### 12.3 Scalability

The system should be designed for millions of users over time.

Requirements:

- Stateless API services where possible.
- Horizontal scaling on Cloud Run.
- Queue-based background work.
- Cache common retrieval and metadata operations.
- Separate online serving from offline ingestion.
- Avoid tight coupling to a single LLM provider.

### 12.4 Maintainability

- Domain modules should have clear boundaries.
- Prompts should be versioned and reviewed.
- Medical source versions should be preserved.
- API schemas should be typed and documented.
- Evaluation tests should run continuously.

### 12.5 Privacy

- Process only the minimum required patient context.
- Do not store unnecessary sensitive data in AI logs.
- Redact or tokenize sensitive data where possible.
- Follow consent and retention rules defined by the backend and compliance
  architecture.
- Maintain strict audit trails for access to patient context.

### 12.6 Compliance

The product must be designed with Nigerian data protection obligations in mind,
including NDPA-aligned privacy and security practices. Additional compliance
requirements may apply depending on markets, partner contracts, and clinical
scope.

## 13. Performance Targets

Initial targets should be treated as product goals and refined after load tests.

### 13.1 Online AI Response Targets

For normal medical Q&A:

- P50 latency: under 4 seconds.
- P95 latency: under 10 seconds.
- Timeout target: under 30 seconds.

For high-risk medical Q&A:

- P50 latency: under 6 seconds.
- P95 latency: under 15 seconds.
- Safety checks must not be skipped to improve latency.

For streaming responses:

- Time to first token: under 2.5 seconds where provider and retrieval allow.
- Citations and safety metadata may arrive at finalization if necessary.

### 13.2 Retrieval Targets

- P50 retrieval latency: under 800 ms.
- P95 retrieval latency: under 2 seconds.
- Hybrid retrieval and reranking may exceed these limits for complex workflows,
  but should be monitored.

### 13.3 OCR Targets

Prescription OCR may be asynchronous.

- Simple printed prescription P50 completion: under 20 seconds.
- Complex or handwritten prescription P95 completion: under 2 minutes.
- Low-confidence prescriptions should enter review instead of forcing an answer.

### 13.4 Availability Targets

Initial targets:

- AI API uptime: 99.5% for MVP.
- Production target after hardening: 99.9%.
- Retrieval availability should be monitored separately from LLM availability.

## 14. Security Requirements

### 14.1 Internal API Authentication

The main backend must authenticate to Zam AI using an internal API key or
equivalent service-to-service credential.

Requirements:

- Store keys in a managed secret store.
- Rotate keys.
- Support separate keys for development, staging, and production.
- Log key identity, not raw key values.
- Reject requests without valid credentials.
- Support future migration to mTLS or signed service tokens if required.

### 14.2 Authorization Context

The AI API should trust only authorization context provided by the main backend
after successful internal authentication.

Requirements:

- Require `request_id`.
- Require caller identity or service identity.
- Require user role where relevant.
- Require organization or tenant context where relevant.
- Require consent flags where patient context is used.
- Reject context fields that are malformed or incomplete.

### 14.3 Sensitive Data Handling

Requirements:

- Minimize stored patient data.
- Avoid logging raw sensitive values unless required for audit and explicitly
  protected.
- Redact secrets and credentials.
- Encrypt data in transit.
- Encrypt sensitive data at rest where stored by the AI service.
- Keep audit logs append-only where possible.

### 14.4 Prompt Injection Protection

Requirements:

- Treat user input and retrieved document text as untrusted.
- Separate system instructions from retrieved content.
- Detect attempts to override medical safety policy.
- Prevent retrieved documents from becoming executable instructions.
- Block requests that ask the model to ignore sources or fabricate citations.

## 15. Medical Safety Requirements

### 15.1 Grounding

All medical claims must map to retrieved sources, structured tools, or authorized
clinical context.

### 15.2 Citations

Medical responses should include citations where user experience permits. At
minimum, citation metadata must be returned to the backend for audit and
display.

### 15.3 Refusal

The system must refuse when:

- The requested answer requires medical evidence and retrieval fails.
- The retrieved evidence is irrelevant or contradictory.
- The user asks for unsafe instructions.
- The user asks the AI to replace a clinician in a high-risk situation.
- The user asks for concealed, illegal, or abusive medical behavior.

### 15.4 Escalation

The system must escalate when:

- Emergency symptoms are detected.
- Severe adverse reaction language is detected.
- Self-harm or mental health crisis language is detected.
- Pediatric, pregnancy, or severe chronic disease medication risk is present and
  context is insufficient.
- High-risk drug interaction or contraindication is found.

### 15.5 Uncertainty

The system must communicate uncertainty clearly and conservatively. It should not
hide missing information, source limitations, or low confidence.

## 16. Success Metrics

### 16.1 Safety Metrics

- Groundedness score.
- Citation accuracy.
- Hallucination rate.
- Unsafe answer rate.
- Emergency escalation recall.
- Refusal appropriateness.
- High-risk workflow defect rate.

### 16.2 Product Metrics

- Successful answer rate.
- Clarification rate.
- User satisfaction.
- Doctor review acceptance rate.
- Pharmacy workflow completion rate.
- Prescription OCR completion rate.
- Partner API usage.

### 16.3 Operational Metrics

- Latency by workflow.
- Cost per request.
- LLM provider error rate.
- Retrieval error rate.
- OCR error rate.
- Queue backlog.
- Evaluation regression failures.

### 16.4 Data Metrics

- Source coverage.
- Source freshness.
- Chunk retrieval quality.
- Medication normalization accuracy.
- Brand-to-generic mapping accuracy.
- OCR field accuracy.

## 17. Acceptance Criteria

Zam AI should not be considered ready for MVP until:

- Medical source ingestion works for at least the first approved source set.
- Retrieval returns relevant, versioned source chunks.
- Medical Q&A refuses when source context is missing.
- Citations are generated and auditable.
- Emergency symptom escalation works in evaluation tests.
- Drug information answers are grounded.
- Interaction checking uses approved sources or deterministic tools.
- The internal API key model is implemented.
- The AI API receives authorized context from the backend rather than owning user
  auth.
- Logs capture request, retrieval, model, prompt, safety, and response metadata.
- Golden evaluation datasets exist for core workflows.
- Regression tests run before deployment.
- Production monitoring exists for latency, errors, cost, and safety events.

## 18. Product Risks

### 18.1 Hallucinated Medical Content

Risk:

The model may generate medical content not supported by sources.

Mitigation:

- Retrieval-required generation.
- Grounding verification.
- Citation validation.
- Conservative refusal.
- Continuous evaluation.

### 18.2 Incorrect Source Retrieval

Risk:

The response may be grounded in the wrong source or wrong medication.

Mitigation:

- Medication normalization.
- Hybrid retrieval.
- Reranking.
- Source metadata filters.
- Evaluation datasets.
- Citation accuracy checks.

### 18.3 Incomplete Patient Context

Risk:

The AI may answer a personalized question without critical patient details.

Mitigation:

- Require explicit context fields.
- Ask clarifying questions.
- State missing information.
- Avoid personalized conclusions when context is insufficient.

### 18.4 OCR Errors

Risk:

Prescription OCR may misread medication names or dosages.

Mitigation:

- Field-level confidence.
- Medication normalization.
- Human review queue.
- Low-confidence refusal.
- Clear separation between extraction and advice.

### 18.5 Data Ownership Ambiguity

Risk:

The AI API and main backend could duplicate or conflict over database ownership.

Mitigation:

- Define integration contracts.
- Keep user auth and primary application data backend-owned.
- Keep AI traces, retrieval metadata, and evaluation data AI-owned where needed.
- Review schema boundaries before implementation.

### 18.6 Regulatory Scope Risk

Risk:

The product may drift into regulated clinical decision-making without adequate
governance.

Mitigation:

- Define scope in product language.
- Require clinical review for high-risk workflows.
- Log and evaluate safety-critical behavior.
- Maintain disclaimers and escalation policies.

## 19. Future Roadmap Summary

The detailed roadmap belongs in `docs/11_ROADMAP.md`. At the PRD level, the
product should progress through:

1. Documentation and architecture foundation.
2. Medical source ingestion and retrieval.
3. AI orchestration and safety layer.
4. Patient MVP.
5. Prescription OCR and medication intelligence.
6. Patient personalization.
7. Doctor and pharmacy workflows.
8. Voice, multilingual, and predictive AI.
9. Partner SaaS platform.

## 20. Open Product Questions

- Which medical source set is available first?
- Which market launches first?
- Which user group is the first MVP?
- What exact user-facing surfaces will call the backend: mobile, web, WhatsApp,
  API partners, or all?
- What clinical governance body approves safety policy?
- What patient context will the backend provide to the AI API in MVP?
- What data will the AI API be allowed to store?
- What source citations must be visible to end users versus only logged for
  audit?
- What partner capabilities are allowed in the first public API release?
- What compliance obligations apply beyond NDPA?

## 21. PRD Change Log

| Date | Change | Status |
| --- | --- | --- |
| 2026-06-29 | Initial PRD created from project brief. | Draft |
| 2026-06-29 | Clarified that main backend owns database/auth and calls Zam AI using an internal API key. | Draft |
