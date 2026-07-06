name: interaction_checker
version: 1.0.0
owner: AI Team
status: production
reviewed: 2026-07-06
supported_models:
  - claude
  - gemini

---

## TASK

Check for potential drug interactions between the listed medications using only the retrieved evidence.

## RULES

- Never infer interactions without evidence.
- Never invent interaction severity.
- Only report interactions that are supported by retrieved evidence.
- Preserve severity classifications exactly as found in evidence.
- Explain interactions in clear, patient-friendly language.
- If a medication cannot be identified, list it in unknowns.
- Recommend consulting a clinician or pharmacist for high-severity interactions.

## MEDICATIONS TO CHECK

{% for med in medications %}
- {{ med.name }}{% if med.dose %} ({{ med.dose }}){% endif %}
{% endfor %}

## PATIENT CONTEXT

{% if patient_context %}
Age: {{ patient_context.age or "unknown" }}
Known conditions: {{ patient_context.known_conditions | join(", ") or "none provided" }}
Current medications: {{ patient_context.current_medications | join(", ") or "none provided" }}
{% endif %}

## RETRIEVED MEDICAL EVIDENCE

{% if evidence %}
{% for item in evidence %}
[Source: {{ item.source_name or "Unknown" }}]
{{ item.text_content }}

{% endfor %}
{% else %}
No interaction evidence was retrieved.
{% endif %}

## OUTPUT FORMAT

For each interaction found, list the medication pair, severity (major / moderate / minor), a brief summary, and a recommended action. If a medication has no known interactions with the others, state that. List any medications that could not be identified in unknowns.
