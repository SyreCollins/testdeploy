# Interaction Check

`POST /v1/ai/interactions/check`

Checks for potential interactions between two or more medications.

## Purpose

Identifies known drug-drug interactions using approved interaction data sources. Returns severity levels, summaries, and recommended actions. Medications that cannot be normalized are returned in the `unknowns` list.

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
    "actor_id": "user-101",
    "role": "patient"
  },
  "authorization_context": {
    "workflow": "interaction_check",
    "consent_flags": {
      "use_patient_context": true,
      "store_ai_trace": true
    },
    "context_scope": ["age"]
  },
  "locale": {
    "language": "en",
    "country": "NG"
  },
  "input": {
    "medications": [
      { "name": "warfarin", "dose": null },
      { "name": "ibuprofen", "dose": null }
    ],
    "patient_context": {
      "age": 68,
      "sex": "male",
      "known_conditions": ["atrial fibrillation"],
      "allergies": [],
      "current_medications": []
    }
  }
}
```

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `input.medications` | object[] | Yes | At least 2 medications to check |
| `input.medications[].name` | string | Yes | Medication name |
| `input.medications[].dose` | string | No | Optional dose information |
| `input.patient_context` | object | No | Patient context for personalized assessment |

## Response

```json
{
  "request_id": "7d9827b8-9f42-4f4f-8e4a-3c4b4fd973a1",
  "status": "success",
  "workflow": "interaction_check",
  "result": {
    "interactions": [
      {
        "medications": ["warfarin", "ibuprofen"],
        "severity": "major",
        "summary": "This combination may increase bleeding risk. Monitor INR closely and consider alternative analgesia.",
        "recommended_action": "consult_clinician_or_pharmacist",
        "citation_ids": ["cit_1"]
      }
    ],
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
      "text_content": "NSAIDs may potentiate the effect of warfarin, increasing bleeding risk. Monitor INR closely.",
      "score": 0.93,
      "source_name": "Nigeria Essential Medicine List",
      "source_version": "2020",
      "source_trust_tier": 1,
      "document_title": "Nigeria Essential Medicine List 2020",
      "section_path": "Appendix: Drug Interactions",
      "page_number": 112
    }
  ],
  "confidence": {
    "overall": 0.87,
    "grounding": 0.91,
    "retrieval": 0.84
  },
  "audit": {
    "trace_id": "ai-trace-101",
    "prompt_version": "interaction_check:v1",
    "model_provider": "provider-name",
    "model_version": "model-version"
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `result.interactions[].medications` | string[] | The medication pair involved |
| `result.interactions[].severity` | string | `"major"`, `"moderate"`, `"minor"`, or `"none"` |
| `result.interactions[].summary` | string | Human-readable interaction description |
| `result.interactions[].recommended_action` | string | Recommended next step |
| `result.unknowns` | string[] | Medications that could not be normalized |

## Safety Rules

- Uses deterministic interaction data where available
- Never invents interaction severity
- Returns `unknowns` for medications that cannot be normalized
- Missing patient context is reported but does not block the check

## Status Codes

| Code | Description |
|------|-------------|
| `200` | Interaction check completed |
| `400` | Validation error (fewer than 2 medications) |
| `401` | Missing or invalid API key |
| `422` | Invalid request body |
| `500` | Internal service error |

## Examples

### cURL

```bash
curl -X POST http://localhost:8000/v1/ai/interactions/check \
  -H "Content-Type: application/json" \
  -H "X-Zam-AI-Key: <your-api-key>" \
  -d '{
    "actor_context": {
      "actor_type": "patient",
      "actor_id": "user-101",
      "role": "patient"
    },
    "input": {
      "medications": [
        { "name": "warfarin" },
        { "name": "ibuprofen" }
      ],
      "patient_context": {
        "age": 68
      }
    }
  }'
```

### JavaScript (fetch)

```javascript
const response = await fetch('http://localhost:8000/v1/ai/interactions/check', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Zam-AI-Key': '<your-api-key>'
  },
  body: JSON.stringify({
    actor_context: {
      actor_type: 'patient',
      actor_id: 'user-101',
      role: 'patient'
    },
    input: {
      medications: [
        { name: 'warfarin' },
        { name: 'ibuprofen' }
      ],
      patient_context: { age: 68 }
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
    "http://localhost:8000/v1/ai/interactions/check",
    headers={
        "Content-Type": "application/json",
        "X-Zam-AI-Key": "<your-api-key>"
    },
    json={
        "actor_context": {
            "actor_type": "patient",
            "actor_id": "user-101",
            "role": "patient"
        },
        "input": {
            "medications": [
                {"name": "warfarin"},
                {"name": "ibuprofen"}
            ],
            "patient_context": {"age": 68}
        }
    }
)

print(response.json())
```

### Node.js (axios)

```javascript
const axios = require('axios');

const response = await axios.post('http://localhost:8000/v1/ai/interactions/check', {
  actor_context: {
    actor_type: 'patient',
    actor_id: 'user-101',
    role: 'patient'
  },
  input: {
    medications: [
      { name: 'warfarin' },
      { name: 'ibuprofen' }
    ],
    patient_context: { age: 68 }
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
            "actor_id":   "user-101",
            "role":       "patient",
        },
        "input": map[string]interface{}{
            "medications": []map[string]string{
                {"name": "warfarin"},
                {"name": "ibuprofen"},
            },
            "patient_context": map[string]interface{}{
                "age": 68,
            },
        },
    }
    jsonBody, _ := json.Marshal(body)
    req, _ := http.NewRequest("POST", "http://localhost:8000/v1/ai/interactions/check", bytes.NewBuffer(jsonBody))
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
$ch = curl_init('http://localhost:8000/v1/ai/interactions/check');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'X-Zam-AI-Key: <your-api-key>'
]);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
    'actor_context' => [
        'actor_type' => 'patient',
        'actor_id' => 'user-101',
        'role' => 'patient'
    ],
    'input' => [
        'medications' => [
            ['name' => 'warfarin'],
            ['name' => 'ibuprofen']
        ],
        'patient_context' => ['age' => 68]
    ]
]));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
curl_close($ch);
echo $response;
```
