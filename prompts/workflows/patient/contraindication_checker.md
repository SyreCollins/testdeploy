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

## MEDICATIONS

{% for med in medications %}
- {{ med.name }}{% if med.dose %} ({{ med.dose }}){% endif %}
{% endfor %}

## PATIENT CONTEXT

{% if patient_context %}
Age: {{ patient_context.age or "unknown" }}
Known conditions: {{ patient_context.known_conditions | join(", ") or "none provided" }}
Allergies: {{ patient_context.allergies | join(", ") or "none provided" }}
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
No contraindication evidence was retrieved.
{% endif %}

## OUTPUT FORMAT

For each contraindication found, list the medication, the contraindicated condition, severity (contraindicated / precaution / no_contraindication), a brief reason, and supporting citations. If a medication has no known contraindications with the patient's context, state that. List any medications that could not be evaluated due to missing context in missing_context, and any that could not be identified in unknowns.
