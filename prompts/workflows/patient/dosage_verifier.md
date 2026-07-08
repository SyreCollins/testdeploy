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

Provide an assessment of the dosage. Include the stated dosage, the typical range found in evidence, any flags (e.g., "above_range", "below_range", "missing_weight", "missing_age", "renal_concern"), and supporting citations. If patient-specific parameters are missing, list them in missing_context.
