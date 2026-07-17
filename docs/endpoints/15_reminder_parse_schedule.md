# Reminder Schedule Parsing

`POST /v1/ai/reminders/parse-schedule`

> **Status: Planned** — Not yet implemented.

Converts medication instructions into structured reminder schedule objects.

## Purpose

Parses natural language medication instructions and returns a structured schedule that the backend can use to set up patient reminders. The backend stores and sends reminders — Zam AI only parses and suggests the schedule structure.

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
    "actor_id": "user-404",
    "role": "patient"
  },
  "authorization_context": {
    "workflow": "parse_schedule",
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
    "instruction_text": "Take one capsule three times daily for 7 days",
    "medication_name": "amoxicillin"
  }
}
```

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `input.instruction_text` | string | Yes | Natural language medication instructions |
| `input.medication_name` | string | No | Medication name for context |

## Response

```json
{
  "request_id": "7d9827b8-9f42-4f4f-8e4a-3c4b4fd973a1",
  "status": "success",
  "workflow": "parse_schedule",
  "result": {
    "schedule": {
      "frequency": "three_times_daily",
      "times_per_day": 3,
      "interval_hours": 8,
      "duration_days": 7,
      "specific_times": ["08:00", "14:00", "20:00"],
      "as_needed": false,
      "notes": "Take with or without food"
    },
    "confidence": 0.88,
    "requires_clarification": false
  },
  "audit": {
    "trace_id": "ai-trace-606",
    "prompt_version": "parse_schedule:v1",
    "model_provider": "provider-name",
    "model_version": "model-version"
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `result.schedule.frequency` | string | Parsed frequency (e.g. `three_times_daily`, `once_daily`, `as_needed`) |
| `result.schedule.times_per_day` | int | Number of times per day |
| `result.schedule.interval_hours` | int | Suggested interval in hours |
| `result.schedule.duration_days` | int | Duration in days |
| `result.schedule.specific_times` | string[] | Suggested specific times |
| `result.schedule.as_needed` | boolean | Whether medication is as-needed |
| `result.schedule.notes` | string | Additional notes |
| `result.confidence` | float | Parsing confidence (0-1) |
| `result.requires_clarification` | boolean | Whether instructions need clarification |

## Safety Rules

- The backend stores and sends reminders — Zam AI only parses and suggests schedule structure
- Ambiguous instructions require clarification
- Does not store or manage reminder state

## Examples

### cURL

```bash
curl -X POST http://localhost:8000/v1/ai/reminders/parse-schedule \
  -H "Content-Type: application/json" \
  -H "X-Zam-AI-Key: <your-api-key>" \
  -d '{
    "actor_context": {
      "actor_type": "patient",
      "actor_id": "user-404",
      "role": "patient"
    },
    "input": {
      "instruction_text": "Take one capsule three times daily for 7 days",
      "medication_name": "amoxicillin"
    }
  }'
```

### JavaScript (fetch)

```javascript
const response = await fetch('http://localhost:8000/v1/ai/reminders/parse-schedule', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Zam-AI-Key': '<your-api-key>'
  },
  body: JSON.stringify({
    actor_context: {
      actor_type: 'patient',
      actor_id: 'user-404',
      role: 'patient'
    },
    input: {
      instruction_text: 'Take one capsule three times daily for 7 days',
      medication_name: 'amoxicillin'
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
    "http://localhost:8000/v1/ai/reminders/parse-schedule",
    headers={
        "Content-Type": "application/json",
        "X-Zam-AI-Key": "<your-api-key>"
    },
    json={
        "actor_context": {
            "actor_type": "patient",
            "actor_id": "user-404",
            "role": "patient"
        },
        "input": {
            "instruction_text": "Take one capsule three times daily for 7 days",
            "medication_name": "amoxicillin"
        }
    }
)

print(response.json())
```

### Node.js (axios)

```javascript
const axios = require('axios');

const response = await axios.post('http://localhost:8000/v1/ai/reminders/parse-schedule', {
  actor_context: {
    actor_type: 'patient',
    actor_id: 'user-404',
    role: 'patient'
  },
  input: {
    instruction_text: 'Take one capsule three times daily for 7 days',
    medication_name: 'amoxicillin'
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
            "actor_id":   "user-404",
            "role":       "patient",
        },
        "input": map[string]interface{}{
            "instruction_text": "Take one capsule three times daily for 7 days",
            "medication_name":  "amoxicillin",
        },
    }
    jsonBody, _ := json.Marshal(body)
    req, _ := http.NewRequest("POST", "http://localhost:8000/v1/ai/reminders/parse-schedule", bytes.NewBuffer(jsonBody))
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
$ch = curl_init('http://localhost:8000/v1/ai/reminders/parse-schedule');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'X-Zam-AI-Key: <your-api-key>'
]);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
    'actor_context' => [
        'actor_type' => 'patient',
        'actor_id' => 'user-404',
        'role' => 'patient'
    ],
    'input' => [
        'instruction_text' => 'Take one capsule three times daily for 7 days',
        'medication_name' => 'amoxicillin'
    ]
]));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
curl_close($ch);
echo $response;
```

| Code | Description |
|------|-------------|
| `200` | Schedule parsed successfully |
| `400` | Validation error |
| `401` | Missing or invalid API key |
| `422` | Invalid request body |
| `500` | Internal service error |
