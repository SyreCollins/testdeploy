# Audit Traces

## List Audit Traces

`GET /v1/audit/traces`

Lists recent audit traces for monitoring and debugging.

## Get Audit Trace

`GET /v1/audit/traces/{trace_id}`

Retrieves a specific audit trace by ID.

## Purpose

Provides visibility into AI workflow execution for compliance, debugging, and monitoring. Every medical endpoint writes an audit trace containing request context, retrieved sources, model metadata, and safety decisions.

## Authentication

Requires a valid internal API key via the `X-Zam-AI-Key` header.

## List Traces

### Request

Query parameter:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | int | No | `50` | Maximum number of traces to return |

### Response

```json
{
  "traces": [
    {
      "trace_id": "ai-trace-123",
      "workflow": "medical_qa",
      "started_at": "2026-07-17T10:30:00Z",
      "completed_at": "2026-07-17T10:30:02Z",
      "event_count": 5,
      "events": [
        {
          "event_type": "request_received",
          "timestamp": "2026-07-17T10:30:00Z",
          "data": {
            "workflow": "medical_qa",
            "actor_type": "patient"
          }
        },
        {
          "event_type": "retrieval_completed",
          "timestamp": "2026-07-17T10:30:01Z",
          "data": {
            "chunks_retrieved": 3,
            "sources": ["Nigeria Essential Medicine List"]
          }
        },
        {
          "event_type": "response_sent",
          "timestamp": "2026-07-17T10:30:02Z",
          "data": {
            "action": "answered",
            "risk_level": "medium"
          }
        }
      ]
    }
  ],
  "total": 1
}
```

## Get Single Trace

### Response

```json
{
  "trace": {
    "trace_id": "ai-trace-123",
    "workflow": "medical_qa",
    "started_at": "2026-07-17T10:30:00Z",
    "completed_at": "2026-07-17T10:30:02Z",
    "event_count": 5,
    "events": [
      {
        "event_type": "request_received",
        "timestamp": "2026-07-17T10:30:00Z",
        "data": {}
      },
      {
        "event_type": "intent_classified",
        "timestamp": "2026-07-17T10:30:00Z",
        "data": {
          "intent": "medical_qa",
          "confidence": 0.95
        }
      },
      {
        "event_type": "retrieval_completed",
        "timestamp": "2026-07-17T10:30:01Z",
        "data": {
          "chunks_retrieved": 3,
          "sources": ["Nigeria Essential Medicine List"]
        }
      },
      {
        "event_type": "grounding_checked",
        "timestamp": "2026-07-17T10:30:01Z",
        "data": {
          "grounding_score": 0.9,
          "passed": true
        }
      },
      {
        "event_type": "response_sent",
        "timestamp": "2026-07-17T10:30:02Z",
        "data": {
          "action": "answered",
          "risk_level": "medium"
        }
      }
    ]
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `trace.trace_id` | string | Unique trace identifier |
| `trace.workflow` | string | Workflow name |
| `trace.started_at` | string | ISO 8601 timestamp |
| `trace.completed_at` | string | ISO 8601 timestamp (null if in progress) |
| `trace.event_count` | int | Number of events in the trace |
| `trace.events[].event_type` | string | Type of event |
| `trace.events[].timestamp` | string | ISO 8601 timestamp |
| `trace.events[].data` | object | Event-specific data payload |

## Event Types

| Event Type | Description |
|------------|-------------|
| `request_received` | Initial request received |
| `intent_classified` | Intent classification result |
| `retrieval_completed` | RAG retrieval completed |
| `grounding_checked` | Grounding verification result |
| `safety_checked` | Safety policy evaluation |
| `model_invoked` | LLM model call |
| `response_sent` | Final response sent |
| `error` | Error occurred |

## Status Codes

| Code | Description |
|------|-------------|
| `200` | Traces retrieved successfully |
| `401` | Missing or invalid API key |
| `404` | Trace ID not found |
| `500` | Internal service error |

## Examples

### cURL

```bash
# List recent traces
curl -H "X-Zam-AI-Key: <your-api-key>" \
  http://localhost:8000/v1/audit/traces?limit=10

# Get a specific trace
curl -H "X-Zam-AI-Key: <your-api-key>" \
  http://localhost:8000/v1/audit/traces/ai-trace-123
```

### JavaScript (fetch)

```javascript
// List recent traces
const listResponse = await fetch('http://localhost:8000/v1/audit/traces?limit=10', {
  headers: { 'X-Zam-AI-Key': '<your-api-key>' }
});
const traces = await listResponse.json();
console.log(traces);

// Get a specific trace
const traceResponse = await fetch('http://localhost:8000/v1/audit/traces/ai-trace-123', {
  headers: { 'X-Zam-AI-Key': '<your-api-key>' }
});
const trace = await traceResponse.json();
console.log(trace);
```

### Python (requests)

```python
import requests

headers = {"X-Zam-AI-Key": "<your-api-key>"}

# List recent traces
response = requests.get(
    "http://localhost:8000/v1/audit/traces",
    params={"limit": 10},
    headers=headers
)
print(response.json())

# Get a specific trace
response = requests.get(
    "http://localhost:8000/v1/audit/traces/ai-trace-123",
    headers=headers
)
print(response.json())
```

### Node.js (axios)

```javascript
const axios = require('axios');

const headers = { 'X-Zam-AI-Key': '<your-api-key>' };

// List recent traces
const listResponse = await axios.get('http://localhost:8000/v1/audit/traces', {
  params: { limit: 10 },
  headers
});
console.log(listResponse.data);

// Get a specific trace
const traceResponse = await axios.get('http://localhost:8000/v1/audit/traces/ai-trace-123', { headers });
console.log(traceResponse.data);
```

### Go

```go
package main

import (
    "fmt"
    "io"
    "net/http"
)

func main() {
    client := &http.Client{}

    // List recent traces
    req1, _ := http.NewRequest("GET", "http://localhost:8000/v1/audit/traces?limit=10", nil)
    req1.Header.Set("X-Zam-AI-Key", "<your-api-key>")
    resp1, _ := client.Do(req1)
    defer resp1.Body.Close()
    body1, _ := io.ReadAll(resp1.Body)
    fmt.Println(string(body1))

    // Get a specific trace
    req2, _ := http.NewRequest("GET", "http://localhost:8000/v1/audit/traces/ai-trace-123", nil)
    req2.Header.Set("X-Zam-AI-Key", "<your-api-key>")
    resp2, _ := client.Do(req2)
    defer resp2.Body.Close()
    body2, _ := io.ReadAll(resp2.Body)
    fmt.Println(string(body2))
}
```

### PHP

```php
<?php
$headers = ['X-Zam-AI-Key: <your-api-key>'];

// List recent traces
$ch1 = curl_init('http://localhost:8000/v1/audit/traces?limit=10');
curl_setopt($ch1, CURLOPT_HTTPHEADER, $headers);
curl_setopt($ch1, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch1);
curl_close($ch1);
echo $response;

// Get a specific trace
$ch2 = curl_init('http://localhost:8000/v1/audit/traces/ai-trace-123');
curl_setopt($ch2, CURLOPT_HTTPHEADER, $headers);
curl_setopt($ch2, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch2);
curl_close($ch2);
echo $response;
```
