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

## MEDICATION

Name: {{ medication.name }}
Strength: {{ medication.strength or "not specified" }}
Instructions: {{ medication.instructions or "not specified" }}

## PATIENT CONTEXT

{% if patient_context %}
Age: {{ patient_context.age or "unknown" }}
Weight: {{ patient_context.weight_kg or "not provided" }}
Known conditions: {{ patient_context.known_conditions | join(", ") or "none provided" }}
Current medications: {{ patient_context.current_medications | join(", ") or "none provided" }}
{% else %}
No patient context provided.
{% endif %}

## RETRIEVED MEDICAL EVIDENCE

{% if evidence %}
{% for item in evidence %}
[Source: {{ item.source_name or "Unknown" }}]
{{ item.text_content }}

{% endfor %}
{% else %}
No dosage evidence was retrieved.
{% endif %}

## OUTPUT FORMAT

Return ONLY valid JSON with this exact structure — no markdown, no extra text:

```json
{
  "dosages": [
    {
      "medication_name": "drug name",
      "stated_dosage": "dosage as prescribed",
      "assessment": "verified | caution | out_of_range | requires_review",
      "typical_range": "typical range from evidence or null",
      "flags": ["above_range", "below_range", "missing_weight", "missing_age", "renal_concern"],
      "citation_ids": ["c1", "c2"]
    }
  ],
  "missing_context": ["list of missing patient info needed"]
}
```

If the dosage is within the typical range, set assessment to "verified". If missing critical context like weight or renal function, include relevant flags and list them in missing_context.
