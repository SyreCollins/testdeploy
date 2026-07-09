---
name: prescription_explainer
version: 1.0.0
owner: AI Team
status: draft
reviewed: 2026-07-08
supported_models:
  - claude
  - gemini

---

## TASK

Explain the supplied prescription in patient-friendly language using retrieved medical evidence.

## RULES

- Do not assume a diagnosis unless it is supplied.
- Use retrieved drug references to explain what the medication is for.
- Explain the purpose, how to take it, common side effects, and important warnings.
- If the prescription text is ambiguous, note the ambiguity.
- Never provide diagnostic information.
- Recommend consulting a clinician with any questions.

## PRESCRIPTION TEXT

{{ prescription_text }}

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
No drug information was retrieved.
{% endif %}

## OUTPUT FORMAT

Return ONLY valid JSON with this exact structure — no markdown, no extra text:

```json
{
  "summary": "brief patient-friendly summary of the prescription",
  "sections": [
    {
      "title": "What is this medication for?",
      "content": "explanation of the medication's purpose",
      "citation_ids": ["c1", "c2"]
    },
    {
      "title": "How to take it",
      "content": "usage instructions",
      "citation_ids": ["c3"]
    }
  ],
  "warnings": ["list of important warnings based on evidence"]
}
```

Include sections relevant to the prescription such as medication purpose, how to take it, common side effects, and important warnings. Set warnings to an empty list if none are identified.
