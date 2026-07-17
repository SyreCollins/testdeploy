# Chat

`POST /v1/ai/chat`

Multi-intent conversational endpoint that classifies the user's intent and routes to the appropriate workflow.

## Purpose

Provides a unified conversational interface that automatically detects the user's intent (medical Q&A, drug info, symptom guidance, etc.) and routes to the correct workflow. Returns the classified intent and confidence for transparency.

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
    "actor_id": "user-303",
    "role": "patient"
  },
  "authorization_context": {
    "workflow": "chat",
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
    "message": "Can I take ibuprofen if I have stomach ulcers?",
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
| `input.message` | string | Yes | The user's message |
| `input.patient_context` | object | No | Patient context |
| `input.conversation_context` | object | No | Multi-turn conversation history |

## Response

```json
{
  "request_id": "7d9827b8-9f42-4f4f-8e4a-3c4b4fd973a1",
  "status": "success",
  "workflow": "chat",
  "result": {
    "intent": "medical_qa",
    "confidence": 0.95,
    "answer": "Ibuprofen may not be appropriate for some people with a history of stomach ulcers. Please speak with a clinician or pharmacist before taking it, especially if you have active ulcer symptoms or are taking other medicines that increase bleeding risk."
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
    "trace_id": "ai-trace-505",
    "prompt_version": "chat:v1",
    "model_provider": "provider-name",
    "model_version": "model-version"
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `result.intent` | string | Classified intent (`medical_qa`, `drug_info`, `symptom_guidance`, `interaction_check`, `contraindication_check`, `dosage_verify`, `prescription_explain`, `general`) |
| `result.confidence` | float | Intent classification confidence (0-1) |
| `result.answer` | string | The routed workflow's response |

## Supported Intents

| Intent | Routed Workflow |
|--------|----------------|
| `medical_qa` | Medical Q&A |
| `drug_info` | Drug Information |
| `symptom_guidance` | Symptom Guidance |
| `interaction_check` | Interaction Check |
| `contraindication_check` | Contraindication Check |
| `dosage_verify` | Dosage Verification |
| `prescription_explain` | Prescription Explanation |
| `general` | General conversational response |

## Status Codes

| Code | Description |
|------|-------------|
| `200` | Chat response generated |
| `400` | Validation error |
| `401` | Missing or invalid API key |
| `422` | Invalid request body |
| `500` | Internal service error |

## Examples

### cURL

```bash
curl -X POST http://localhost:8000/v1/ai/chat \
  -H "Content-Type: application/json" \
  -H "X-Zam-AI-Key: <your-api-key>" \
  -d '{
    "actor_context": {
      "actor_type": "patient",
      "actor_id": "user-303",
      "role": "patient"
    },
    "input": {
      "message": "Can I take ibuprofen if I have stomach ulcers?",
      "patient_context": {
        "age": 42,
        "known_conditions": ["peptic ulcer disease"]
      }
    }
  }'
```

### JavaScript (fetch)

```javascript
const response = await fetch('http://localhost:8000/v1/ai/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Zam-AI-Key': '<your-api-key>'
  },
  body: JSON.stringify({
    actor_context: {
      actor_type: 'patient',
      actor_id: 'user-303',
      role: 'patient'
    },
    input: {
      message: 'Can I take ibuprofen if I have stomach ulcers?',
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
    "http://localhost:8000/v1/ai/chat",
    headers={
        "Content-Type": "application/json",
        "X-Zam-AI-Key": "<your-api-key>"
    },
    json={
        "actor_context": {
            "actor_type": "patient",
            "actor_id": "user-303",
            "role": "patient"
        },
        "input": {
            "message": "Can I take ibuprofen if I have stomach ulcers?",
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

const response = await axios.post('http://localhost:8000/v1/ai/chat', {
  actor_context: {
    actor_type: 'patient',
    actor_id: 'user-303',
    role: 'patient'
  },
  input: {
    message: 'Can I take ibuprofen if I have stomach ulcers?',
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
            "actor_id":   "user-303",
            "role":       "patient",
        },
        "input": map[string]interface{}{
            "message": "Can I take ibuprofen if I have stomach ulcers?",
            "patient_context": map[string]interface{}{
                "age":              42,
                "known_conditions": []string{"peptic ulcer disease"},
            },
        },
    }
    jsonBody, _ := json.Marshal(body)
    req, _ := http.NewRequest("POST", "http://localhost:8000/v1/ai/chat", bytes.NewBuffer(jsonBody))
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
$ch = curl_init('http://localhost:8000/v1/ai/chat');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'X-Zam-AI-Key: <your-api-key>'
]);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
    'actor_context' => [
        'actor_type' => 'patient',
        'actor_id' => 'user-303',
        'role' => 'patient'
    ],
    'input' => [
        'message' => 'Can I take ibuprofen if I have stomach ulcers?',
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
