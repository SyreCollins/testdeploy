# Drug Information

`POST /v1/ai/drug-info`

Returns source-grounded medication information from approved medical references.

## Purpose

Provides patients and clinicians with reliable drug information including uses, warnings, side effects, and other sections. The drug name is normalized to its generic form for consistent referencing.

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
    "actor_id": "user-789",
    "role": "patient"
  },
  "authorization_context": {
    "workflow": "drug_info",
    "consent_flags": {
      "use_patient_context": false,
      "store_ai_trace": true
    },
    "context_scope": []
  },
  "locale": {
    "language": "en",
    "country": "NG"
  },
  "input": {
    "drug_name": "Augmentin",
    "requested_sections": ["uses", "warnings", "side_effects"],
    "country": "NG"
  }
}
```

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `input.drug_name` | string | Yes | Brand or generic drug name |
| `input.requested_sections` | string[] | No | Specific sections to return (e.g. `uses`, `warnings`, `side_effects`, `dosage`). Returns all if omitted |
| `input.country` | string | No | Country code for localized information (default: `"NG"`) |

## Response

```json
{
  "request_id": "7d9827b8-9f42-4f4f-8e4a-3c4b4fd973a1",
  "status": "success",
  "workflow": "drug_info",
  "result": {
    "normalized_drug": {
      "input_name": "Augmentin",
      "generic_name": "amoxicillin/clavulanate",
      "match_confidence": 0.94
    },
    "sections": {
      "uses": "Augmentin (amoxicillin/clavulanate) is an antibiotic used to treat bacterial infections including sinusitis, pneumonia, ear infections, and urinary tract infections.",
      "warnings": "Use with caution in patients with liver impairment or history of cholestatic jaundice. May cause allergic reactions in patients with penicillin allergy.",
      "side_effects": "Common side effects include diarrhea, nausea, skin rash, and vomiting. Seek medical attention if severe allergic reaction occurs."
    }
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
      "text_content": "Amoxicillin/clavulanate is indicated for the treatment of bacterial infections including lower respiratory tract infections, sinusitis, and urinary tract infections.",
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
    "trace_id": "ai-trace-789",
    "prompt_version": "drug_info:v1",
    "model_provider": "provider-name",
    "model_version": "model-version"
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `result.normalized_drug.input_name` | string | The original drug name queried |
| `result.normalized_drug.generic_name` | string | Normalized generic name |
| `result.normalized_drug.match_confidence` | float | Confidence of the drug name match (0-1) |
| `result.sections` | object | Map of section name to content text |

## Safety Rules

- All drug information is sourced from approved medical references
- Drug names are normalized to generic names for consistency
- Missing or ambiguous drug names return a normalization error

## Status Codes

| Code | Description |
|------|-------------|
| `200` | Drug information returned successfully |
| `400` | Validation error (e.g. unknown drug name) |
| `401` | Missing or invalid API key |
| `422` | Invalid request body |
| `500` | Internal service error |

## Examples

### cURL

```bash
curl -X POST http://localhost:8000/v1/ai/drug-info \
  -H "Content-Type: application/json" \
  -H "X-Zam-AI-Key: <your-api-key>" \
  -d '{
    "actor_context": {
      "actor_type": "patient",
      "actor_id": "user-789",
      "role": "patient"
    },
    "input": {
      "drug_name": "Augmentin",
      "requested_sections": ["uses", "warnings", "side_effects"]
    }
  }'
```

### JavaScript (fetch)

```javascript
const response = await fetch('http://localhost:8000/v1/ai/drug-info', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Zam-AI-Key': '<your-api-key>'
  },
  body: JSON.stringify({
    actor_context: {
      actor_type: 'patient',
      actor_id: 'user-789',
      role: 'patient'
    },
    input: {
      drug_name: 'Augmentin',
      requested_sections: ['uses', 'warnings', 'side_effects']
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
    "http://localhost:8000/v1/ai/drug-info",
    headers={
        "Content-Type": "application/json",
        "X-Zam-AI-Key": "<your-api-key>"
    },
    json={
        "actor_context": {
            "actor_type": "patient",
            "actor_id": "user-789",
            "role": "patient"
        },
        "input": {
            "drug_name": "Augmentin",
            "requested_sections": ["uses", "warnings", "side_effects"]
        }
    }
)

print(response.json())
```

### Node.js (axios)

```javascript
const axios = require('axios');

const response = await axios.post('http://localhost:8000/v1/ai/drug-info', {
  actor_context: {
    actor_type: 'patient',
    actor_id: 'user-789',
    role: 'patient'
  },
  input: {
    drug_name: 'Augmentin',
    requested_sections: ['uses', 'warnings', 'side_effects']
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
            "actor_id":   "user-789",
            "role":       "patient",
        },
        "input": map[string]interface{}{
            "drug_name":          "Augmentin",
            "requested_sections": []string{"uses", "warnings", "side_effects"},
        },
    }
    jsonBody, _ := json.Marshal(body)
    req, _ := http.NewRequest("POST", "http://localhost:8000/v1/ai/drug-info", bytes.NewBuffer(jsonBody))
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
$ch = curl_init('http://localhost:8000/v1/ai/drug-info');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'X-Zam-AI-Key: <your-api-key>'
]);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
    'actor_context' => [
        'actor_type' => 'patient',
        'actor_id' => 'user-789',
        'role' => 'patient'
    ],
    'input' => [
        'drug_name' => 'Augmentin',
        'requested_sections' => ['uses', 'warnings', 'side_effects']
    ]
]));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
curl_close($ch);
echo $response;
```
