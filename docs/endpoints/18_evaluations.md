# Evaluations

`POST /v1/admin/evaluations/run`

> **Status: Planned** — Not yet implemented.

Starts an evaluation run against a specified dataset and prompt version.

## Purpose

Triggers automated evaluation runs for testing and regression detection. Used to validate prompt changes, model updates, and retrieval improvements against known test datasets.

## Authentication

Requires a valid admin-level internal API key via the `X-Zam-AI-Key` header.

## Request

```json
{
  "dataset_id": "medical_qa_core_v1",
  "prompt_version": "medical_qa:v1",
  "model_config": "default",
  "run_type": "regression"
}
```

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `dataset_id` | string | Yes | Identifier for the evaluation dataset |
| `prompt_version` | string | Yes | Prompt version to evaluate |
| `model_config` | string | No | Model configuration to use (default: `"default"`) |
| `run_type` | string | No | Type of run (`"regression"`, `"benchmark"`, or `"exploratory"`) |

## Response

```json
{
  "request_id": "7d9827b8-9f42-4f4f-8e4a-3c4b4fd973a1",
  "status": "success",
  "workflow": "evaluation",
  "result": {
    "run_id": "eval_run_001",
    "dataset_id": "medical_qa_core_v1",
    "status": "queued",
    "created_at": "2026-07-17T10:30:00Z"
  },
  "audit": {
    "trace_id": "ai-trace-909",
    "prompt_version": "evaluation:v1",
    "model_provider": "provider-name",
    "model_version": "model-version"
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `result.run_id` | string | Evaluation run identifier |
| `result.dataset_id` | string | Dataset being evaluated |
| `result.status` | string | `"queued"`, `"running"`, `"completed"`, or `"failed"` |
| `result.created_at` | datetime | Run creation timestamp |

## Examples

### cURL

```bash
curl -X POST http://localhost:8000/v1/admin/evaluations/run \
  -H "Content-Type: application/json" \
  -H "X-Zam-AI-Key: <admin-api-key>" \
  -d '{
    "dataset_id": "medical_qa_core_v1",
    "prompt_version": "medical_qa:v1",
    "model_config": "default",
    "run_type": "regression"
  }'
```

### JavaScript (fetch)

```javascript
const response = await fetch('http://localhost:8000/v1/admin/evaluations/run', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Zam-AI-Key': '<admin-api-key>'
  },
  body: JSON.stringify({
    dataset_id: 'medical_qa_core_v1',
    prompt_version: 'medical_qa:v1',
    model_config: 'default',
    run_type: 'regression'
  })
});

const data = await response.json();
console.log(data);
```

### Python (requests)

```python
import requests

response = requests.post(
    "http://localhost:8000/v1/admin/evaluations/run",
    headers={
        "Content-Type": "application/json",
        "X-Zam-AI-Key": "<admin-api-key>"
    },
    json={
        "dataset_id": "medical_qa_core_v1",
        "prompt_version": "medical_qa:v1",
        "model_config": "default",
        "run_type": "regression"
    }
)

print(response.json())
```

### Node.js (axios)

```javascript
const axios = require('axios');

const response = await axios.post('http://localhost:8000/v1/admin/evaluations/run', {
  dataset_id: 'medical_qa_core_v1',
  prompt_version: 'medical_qa:v1',
  model_config: 'default',
  run_type: 'regression'
}, {
  headers: {
    'Content-Type': 'application/json',
    'X-Zam-AI-Key': '<admin-api-key>'
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
        "dataset_id":     "medical_qa_core_v1",
        "prompt_version": "medical_qa:v1",
        "model_config":   "default",
        "run_type":       "regression",
    }
    jsonBody, _ := json.Marshal(body)
    req, _ := http.NewRequest("POST", "http://localhost:8000/v1/admin/evaluations/run", bytes.NewBuffer(jsonBody))
    req.Header.Set("Content-Type", "application/json")
    req.Header.Set("X-Zam-AI-Key", "<admin-api-key>")

    client := &http.Client{}
    resp, _ := client.Do(req)
    defer resp.Body.Close()
    io.Copy(os.Stdout, resp.Body)
}
```

### PHP

```php
<?php
$ch = curl_init('http://localhost:8000/v1/admin/evaluations/run');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'X-Zam-AI-Key: <admin-api-key>'
]);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
    'dataset_id' => 'medical_qa_core_v1',
    'prompt_version' => 'medical_qa:v1',
    'model_config' => 'default',
    'run_type' => 'regression'
]));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
curl_close($ch);
echo $response;
```

| Code | Description |
|------|-------------|
| `200` | Evaluation run created |
| `400` | Validation error |
| `401` | Missing or invalid API key |
| `422` | Invalid request body |
| `500` | Internal service error |
