# Pharmacy Assistant

`POST /v1/ai/pharmacy/assist`

> **Status: Planned** — Not yet implemented.

Supports pharmacy-facing medication intelligence workflows.

## Purpose

Provides AI-assisted support for pharmacists including drug explanations, interaction reviews, alternative recommendations, and inventory contextualization.

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
    "actor_type": "pharmacy",
    "actor_id": "pharm-202",
    "role": "pharmacist"
  },
  "authorization_context": {
    "workflow": "pharmacy_assist",
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
    "task_type": "drug_explanation",
    "medication_name": "Augmentin",
    "patient_context": {
      "age": 35,
      "known_conditions": [],
      "allergies": ["penicillin"]
    },
    "task_params": {}
  }
}
```

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `input.task_type` | string | Yes | Type of pharmacy task |
| `input.medication_name` | string | No | Medication name (if applicable) |
| `input.patient_context` | object | No | Patient context |
| `input.task_params` | object | No | Task-specific parameters |

## Supported Task Types

| Task Type | Description |
|-----------|-------------|
| `drug_explanation` | Explain a medication to a patient |
| `interaction_review` | Review all medications for interactions |
| `alternative_review` | Suggest therapeutic alternatives |
| `inventory_contextualization` | Contextualize inventory availability |

## Response

```json
{
  "request_id": "7d9827b8-9f42-4f4f-8e4a-3c4b4fd973a1",
  "status": "success",
  "workflow": "pharmacy_assist",
  "result": {
    "task_type": "drug_explanation",
    "summary": "Augmentin (amoxicillin/clavulanate) is a broad-spectrum antibiotic. Patient has listed penicillin allergy — verify before dispensing.",
    "findings": [
      {
        "type": "allergy_warning",
        "severity": "high",
        "description": "Patient has listed penicillin allergy. Augmentin contains amoxicillin (a penicillin).",
        "citation_ids": ["cit_1"]
      }
    ],
    "recommendations": [
      "Verify allergy status with patient before dispensing",
      "Consider alternative antibiotic if allergy is confirmed"
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
    "trace_id": "ai-trace-808",
    "prompt_version": "pharmacy_assist:v1",
    "model_provider": "provider-name",
    "model_version": "model-version"
  }
}
```

## Safety Rules

- Inventory availability is not clinical equivalence
- Alternative recommendations require source-backed clinical rationale
- Pharmacist review metadata is returned for substitution workflows

## Examples

### cURL

```bash
curl -X POST http://localhost:8000/v1/ai/pharmacy/assist \
  -H "Content-Type: application/json" \
  -H "X-Zam-AI-Key: <your-api-key>" \
  -d '{
    "actor_context": {
      "actor_type": "pharmacy",
      "actor_id": "pharm-202",
      "role": "pharmacist"
    },
    "input": {
      "task_type": "drug_explanation",
      "medication_name": "Augmentin",
      "patient_context": {
        "age": 35,
        "allergies": ["penicillin"]
      }
    }
  }'
```

### JavaScript (fetch)

```javascript
const response = await fetch('http://localhost:8000/v1/ai/pharmacy/assist', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Zam-AI-Key': '<your-api-key>'
  },
  body: JSON.stringify({
    actor_context: {
      actor_type: 'pharmacy',
      actor_id: 'pharm-202',
      role: 'pharmacist'
    },
    input: {
      task_type: 'drug_explanation',
      medication_name: 'Augmentin',
      patient_context: {
        age: 35,
        allergies: ['penicillin']
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
    "http://localhost:8000/v1/ai/pharmacy/assist",
    headers={
        "Content-Type": "application/json",
        "X-Zam-AI-Key": "<your-api-key>"
    },
    json={
        "actor_context": {
            "actor_type": "pharmacy",
            "actor_id": "pharm-202",
            "role": "pharmacist"
        },
        "input": {
            "task_type": "drug_explanation",
            "medication_name": "Augmentin",
            "patient_context": {
                "age": 35,
                "allergies": ["penicillin"]
            }
        }
    }
)

print(response.json())
```

### Node.js (axios)

```javascript
const axios = require('axios');

const response = await axios.post('http://localhost:8000/v1/ai/pharmacy/assist', {
  actor_context: {
    actor_type: 'pharmacy',
    actor_id: 'pharm-202',
    role: 'pharmacist'
  },
  input: {
    task_type: 'drug_explanation',
    medication_name: 'Augmentin',
    patient_context: {
      age: 35,
      allergies: ['penicillin']
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
            "actor_type": "pharmacy",
            "actor_id":   "pharm-202",
            "role":       "pharmacist",
        },
        "input": map[string]interface{}{
            "task_type":       "drug_explanation",
            "medication_name": "Augmentin",
            "patient_context": map[string]interface{}{
                "age":       35,
                "allergies": []string{"penicillin"},
            },
        },
    }
    jsonBody, _ := json.Marshal(body)
    req, _ := http.NewRequest("POST", "http://localhost:8000/v1/ai/pharmacy/assist", bytes.NewBuffer(jsonBody))
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
$ch = curl_init('http://localhost:8000/v1/ai/pharmacy/assist');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'X-Zam-AI-Key: <your-api-key>'
]);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
    'actor_context' => [
        'actor_type' => 'pharmacy',
        'actor_id' => 'pharm-202',
        'role' => 'pharmacist'
    ],
    'input' => [
        'task_type' => 'drug_explanation',
        'medication_name' => 'Augmentin',
        'patient_context' => [
            'age' => 35,
            'allergies' => ['penicillin']
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
