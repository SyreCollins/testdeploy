---
name: drug_info
version: 1.0.0
owner: AI Team
status: production
reviewed: 2026-07-06
supported_models:
  - claude
  - gemini

---

## TASK

Provide detailed medication information for the requested drug using only the retrieved evidence.

## RULES

- Never invent drug information.
- Only use retrieved evidence to answer.
- Preserve medication names, dosages, and strengths exactly as retrieved.
- If the evidence does not contain the requested section, state that clearly.
- Do not provide personal medical advice.
- Cite sources using [Source: name].

## REQUESTED DRUG

{{ drug_name }}

## REQUESTED SECTIONS

{% if requested_sections %}
{{ requested_sections | join(", ") }}
{% else %}
All available information.
{% endif %}

## RETRIEVED MEDICAL EVIDENCE (TOON)

```
{{ evidence_toon }}
```

## OUTPUT FORMAT

Respond with structured information organized by the requested sections. If the drug has a known generic name, include it. Use inline citations. If a requested section has no supporting evidence, note that the information is not available in the retrieved sources.

After your response, if there are relevant follow-up questions the user might want to ask, include them in a section like this:

## Follow-up Questions
- What are the common side effects?
- How long does treatment typically last?

Only include this section if you have meaningful follow-up questions. Keep questions brief and natural.
