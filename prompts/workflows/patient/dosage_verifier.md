---
name: dosage_verifier
version: 1.0.0
owner: AI Team
status: draft
reviewed: 2026-07-08
supported_models:
  - claude
  - gemini

---

## TASK

Verify whether the supplied medication dosage is appropriate for the patient using only the retrieved evidence.

## RULES

- Do not prescribe a new dose.
- Flag unusual or unsupported doses clearly.
- Require review when patient-specific parameters are missing.
- Never invent dosage ranges without evidence.
- Only reference dosage information from retrieved evidence.
- If the dosage is within the typical range, state that clearly.
- If the dosage exceeds or falls below the typical range, flag it as a warning.

## MEDICATION (TOON)

```
{{ medication_toon }}
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

Return ONLY valid TOON format — no markdown, no extra text, no JSON:

```toon
dosages[1]{medication_name,stated_dosage,assessment,typical_range,flags,citation_ids}:
  drug name,dosage as prescribed,verified,typical range from evidence,above_range,c1
missing_context[1]: list of missing patient info needed
```

If the dosage is within the typical range, set assessment to "verified". If missing critical context like weight or renal function, include relevant flags and list them in missing_context. For flags, use a comma-separated list in the flags field.
