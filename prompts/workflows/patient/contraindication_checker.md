---
name: contraindication_checker
version: 1.0.0
owner: AI Team
status: draft
reviewed: 2026-07-08
supported_models:
  - claude
  - gemini

---

## TASK

Check whether the supplied medications are contraindicated for the provided patient context using only the retrieved evidence.

## RULES

- Never invent contraindications without evidence.
- Never infer contraindications not supported by retrieved evidence.
- Preserve severity classifications exactly as found in evidence.
- If patient context is missing critical information, list it in missing_context.
- Explain contraindications in clear, patient-friendly language.
- Recommend consulting a clinician for high-risk findings.

## MEDICATIONS (TOON)

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

Return ONLY valid TOON format — no markdown, no extra text, no JSON:

```toon
contraindications[1]{medication,condition,severity,reason,evidence_summary,citation_ids}:
  drug name,contraindicated condition,contraindicated,brief patient-friendly explanation,summary of supporting evidence,c1,c2
missing_context[1]: list of missing patient info needed
unknowns[1]: medications that could not be evaluated
```

If no contraindications are found, set contraindications to an empty array: `contraindications[0]:` with no rows. If a medication has no known contraindications, include it with severity "no_contraindication".
