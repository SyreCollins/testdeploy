# Symptom Guidance

`POST /v1/ai/symptom-guidance`

Provides non-diagnostic symptom guidance and triage support.

## Purpose

Helps patients understand the urgency of their symptoms and provides appropriate guidance. The endpoint never provides a diagnosis — it triages, educates, and escalates. Red-flag symptoms (chest pain, difficulty breathing, stroke signs) trigger immediate emergency escalation.

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
    "actor_id": "user-456",
    "role": "patient"
  },
  "authorization_context": {
    "workflow": "symptom_guidance",
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
    "symptoms": "I have chest pain and shortness of breath",
    "patient_context": {
      "age": 55,
      "sex": "male",
      "known_conditions": ["hypertension"],
      "allergies": [],
      "current_medications": ["lisinopril"]
    }
  }
}
```

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `input.symptoms` | string | Yes | Description of symptoms |
| `input.patient_context` | object | No | Patient context for triage accuracy |

## Response

### Normal Response

```json
{
  "request_id": "7d9827b8-9f42-4f4f-8e4a-3c4b4fd973a1",
  "status": "success",
  "workflow": "symptom_guidance",
  "result": {
    "answer": "Based on the symptoms described, this appears to be a non-urgent issue. However, if symptoms worsen or persist, please consult a healthcare provider.",
    "triage_level": "non_urgent",
    "diagnosis_provided": false
  },
  "safety": {
    "risk_level": "low",
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
    "trace_id": "ai-trace-456",
    "prompt_version": "symptom_guidance:v1",
    "model_provider": "provider-name",
    "model_version": "model-version"
  }
}
```

### Emergency Response

```json
{
  "request_id": "7d9827b8-9f42-4f4f-8e4a-3c4b4fd973a1",
  "status": "success",
  "workflow": "symptom_guidance",
  "result": {
    "answer": "Chest pain with shortness of breath can be urgent. Please seek emergency medical care now or contact local emergency services.",
    "triage_level": "emergency",
    "diagnosis_provided": false
  },
  "safety": {
    "risk_level": "emergency",
    "action": "escalated",
    "requires_escalation": true,
    "requires_human_review": false
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `result.answer` | string | Guidance or triage instruction |
| `result.triage_level` | string | `"emergency"`, `"urgent"`, `"non_urgent"`, or `"self_care"` |
| `result.diagnosis_provided` | boolean | Always `false` — no diagnosis is ever given |
| `safety.risk_level` | string | Risk classification |
| `safety.action` | string | `"answered"`, `"escalated"`, or `"refused"` |

## Safety Rules

- Never provides a diagnosis
- Escalates red-flag symptoms immediately (chest pain, stroke signs, severe bleeding, difficulty breathing)
- Asks clarifying questions only when it does not delay urgent care
- Refuses unsupported symptom queries

## Status Codes

| Code | Description |
|------|-------------|
| `200` | Guidance generated successfully |
| `400` | Validation error |
| `401` | Missing or invalid API key |
| `422` | Invalid request body |
| `500` | Internal service error |

## Examples

### cURL

```bash
curl -X POST http://localhost:8000/v1/ai/symptom-guidance \
  -H "Content-Type: application/json" \
  -H "X-Zam-AI-Key: <your-api-key>" \
  -d '{
    "actor_context": {
      "actor_type": "patient",
      "actor_id": "user-456",
      "role": "patient"
    },
    "input": {
      "symptoms": "I have a mild headache and feel tired",
      "patient_context": {
        "age": 30
      }
    }
  }'
```

### JavaScript (fetch)

```javascript
const response = await fetch('http://localhost:8000/v1/ai/symptom-guidance', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Zam-AI-Key': '<your-api-key>'
  },
  body: JSON.stringify({
    actor_context: {
      actor_type: 'patient',
      actor_id: 'user-456',
      role: 'patient'
    },
    input: {
      symptoms: 'I have a mild headache and feel tired',
      patient_context: { age: 30 }
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
    "http://localhost:8000/v1/ai/symptom-guidance",
    headers={
        "Content-Type": "application/json",
        "X-Zam-AI-Key": "<your-api-key>"
    },
    json={
        "actor_context": {
            "actor_type": "patient",
            "actor_id": "user-456",
            "role": "patient"
        },
        "input": {
            "symptoms": "I have a mild headache and feel tired",
            "patient_context": {"age": 30}
        }
    }
)

print(response.json())
```

### Node.js (axios)

```javascript
const axios = require('axios');

const response = await axios.post('http://localhost:8000/v1/ai/symptom-guidance', {
  actor_context: {
    actor_type: 'patient',
    actor_id: 'user-456',
    role: 'patient'
  },
  input: {
    symptoms: 'I have a mild headache and feel tired',
    patient_context: { age: 30 }
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
            "actor_id":   "user-456",
            "role":       "patient",
        },
        "input": map[string]interface{}{
            "symptoms": "I have a mild headache and feel tired",
            "patient_context": map[string]interface{}{
                "age": 30,
            },
        },
    }
    jsonBody, _ := json.Marshal(body)
    req, _ := http.NewRequest("POST", "http://localhost:8000/v1/ai/symptom-guidance", bytes.NewBuffer(jsonBody))
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
$ch = curl_init('http://localhost:8000/v1/ai/symptom-guidance');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'X-Zam-AI-Key: <your-api-key>'
]);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
    'actor_context' => [
        'actor_type' => 'patient',
        'actor_id' => 'user-456',
        'role' => 'patient'
    ],
    'input' => [
        'symptoms' => 'I have a mild headache and feel tired',
        'patient_context' => ['age' => 30]
    ]
]));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
curl_close($ch);
echo $response;
```
