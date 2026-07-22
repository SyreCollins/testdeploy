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
summary: brief patient-friendly summary of the prescription
sections[1]{title,content,citation_ids}:
  What is this medication for?,explanation of the medication's purpose,c1,c2
warnings[1]: list of important warnings based on evidence
```

Include sections relevant to the prescription such as medication purpose, how to take it, common side effects, and important warnings. Set warnings to an empty list if none are identified.

After your response, if there are relevant follow-up questions the user might want to ask, include them in a section like this:

## Follow-up Questions
- What should I do if I miss a dose?
- Are there any foods I should avoid?

Only include this section if you have meaningful follow-up questions. Keep questions brief and natural.
