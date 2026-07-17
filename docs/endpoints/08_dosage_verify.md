# Dosage Verification

`POST /v1/ai/dosage/verify`

Compares supplied dosage instructions against approved reference sources.

## Purpose

Helps verify that prescribed or patient-reported dosages fall within typical ranges for the given medication and patient context. The endpoint does not prescribe new doses — it only compares supplied instructions against references.

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
    "workflow": "dosage_verify",
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
    "medication": {
      "name": "amoxicillin",
      "strength": "500 mg",
      "instructions": "Take one capsule three times daily for 7 days"
    },
    "patient_context": {
      "age": 35,
      "sex": "male",
      "known_conditions": [],
      "allergies": [],
      "current_medications": []
    }
  }
}
```

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `input.medication.name` | string | Yes | Medication name |
| `input.medication.strength` | string | No | Medication strength (e.g. "500 mg") |
| `input.medication.instructions` | string | No | Dosage instructions to verify |
| `input.patient_context` | object | No | Patient context for personalized verification |

## Response

```json
{
  "request_id": "7d9827b8-9f42-4f4f-8e4a-3c4b4fd973a1",
  "status": "success",
  "workflow": "dosage_verify",
  "result": {
    "dosages": [
      {
        "medication_name": "amoxicillin",
        "stated_dosage": "500 mg three times daily for 7 days",
        "assessment": "within_typical_range",
        "typical_range": "250-500 mg three times daily for 7-10 days",
        "flags": [],
        "citation_ids": ["cit_1"]
      }
    ],
    "missing_context": ["weight_kg", "renal_impairment"]
  },
  "safety": {
    "risk_level": "low",
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
    "overall": 0.88,
    "grounding": 0.92,
    "retrieval": 0.85
  },
  "audit": {
    "trace_id": "ai-trace-303",
    "prompt_version": "dosage_verify:v1",
    "model_provider": "provider-name",
    "model_version": "model-version"
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `result.dosages[].medication_name` | string | Normalized medication name |
| `result.dosages[].stated_dosage` | string | The dosage instructions as provided |
| `result.dosages[].assessment` | string | `"within_typical_range"`, `"outside_typical_range"`, `"insufficient_data"`, or `"unknown"` |
| `result.dosages[].typical_range` | string | Typical dosage range from references |
| `result.dosages[].flags` | string[] | Any warnings or concerns |
| `result.missing_context` | string[] | Patient parameters that would improve verification |

## Safety Rules

- Does not prescribe new doses
- Flags unusual or unsupported doses
- Requires review when patient-specific parameters are missing
- All assessments are comparative, not prescriptive

## Status Codes

| Code | Description |
|------|-------------|
| `200` | Dosage verification completed |
| `400` | Validation error |
| `401` | Missing or invalid API key |
| `422` | Invalid request body |
| `500` | Internal service error |

## Examples

### cURL

```bash
curl -X POST http://localhost:8000/v1/ai/dosage/verify \
  -H "Content-Type: application/json" \
  -H "X-Zam-AI-Key: <your-api-key>" \
  -d '{
    "actor_context": {
      "actor_type": "doctor",
      "actor_id": "dr-789",
      "role": "clinician"
    },
    "input": {
      "medication": {
        "name": "amoxicillin",
        "strength": "500 mg",
        "instructions": "Take one capsule three times daily for 7 days"
      },
      "patient_context": {
        "age": 35
      }
    }
  }'
```

### JavaScript (fetch)

```javascript
const response = await fetch('http://localhost:8000/v1/ai/dosage/verify', {
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
      medication: {
        name: 'amoxicillin',
        strength: '500 mg',
        instructions: 'Take one capsule three times daily for 7 days'
      },
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
    "http://localhost:8000/v1/ai/dosage/verify",
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
            "medication": {
                "name": "amoxicillin",
                "strength": "500 mg",
                "instructions": "Take one capsule three times daily for 7 days"
            },
            "patient_context": {"age": 35}
        }
    }
)

print(response.json())
```

### Node.js (axios)

```javascript
const axios = require('axios');

const response = await axios.post('http://localhost:8000/v1/ai/dosage/verify', {
  actor_context: {
    actor_type: 'doctor',
    actor_id: 'dr-789',
    role: 'clinician'
  },
  input: {
    medication: {
      name: 'amoxicillin',
      strength: '500 mg',
      instructions: 'Take one capsule three times daily for 7 days'
    },
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
            "actor_type": "doctor",
            "actor_id":   "dr-789",
            "role":       "clinician",
        },
        "input": map[string]interface{}{
            "medication": map[string]interface{}{
                "name":         "amoxicillin",
                "strength":     "500 mg",
                "instructions": "Take one capsule three times daily for 7 days",
            },
            "patient_context": map[string]interface{}{
                "age": 35,
            },
        },
    }
    jsonBody, _ := json.Marshal(body)
    req, _ := http.NewRequest("POST", "http://localhost:8000/v1/ai/dosage/verify", bytes.NewBuffer(jsonBody))
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
$ch = curl_init('http://localhost:8000/v1/ai/dosage/verify');
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
        'medication' => [
            'name' => 'amoxicillin',
            'strength' => '500 mg',
            'instructions' => 'Take one capsule three times daily for 7 days'
        ],
        'patient_context' => ['age' => 35]
    ]
]));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
curl_close($ch);
echo $response;
```
