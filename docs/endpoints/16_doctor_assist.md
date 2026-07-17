# Doctor Assistant

`POST /v1/ai/doctor/assist`

> **Status: Planned** — Not yet implemented.

Supports clinician-facing workflows including medication review, patient summaries, interaction review, and patient education drafts.

## Purpose

Provides AI-assisted clinical support for doctors. Responses distinguish between source-backed facts, patient-supplied context, and AI-generated synthesis.

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
    "actor_id": "dr-789",
    "role": "clinician"
  },
  "authorization_context": {
    "workflow": "doctor_assist",
    "consent_flags": {
      "use_patient_context": true,
      "store_ai_trace": true
    },
    "context_scope": ["age", "known_conditions", "current_medications"]
  },
  "locale": {
    "language": "en",
    "country": "NG"
  },
  "input": {
    "task_type": "medication_review",
    "patient_context": {
      "age": 68,
      "sex": "male",
      "known_conditions": ["atrial fibrillation", "hypertension"],
      "allergies": [],
      "current_medications": ["warfarin", "lisinopril", "atorvastatin"]
    },
    "task_params": {}
  }
}
```

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `input.task_type` | string | Yes | Type of assistant task |
| `input.patient_context` | object | Yes | Patient medical context |
| `input.task_params` | object | No | Task-specific parameters |

## Supported Task Types

| Task Type | Description |
|-----------|-------------|
| `medication_review` | Review current medications for issues |
| `patient_summary` | Generate a concise patient summary |
| `interaction_review` | Review all medications for interactions |
| `contraindication_review` | Review all medications for contraindications |
| `patient_education_draft` | Draft patient education materials |

## Response

```json
{
  "request_id": "7d9827b8-9f42-4f4f-8e4a-3c4b4fd973a1",
  "status": "success",
  "workflow": "doctor_assist",
  "result": {
    "task_type": "medication_review",
    "summary": "Patient is on 3 medications. Warfarin and ibuprofen have a major interaction. Consider alternative analgesia.",
    "findings": [
      {
        "type": "interaction",
        "severity": "major",
        "description": "Warfarin and ibuprofen combination increases bleeding risk.",
        "citation_ids": ["cit_1"]
      }
    ],
    "recommendations": [
      "Consider paracetamol as alternative to ibuprofen",
      "Monitor INR if warfarin is continued"
    ]
  },
  "safety": {
    "risk_level": "medium",
    "action": "answered",
    "requires_escalation": false,
    "requires_human_review": false
  },
  "citations": [],
  "confidence": {
    "overall": 0.85,
    "grounding": 0.88,
    "retrieval": 0.82
  },
  "audit": {
    "trace_id": "ai-trace-707",
    "prompt_version": "doctor_assist:v1",
    "model_provider": "provider-name",
    "model_version": "model-version"
  }
}
```

## Safety Rules

- Distinguishes source-backed facts, patient-supplied context, and AI-generated synthesis
- All clinical claims require source evidence
- Does not replace clinical judgment

## Examples

### cURL

```bash
curl -X POST http://localhost:8000/v1/ai/doctor/assist \
  -H "Content-Type: application/json" \
  -H "X-Zam-AI-Key: <your-api-key>" \
  -d '{
    "actor_context": {
      "actor_type": "doctor",
      "actor_id": "dr-789",
      "role": "clinician"
    },
    "input": {
      "task_type": "medication_review",
      "patient_context": {
        "age": 68,
        "known_conditions": ["atrial fibrillation", "hypertension"],
        "current_medications": ["warfarin", "lisinopril", "atorvastatin"]
      }
    }
  }'
```

### JavaScript (fetch)

```javascript
const response = await fetch('http://localhost:8000/v1/ai/doctor/assist', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Zam-AI-Key': '<your-api-key>'
  },
  body: JSON.stringify({
    actor_context: {
      actor_type: 'doctor',
      actor_id: 'dr-789',
      role: 'clinician'
    },
    input: {
      task_type: 'medication_review',
      patient_context: {
        age: 68,
        known_conditions: ['atrial fibrillation', 'hypertension'],
        current_medications: ['warfarin', 'lisinopril', 'atorvastatin']
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
    "http://localhost:8000/v1/ai/doctor/assist",
    headers={
        "Content-Type": "application/json",
        "X-Zam-AI-Key": "<your-api-key>"
    },
    json={
        "actor_context": {
            "actor_type": "doctor",
            "actor_id": "dr-789",
            "role": "clinician"
        },
        "input": {
            "task_type": "medication_review",
            "patient_context": {
                "age": 68,
                "known_conditions": ["atrial fibrillation", "hypertension"],
                "current_medications": ["warfarin", "lisinopril", "atorvastatin"]
            }
        }
    }
)

print(response.json())
```

### Node.js (axios)

```javascript
const axios = require('axios');

const response = await axios.post('http://localhost:8000/v1/ai/doctor/assist', {
  actor_context: {
    actor_type: 'doctor',
    actor_id: 'dr-789',
    role: 'clinician'
  },
  input: {
    task_type: 'medication_review',
    patient_context: {
      age: 68,
      known_conditions: ['atrial fibrillation', 'hypertension'],
      current_medications: ['warfarin', 'lisinopril', 'atorvastatin']
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
            "actor_id":   "dr-789",
            "role":       "clinician",
        },
        "input": map[string]interface{}{
            "task_type": "medication_review",
            "patient_context": map[string]interface{}{
                "age":                 68,
                "known_conditions":    []string{"atrial fibrillation", "hypertension"},
                "current_medications": []string{"warfarin", "lisinopril", "atorvastatin"},
            },
        },
    }
    jsonBody, _ := json.Marshal(body)
    req, _ := http.NewRequest("POST", "http://localhost:8000/v1/ai/doctor/assist", bytes.NewBuffer(jsonBody))
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
$ch = curl_init('http://localhost:8000/v1/ai/doctor/assist');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'X-Zam-AI-Key: <your-api-key>'
]);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
    'actor_context' => [
        'actor_type' => 'doctor',
        'actor_id' => 'dr-789',
        'role' => 'clinician'
    ],
    'input' => [
        'task_type' => 'medication_review',
        'patient_context' => [
            'age' => 68,
            'known_conditions' => ['atrial fibrillation', 'hypertension'],
            'current_medications' => ['warfarin', 'lisinopril', 'atorvastatin']
        ]
    ]
]));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
curl_close($ch);
echo $response;
```

| Code | Description |
|------|-------------|
| `200` | Assistant response generated |
| `400` | Validation error |
| `401` | Missing or invalid API key |
| `422` | Invalid request body |
| `500` | Internal service error |
