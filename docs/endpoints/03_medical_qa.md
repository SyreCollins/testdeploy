# Medical Q&A

`POST /v1/ai/medical-qa`

Answer a medical question using verified retrieved evidence from approved medical sources.

## Purpose

Provides grounded, source-backed answers to patient medical questions. Every medical claim must cite an approved source. The endpoint refuses to answer if no reliable evidence is found.

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
    "actor_id": "backend-user-ref",
    "organization_id": null,
    "role": "patient"
  },
  "authorization_context": {
    "workflow": "medical_qa",
    "consent_flags": {
      "use_patient_context": true,
      "store_ai_trace": true
    },
    "context_scope": ["age", "allergies", "current_medications"]
  },
  "locale": {
    "language": "en",
    "country": "NG"
  },
  "input": {
    "question": "Can I take ibuprofen if I have stomach ulcers?",
    "patient_context": {
      "age": 42,
      "sex": "female",
      "known_conditions": ["peptic ulcer disease"],
      "allergies": [],
      "current_medications": []
    },
    "conversation_context": {
      "conversation_id": "conv_123",
      "recent_messages": []
    }
  }
}
```

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `request_id` | string | No | Client-generated UUID for tracing |
| `caller.service` | string | No | Name of the calling service |
| `caller.environment` | string | No | Environment of the caller |
| `actor_context.actor_type` | string | Yes | Type of end user (`patient`, `doctor`, `pharmacy`) |
| `actor_context.actor_id` | string | Yes | Backend user reference identifier |
| `actor_context.role` | string | Yes | Role of the end user |
| `input.question` | string | Yes | The medical question to answer |
| `input.patient_context.age` | int | No | Patient age |
| `input.patient_context.sex` | string | No | Patient sex |
| `input.patient_context.known_conditions` | string[] | No | List of known medical conditions |
| `input.patient_context.allergies` | string[] | No | List of known allergies |
| `input.patient_context.current_medications` | string[] | No | List of current medications |
| `input.conversation_context.conversation_id` | string | No | Conversation ID for multi-turn context |
| `input.conversation_context.recent_messages` | object[] | No | Recent messages for context |

## Response

```json
{
  "request_id": "7d9827b8-9f42-4f4f-8e4a-3c4b4fd973a1",
  "status": "success",
  "workflow": "medical_qa",
  "result": {
    "answer": "Ibuprofen may not be appropriate for some people with a history of stomach ulcers. Please speak with a clinician or pharmacist before taking it, especially if you have active ulcer symptoms or are taking other medicines that increase bleeding risk.",
    "missing_context": [],
    "follow_up_questions": [],
    "medical_claims": [
      {
        "claim": "Ibuprofen can increase gastrointestinal bleeding or ulcer risk in susceptible patients.",
        "citation_ids": ["cit_1"]
      }
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
      "text_content": "NSAIDs including ibuprofen may increase risk of gastrointestinal bleeding in patients with a history of peptic ulcer disease.",
      "score": 0.94,
      "source_name": "Nigeria Essential Medicine List",
      "source_version": "2020",
      "source_trust_tier": 1,
      "document_title": "Nigeria Essential Medicine List 2020",
      "section_path": "Chapter 2: Analgesics",
      "page_number": 45
    }
  ],
  "confidence": {
    "overall": 0.82,
    "grounding": 0.9,
    "retrieval": 0.86
  },
  "audit": {
    "trace_id": "ai-trace-123",
    "prompt_version": "medical_qa:v1",
    "model_provider": "provider-name",
    "model_version": "model-version"
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `request_id` | string | Echoed from request for tracing |
| `status` | string | `"success"` or `"error"` |
| `workflow` | string | Workflow identifier |
| `result.answer` | string | The grounded medical answer |
| `result.missing_context` | string[] | Context fields that would improve the answer |
| `result.follow_up_questions` | string[] | Suggested follow-up questions |
| `result.medical_claims` | object[] | Individual medical claims with citations |
| `safety.risk_level` | string | `"low"`, `"medium"`, `"high"`, or `"emergency"` |
| `safety.action` | string | `"answered"`, `"refused"`, or `"escalated"` |
| `citations` | object[] | Source citations for claims made |
| `confidence.overall` | float | Overall confidence score (0-1) |
| `confidence.grounding` | float | Grounding confidence score (0-1) |
| `confidence.retrieval` | float | Retrieval confidence score (0-1) |
| `audit.trace_id` | string | Audit trace identifier |

## Safety Rules

- Must retrieve approved sources before answering
- Every medical claim must cite a source
- Refuses if no reliable evidence is found
- Escalates emergency symptoms immediately

## Status Codes

| Code | Description |
|------|-------------|
| `200` | Answer generated successfully |
| `400` | Validation error |
| `401` | Missing or invalid API key |
| `403` | Unauthorized caller scope |
| `422` | Invalid request body |
| `500` | Internal service error |

## Error Response

```json
{
  "request_id": "7d9827b8-9f42-4f4f-8e4a-3c4b4fd973a1",
  "status": "error",
  "error": {
    "code": "retrieval_no_evidence",
    "message": "No reliable medical evidence was found for this request.",
    "retryable": false,
    "details": {
      "workflow": "medical_qa"
    }
  },
  "safety": {
    "action": "refused",
    "requires_escalation": false
  }
}
```

## Examples

### cURL

```bash
curl -X POST http://localhost:8000/v1/ai/medical-qa \
  -H "Content-Type: application/json" \
  -H "X-Zam-AI-Key: <your-api-key>" \
  -d '{
    "actor_context": {
      "actor_type": "patient",
      "actor_id": "user-123",
      "role": "patient"
    },
    "input": {
      "question": "Can I take ibuprofen if I have stomach ulcers?",
      "patient_context": {
        "age": 42,
        "known_conditions": ["peptic ulcer disease"]
      }
    }
  }'
```

### JavaScript (fetch)

```javascript
const response = await fetch('http://localhost:8000/v1/ai/medical-qa', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Zam-AI-Key': '<your-api-key>'
  },
  body: JSON.stringify({
    actor_context: {
      actor_type: 'patient',
      actor_id: 'user-123',
      role: 'patient'
    },
    input: {
      question: 'Can I take ibuprofen if I have stomach ulcers?',
      patient_context: {
        age: 42,
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
    "http://localhost:8000/v1/ai/medical-qa",
    headers={
        "Content-Type": "application/json",
        "X-Zam-AI-Key": "<your-api-key>"
    },
    json={
        "actor_context": {
            "actor_type": "patient",
            "actor_id": "user-123",
            "role": "patient"
        },
        "input": {
            "question": "Can I take ibuprofen if I have stomach ulcers?",
            "patient_context": {
                "age": 42,
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

const response = await axios.post('http://localhost:8000/v1/ai/medical-qa', {
  actor_context: {
    actor_type: 'patient',
    actor_id: 'user-123',
    role: 'patient'
  },
  input: {
    question: 'Can I take ibuprofen if I have stomach ulcers?',
    patient_context: {
      age: 42,
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
            "actor_type": "patient",
            "actor_id":   "user-123",
            "role":       "patient",
        },
        "input": map[string]interface{}{
            "question": "Can I take ibuprofen if I have stomach ulcers?",
            "patient_context": map[string]interface{}{
                "age":               42,
                "known_conditions":  []string{"peptic ulcer disease"},
            },
        },
    }
    jsonBody, _ := json.Marshal(body)
    req, _ := http.NewRequest("POST", "http://localhost:8000/v1/ai/medical-qa", bytes.NewBuffer(jsonBody))
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
$ch = curl_init('http://localhost:8000/v1/ai/medical-qa');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'X-Zam-AI-Key: <your-api-key>'
]);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
    'actor_context' => [
        'actor_type' => 'patient',
        'actor_id' => 'user-123',
        'role' => 'patient'
    ],
    'input' => [
        'question' => 'Can I take ibuprofen if I have stomach ulcers?',
        'patient_context' => [
            'age' => 42,
            'known_conditions' => ['peptic ulcer disease']
        ]
    ]
]));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
curl_close($ch);
echo $response;
```
