# Prescription OCR

> **Status: Planned** — Not yet implemented.

## Create OCR Job

`POST /v1/ai/prescriptions/ocr-jobs`

Creates an asynchronous OCR job to extract structured prescription data from an image.

## Get OCR Job

`GET /v1/ai/prescriptions/ocr-jobs/{job_id}`

Retrieves the status and result of an OCR job.

## Purpose

Extracts structured prescription data (medication names, dosages, instructions) from prescription images. OCR is asynchronous — the create endpoint returns a job ID, and the get endpoint is polled for results.

## Authentication

Requires a valid internal API key via the `X-Zam-AI-Key` header.

## Create OCR Job

### Request

```json
{
  "request_id": "7d9827b8-9f42-4f4f-8e4a-3c4b4fd973a1",
  "caller": {
    "service": "zamda-backend",
    "environment": "production"
  },
  "actor_context": {
    "actor_type": "pharmacy",
    "actor_id": "pharm-101",
    "role": "pharmacist"
  },
  "authorization_context": {
    "workflow": "prescription_ocr",
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
    "image_reference": "backend-storage-ref",
    "prescription_id": "backend-prescription-ref",
    "callback_url": null
  }
}
```

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `input.image_reference` | string | Yes | Reference to the stored prescription image |
| `input.prescription_id` | string | Yes | Backend prescription reference |
| `input.callback_url` | string | No | URL to call when OCR completes |

### Response

`201 Created`

```json
{
  "request_id": "7d9827b8-9f42-4f4f-8e4a-3c4b4fd973a1",
  "status": "success",
  "workflow": "prescription_ocr",
  "result": {
    "job_id": "ocr_job_123",
    "status": "queued"
  }
}
```

---

## Get OCR Job

`GET /v1/ai/prescriptions/ocr-jobs/{job_id}`

### Response

```json
{
  "request_id": "7d9827b8-9f42-4f4f-8e4a-3c4b4fd973a1",
  "status": "success",
  "workflow": "prescription_ocr",
  "result": {
    "job_id": "ocr_job_123",
    "status": "completed",
    "fields": [
      {
        "field": "medication_name",
        "value": "amoxicillin",
        "confidence": 0.91,
        "requires_review": false
      },
      {
        "field": "dosage",
        "value": "500 mg",
        "confidence": 0.88,
        "requires_review": false
      },
      {
        "field": "frequency",
        "value": "three times daily",
        "confidence": 0.85,
        "requires_review": false
      },
      {
        "field": "duration",
        "value": "7 days",
        "confidence": 0.82,
        "requires_review": false
      }
    ],
    "overall_confidence": 0.84,
    "requires_human_review": false
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `result.job_id` | string | OCR job identifier |
| `result.status` | string | `"queued"`, `"processing"`, `"completed"`, or `"failed"` |
| `result.fields[].field` | string | Extracted field name |
| `result.fields[].value` | string | Extracted value |
| `result.fields[].confidence` | float | OCR confidence score (0-1) |
| `result.fields[].requires_review` | boolean | Whether this field needs human review |
| `result.overall_confidence` | float | Overall OCR confidence |
| `result.requires_human_review` | boolean | Whether the entire result needs human review |

## Status Codes

| Code | Description |
|------|-------------|
| `201` | OCR job created |
| `200` | OCR job status retrieved |
| `400` | Validation error |
| `401` | Missing or invalid API key |
| `404` | Job ID not found |
| `500` | Internal service error |

## Examples

### cURL

```bash
# Create OCR job
curl -X POST http://localhost:8000/v1/ai/prescriptions/ocr-jobs \
  -H "Content-Type: application/json" \
  -H "X-Zam-AI-Key: <your-api-key>" \
  -d '{
    "actor_context": {
      "actor_type": "pharmacy",
      "actor_id": "pharm-101",
      "role": "pharmacist"
    },
    "input": {
      "image_reference": "backend-storage-ref-123",
      "prescription_id": "rx-456"
    }
  }'

# Poll for results
curl -H "X-Zam-AI-Key: <your-api-key>" \
  http://localhost:8000/v1/ai/prescriptions/ocr-jobs/ocr_job_123
```

### JavaScript (fetch)

```javascript
// Create OCR job
const createRes = await fetch('http://localhost:8000/v1/ai/prescriptions/ocr-jobs', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Zam-AI-Key': '<your-api-key>'
  },
  body: JSON.stringify({
    actor_context: {
      actor_type: 'pharmacy',
      actor_id: 'pharm-101',
      role: 'pharmacist'
    },
    input: {
      image_reference: 'backend-storage-ref-123',
      prescription_id: 'rx-456'
    }
  })
});
const job = await createRes.json();
console.log(job);

// Poll for results
const pollRes = await fetch(`http://localhost:8000/v1/ai/prescriptions/ocr-jobs/${job.result.job_id}`, {
  headers: { 'X-Zam-AI-Key': '<your-api-key>' }
});
console.log(await pollRes.json());
```

### Python (requests)

```python
import requests

headers = {
    "Content-Type": "application/json",
    "X-Zam-AI-Key": "<your-api-key>"
}

# Create OCR job
response = requests.post(
    "http://localhost:8000/v1/ai/prescriptions/ocr-jobs",
    headers=headers,
    json={
        "actor_context": {
            "actor_type": "pharmacy",
            "actor_id": "pharm-101",
            "role": "pharmacist"
        },
        "input": {
            "image_reference": "backend-storage-ref-123",
            "prescription_id": "rx-456"
        }
    }
)
job = response.json()
print(job)

# Poll for results
job_id = job["result"]["job_id"]
response = requests.get(
    f"http://localhost:8000/v1/ai/prescriptions/ocr-jobs/{job_id}",
    headers=headers
)
print(response.json())
```

### Node.js (axios)

```javascript
const axios = require('axios');

const headers = {
  'Content-Type': 'application/json',
  'X-Zam-AI-Key': '<your-api-key>'
};

// Create OCR job
const createRes = await axios.post('http://localhost:8000/v1/ai/prescriptions/ocr-jobs', {
  actor_context: {
    actor_type: 'pharmacy',
    actor_id: 'pharm-101',
    role: 'pharmacist'
  },
  input: {
    image_reference: 'backend-storage-ref-123',
    prescription_id: 'rx-456'
  }
}, { headers });
console.log(createRes.data);

// Poll for results
const jobId = createRes.data.result.job_id;
const pollRes = await axios.get(`http://localhost:8000/v1/ai/prescriptions/ocr-jobs/${jobId}`, { headers });
console.log(pollRes.data);
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
    client := &http.Client{}

    // Create OCR job
    body := map[string]interface{}{
        "actor_context": map[string]string{
            "actor_type": "pharmacy",
            "actor_id":   "pharm-101",
            "role":       "pharmacist",
        },
        "input": map[string]string{
            "image_reference": "backend-storage-ref-123",
            "prescription_id": "rx-456",
        },
    }
    jsonBody, _ := json.Marshal(body)
    req, _ := http.NewRequest("POST", "http://localhost:8000/v1/ai/prescriptions/ocr-jobs", bytes.NewBuffer(jsonBody))
    req.Header.Set("Content-Type", "application/json")
    req.Header.Set("X-Zam-AI-Key", "<your-api-key>")
    resp, _ := client.Do(req)
    defer resp.Body.Close()
    io.Copy(os.Stdout, resp.Body)
}
```

### PHP

```php
<?php
$headers = [
    'Content-Type: application/json',
    'X-Zam-AI-Key: <your-api-key>'
];

// Create OCR job
$ch = curl_init('http://localhost:8000/v1/ai/prescriptions/ocr-jobs');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
    'actor_context' => [
        'actor_type' => 'pharmacy',
        'actor_id' => 'pharm-101',
        'role' => 'pharmacist'
    ],
    'input' => [
        'image_reference' => 'backend-storage-ref-123',
        'prescription_id' => 'rx-456'
    ]
]));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
curl_close($ch);
echo $response;
```
