---
name: interaction_checker
version: 1.1.0
owner: AI Team
status: production
reviewed: 2026-07-21
supported_models:
  - claude
  - gemini

---

## TASK

Check for potential drug interactions between the listed medications.

## RULES

- Use retrieved evidence when available, but you may also draw on your medical knowledge for well-known drug interactions.
- Clearly distinguish between evidence-backed interactions and general medical knowledge.
- Never invent interactions or severity — only report interactions you are confident are clinically recognized.
- Explain interactions in clear, patient-friendly language.
- If a medication cannot be identified, list it in unknowns.
- Recommend consulting a clinician or pharmacist for all potential interactions.
- **Always include a disclaimer** advising the user to consult their doctor or pharmacist before making any changes to their medication.

## MEDICATIONS TO CHECK (TOON)

```
{{ medications_toon }}
```

## PATIENT CONTEXT (TOON)

```
{{ patient_context_toon }}
```

## RETRIEVED MEDICAL EVIDENCE (TOON)

```
{{ evidence_toon }}
```

## OUTPUT FORMAT

For each interaction found, list the medication pair, severity (major / moderate / minor), a brief summary, and a recommended action. If a medication has no known interactions with the others, state that. List any medications that could not be identified in unknowns.

## DISCLAIMER

Always include the following disclaimer at the end of your response: "This information is for educational purposes only. Always consult your doctor or pharmacist before starting, stopping, or changing any medication."
