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

Return ONLY valid JSON — no markdown, no extra text:

```json
{
  "contraindications": [
    {
      "medication": "drug name",
      "condition": "contraindicated condition",
      "severity": "contraindicated",
      "reason": "brief patient-friendly explanation",
      "evidence_summary": "summary of supporting evidence",
      "citation_ids": ["c1", "c2"]
    }
  ],
  "missing_context": ["list of missing patient info needed"],
  "unknowns": ["medications that could not be evaluated"]
}
```

If no contraindications are found, set contraindications to an empty array. If a medication has no known contraindications, include it with severity "no_contraindication".

After your response, if there are relevant follow-up questions the user might want to ask, include them in a section like this:

## Follow-up Questions
- Are there alternative medications I can take?
- What symptoms of a reaction should I watch for?

Only include this section if you have meaningful follow-up questions. Keep questions brief and natural.
