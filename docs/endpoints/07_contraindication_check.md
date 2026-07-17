# Contraindication Check

`POST /v1/ai/contraindications/check`

Checks whether supplied medications may be contraindicated for a given patient context.

## Purpose

Identifies potential contraindications between medications and patient conditions, allergies, or other factors. Returns evidence-backed findings and flags missing context that would improve accuracy.

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
    "actor_type": "doctor",
    "actor_id": "dr-456",
    "role": "clinician"
  },
  "authorization_context": {
    "workflow": "contraindication_check",
    "consent_flags": {
      "use_patient_context": true,
      "store_ai_trace": true
    },
    "context_scope": ["known_conditions", "allergies"]
  },
  "locale": {
    "language": "en",
    "country": "NG"
  },
  "input": {
    "medications": [
      { "name": "ibuprofen" }
    ],
    "patient_context": {
      "age": 45,
      "sex": "female",
      "known_conditions": ["peptic ulcer disease"],
      "allergies": [],
      "current_medications": []
    }
  }
}
```

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `input.medications` | object[] | Yes | At least 1 medication to check |
| `input.medications[].name` | string | Yes | Medication name |
| `input.patient_context` | object | No | Patient medical context |

## Response

```json
{
  "request_id": "7d9827b8-9f42-4f4f-8e4a-3c4b4fd973a1",
  "status": "success",
  "workflow": "contraindication_check",
  "result": {
    "contraindications": [
      {
        "medication": "ibuprofen",
        "condition": "peptic ulcer disease",
        "severity": "major",
        "reason": "NSAIDs can exacerbate or cause gastrointestinal bleeding in patients with peptic ulcer disease.",
        "evidence_summary": "Multiple clinical guidelines recommend avoiding NSAIDs in patients with active or history of peptic ulcer disease.",
        "citation_ids": ["cit_1"]
      }
    ],
    "missing_context": ["pregnancy_status"],
    "unknowns": []
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
      "text_content": "NSAIDs are contraindicated in patients with active peptic ulcer disease due to increased risk of gastrointestinal bleeding.",
      "score": 0.96,
      "source_name": "Nigeria Essential Medicine List",
      "source_version": "2020",
      "source_trust_tier": 1,
      "document_title": "Nigeria Essential Medicine List 2020",
      "section_path": "Chapter 2: Analgesics",
      "page_number": 45
    }
  ],
  "confidence": {
    "overall": 0.85,
    "grounding": 0.9,
    "retrieval": 0.8
  },
  "audit": {
    "trace_id": "ai-trace-202",
    "prompt_version": "contraindication_check:v1",
    "model_provider": "provider-name",
    "model_version": "model-version"
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `result.contraindications[].medication` | string | The medication with a contraindication |
| `result.contraindications[].condition` | string | The patient condition causing the contraindication |
| `result.contraindications[].severity` | string | `"major"`, `"moderate"`, or `"minor"` |
| `result.contraindications[].reason` | string | Explanation of the contraindication |
| `result.contraindications[].evidence_summary` | string | Summary of supporting evidence |
| `result.missing_context` | string[] | Patient context fields that would improve accuracy |
| `result.unknowns` | string[] | Medications that could not be evaluated |

## Safety Rules

- Missing patient context is reported in `missing_context`
- Contraindications require source evidence
- High-risk findings include escalation or review metadata

## Status Codes

| Code | Description |
|------|-------------|
| `200` | Contraindication check completed |
| `400` | Validation error |
| `401` | Missing or invalid API key |
| `422` | Invalid request body |
| `500` | Internal service error |

## Examples

### cURL

```bash
curl -X POST http://localhost:8000/v1/ai/contraindications/check \
  -H "Content-Type: application/json" \
  -H "X-Zam-AI-Key: <your-api-key>" \
  -d '{
    "actor_context": {
      "actor_type": "doctor",
      "actor_id": "dr-456",
      "role": "clinician"
    },
    "input": {
      "medications": [{ "name": "ibuprofen" }],
      "patient_context": {
        "known_conditions": ["peptic ulcer disease"]
      }
    }
  }'
```

### JavaScript (fetch)

```javascript
const response = await fetch('http://localhost:8000/v1/ai/contraindications/check', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Zam-AI-Key': '<your-api-key>'
  },
  body: JSON.stringify({
    actor_context: {
      actor_type: 'doctor',
      actor_id: 'dr-456',
      role: 'clinician'
    },
    input: {
      medications: [{ name: 'ibuprofen' }],
      patient_context: {
        known_conditions: ['peptic ulcer disease']
      }
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
    "http://localhost:8000/v1/ai/contraindications/check",
    headers={
        "Content-Type": "application/json",
        "X-Zam-AI-Key": "<your-api-key>"
    },
    json={
        "actor_context": {
            "actor_type": "doctor",
            "actor_id": "dr-456",
            "role": "clinician"
        },
        "input": {
            "medications": [{"name": "ibuprofen"}],
            "patient_context": {
                "known_conditions": ["peptic ulcer disease"]
            }
        }
    }
)

print(response.json())
```

### Node.js (axios)

```javascript
const axios = require('axios');

const response = await axios.post('http://localhost:8000/v1/ai/contraindications/check', {
  actor_context: {
    actor_type: 'doctor',
    actor_id: 'dr-456',
    role: 'clinician'
  },
  input: {
    medications: [{ name: 'ibuprofen' }],
    patient_context: {
      known_conditions: ['peptic ulcer disease']
    }
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
            "actor_type": "doctor",
            "actor_id":   "dr-456",
            "role":       "clinician",
        },
        "input": map[string]interface{}{
            "medications": []map[string]string{
                {"name": "ibuprofen"},
            },
            "patient_context": map[string]interface{}{
                "known_conditions": []string{"peptic ulcer disease"},
            },
        },
    }
    jsonBody, _ := json.Marshal(body)
    req, _ := http.NewRequest("POST", "http://localhost:8000/v1/ai/contraindications/check", bytes.NewBuffer(jsonBody))
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
$ch = curl_init('http://localhost:8000/v1/ai/contraindications/check');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'X-Zam-AI-Key: <your-api-key>'
]);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
    'actor_context' => [
        'actor_type' => 'doctor',
        'actor_id' => 'dr-456',
        'role' => 'clinician'
    ],
    'input' => [
        'medications' => [['name' => 'ibuprofen']],
        'patient_context' => [
            'known_conditions' => ['peptic ulcer disease']
        ]
    ]
]));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
curl_close($ch);
echo $response;
```
