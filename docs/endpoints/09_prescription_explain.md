# Prescription Explanation

`POST /v1/ai/prescriptions/explain`

Explains structured prescription information in patient-friendly language.

## Purpose

Translates prescription text into easy-to-understand language for patients. Includes medication purpose, usage instructions, warnings, and side effects — all backed by approved sources.

## Authentication

Requires a valid internal API key via the `X-Zam-AI-Key` header.

## Request

```json
{
  "request_id": "7d9827b8-9f42-4f4f-8e4a-3c4b4fd973a1",
  "caller": {
    "service": "zamda-backend",
    "environment": "production"
  },
  "actor_context": {
    "actor_type": "patient",
    "actor_id": "user-202",
    "role": "patient"
  },
  "authorization_context": {
    "workflow": "prescription_explain",
    "consent_flags": {
      "use_patient_context": true,
      "store_ai_trace": true
    },
    "context_scope": ["age", "known_conditions"]
  },
  "locale": {
    "language": "en",
    "country": "NG"
  },
  "input": {
    "prescription_text": "Amoxicillin 500 mg. Take one capsule three times daily for 7 days. For bacterial infection.",
    "patient_context": {
      "age": 35,
      "sex": "male",
      "known_conditions": [],
      "allergies": ["penicillin"],
      "current_medications": []
    }
  }
}
```

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `input.prescription_text` | string | Yes | Raw prescription text to explain |
| `input.patient_context` | object | No | Patient context for personalized explanation |

## Response

```json
{
  "request_id": "7d9827b8-9f42-4f4f-8e4a-3c4b4fd973a1",
  "status": "success",
  "workflow": "prescription_explain",
  "result": {
    "summary": "This prescription is for Amoxicillin, an antibiotic used to treat bacterial infections. Take as directed for the full course even if you feel better.",
    "sections": [
      {
        "title": "What is this medication?",
        "content": "Amoxicillin is a penicillin-type antibiotic that stops the growth of bacteria. It is commonly used for ear infections, sinusitis, pneumonia, and urinary tract infections.",
        "citation_ids": ["cit_1"]
      },
      {
        "title": "How to take it",
        "content": "Take one 500 mg capsule three times daily. Complete the full 7-day course even if symptoms improve. Take with or without food.",
        "citation_ids": ["cit_1"]
      },
      {
        "title": "Possible side effects",
        "content": "Common side effects include diarrhea, nausea, and skin rash. Seek medical attention if you experience severe allergic reaction (difficulty breathing, swelling of face or throat).",
        "citation_ids": ["cit_2"]
      }
    ],
    "warnings": [
      "You have listed a penicillin allergy. Please confirm with your doctor before taking this medication."
    ]
  },
  "safety": {
    "risk_level": "medium",
    "action": "answered",
    "requires_escalation": false,
    "requires_human_review": false
  },
  "citations": [
    {
      "citation_id": "cit_1",
      "text_content": "Amoxicillin 500 mg three times daily for 7-10 days is a standard adult dosage for common bacterial infections.",
      "score": 0.95,
      "source_name": "Nigeria Essential Medicine List",
      "source_version": "2020",
      "source_trust_tier": 1,
      "document_title": "Nigeria Essential Medicine List 2020",
      "section_path": "Section 6: Anti-infective Medicines",
      "page_number": 23
    }
  ],
  "confidence": {
    "overall": 0.86,
    "grounding": 0.9,
    "retrieval": 0.83
  },
  "audit": {
    "trace_id": "ai-trace-404",
    "prompt_version": "prescription_explain:v1",
    "model_provider": "provider-name",
    "model_version": "model-version"
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `result.summary` | string | High-level summary of the prescription |
| `result.sections[].title` | string | Section heading |
| `result.sections[].content` | string | Patient-friendly explanation |
| `result.warnings` | string[] | Important warnings (e.g. allergies, interactions) |

## Safety Rules

- Uses structured prescription data supplied by backend or OCR result
- Retrieves drug references for all claims
- Does not assume diagnosis unless supplied
- Warns when patient allergies or conditions conflict with the medication

## Status Codes

| Code | Description |
|------|-------------|
| `200` | Prescription explained successfully |
| `400` | Validation error |
| `401` | Missing or invalid API key |
| `422` | Invalid request body |
| `500` | Internal service error |

## Examples

### cURL

```bash
curl -X POST http://localhost:8000/v1/ai/prescriptions/explain \
  -H "Content-Type: application/json" \
  -H "X-Zam-AI-Key: <your-api-key>" \
  -d '{
    "actor_context": {
      "actor_type": "patient",
      "actor_id": "user-202",
      "role": "patient"
    },
    "input": {
      "prescription_text": "Amoxicillin 500 mg. Take one capsule three times daily for 7 days.",
      "patient_context": {
        "age": 35
      }
    }
  }'
```

### JavaScript (fetch)

```javascript
const response = await fetch('http://localhost:8000/v1/ai/prescriptions/explain', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Zam-AI-Key': '<your-api-key>'
  },
  body: JSON.stringify({
    actor_context: {
      actor_type: 'patient',
      actor_id: 'user-202',
      role: 'patient'
    },
    input: {
      prescription_text: 'Amoxicillin 500 mg. Take one capsule three times daily for 7 days.',
      patient_context: { age: 35 }
    }
  })
});

const data = await response.json();
console.log(data);
```

### Python (requests)

```python
import requests

response = requests.post(
    "http://localhost:8000/v1/ai/prescriptions/explain",
    headers={
        "Content-Type": "application/json",
        "X-Zam-AI-Key": "<your-api-key>"
    },
    json={
        "actor_context": {
            "actor_type": "patient",
            "actor_id": "user-202",
            "role": "patient"
        },
        "input": {
            "prescription_text": "Amoxicillin 500 mg. Take one capsule three times daily for 7 days.",
            "patient_context": {"age": 35}
        }
    }
)

print(response.json())
```

### Node.js (axios)

```javascript
const axios = require('axios');

const response = await axios.post('http://localhost:8000/v1/ai/prescriptions/explain', {
  actor_context: {
    actor_type: 'patient',
    actor_id: 'user-202',
    role: 'patient'
  },
  input: {
    prescription_text: 'Amoxicillin 500 mg. Take one capsule three times daily for 7 days.',
    patient_context: { age: 35 }
  }
}, {
  headers: {
    'Content-Type': 'application/json',
    'X-Zam-AI-Key': '<your-api-key>'
  }
});

console.log(response.data);
```

### Go

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io"
    "net/http"
)

func main() {
    body := map[string]interface{}{
        "actor_context": map[string]string{
            "actor_type": "patient",
            "actor_id":   "user-202",
            "role":       "patient",
        },
        "input": map[string]interface{}{
            "prescription_text": "Amoxicillin 500 mg. Take one capsule three times daily for 7 days.",
            "patient_context": map[string]interface{}{
                "age": 35,
            },
        },
    }
    jsonBody, _ := json.Marshal(body)
    req, _ := http.NewRequest("POST", "http://localhost:8000/v1/ai/prescriptions/explain", bytes.NewBuffer(jsonBody))
    req.Header.Set("Content-Type", "application/json")
    req.Header.Set("X-Zam-AI-Key", "<your-api-key>")

    client := &http.Client{}
    resp, _ := client.Do(req)
    defer resp.Body.Close()
    io.Copy(os.Stdout, resp.Body)
}
```

### PHP

```php
<?php
$ch = curl_init('http://localhost:8000/v1/ai/prescriptions/explain');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'X-Zam-AI-Key: <your-api-key>'
]);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
    'actor_context' => [
        'actor_type' => 'patient',
        'actor_id' => 'user-202',
        'role' => 'patient'
    ],
    'input' => [
        'prescription_text' => 'Amoxicillin 500 mg. Take one capsule three times daily for 7 days.',
        'patient_context' => ['age' => 35]
    ]
]));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
curl_close($ch);
echo $response;
```
