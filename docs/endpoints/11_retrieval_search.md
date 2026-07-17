# Retrieval Search

`POST /v1/retrieval/search`

Searches the medical knowledge corpus for relevant document chunks.

## Purpose

Provides direct access to the RAG retrieval system. Returns ranked document chunks matching the query, with metadata including source, section, and trust tier. Primarily used for debugging, evaluation, and internal tooling.

## Authentication

Requires a valid internal API key via the `X-Zam-AI-Key` header.

## Request

```json
{
  "query": "What is the dosage of amoxicillin?",
  "limit": 10,
  "generic_name_filter": "amoxicillin",
  "chunk_type_filter": "dosage",
  "min_trust_tier": 2
}
```

### Request Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `query` | string | Yes | — | Search query text |
| `limit` | int | No | `10` | Maximum results (1-50) |
| `generic_name_filter` | string | No | — | Filter by generic drug name |
| `chunk_type_filter` | string | No | — | Filter by chunk type (e.g. `dosage`, `contraindication`, `indication`) |
| `min_trust_tier` | int | No | — | Minimum source trust tier (1-4, lower = more trusted) |

## Response

```json
{
  "query": "What is the dosage of amoxicillin?",
  "results": [
    {
      "citation_id": "cit_1",
      "text_content": "Amoxicillin 500 mg three times daily for 7-10 days is a standard adult dosage for common bacterial infections.",
      "score": 0.92,
      "section_path": "Section 6: Anti-infective Medicines",
      "page_number": 23,
      "generic_name": "amoxicillin",
      "chunk_type": "dosage",
      "source_name": "Nigeria Essential Medicine List",
      "source_version": "2020",
      "source_trust_tier": 1,
      "document_title": "Nigeria Essential Medicine List 2020"
    }
  ],
  "total": 1
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `query` | string | Echoed search query |
| `results` | object[] | Ranked search results |
| `results[].citation_id` | string | Unique citation identifier |
| `results[].text_content` | string | The chunk text content |
| `results[].score` | float | Relevance score (0-1) |
| `results[].source_name` | string | Name of the source document |
| `results[].source_version` | string | Version of the source |
| `results[].source_trust_tier` | int | Trust tier (1 = highest) |
| `results[].document_title` | string | Document title |
| `results[].section_path` | string | Section path within the document |
| `results[].page_number` | int | Page number |
| `results[].generic_name` | string | Associated generic drug name |
| `results[].chunk_type` | string | Type of chunk (dosage, contraindication, etc.) |
| `total` | int | Total number of results |

## Status Codes

| Code | Description |
|------|-------------|
| `200` | Search completed |
| `400` | Invalid query parameters |
| `401` | Missing or invalid API key |
| `500` | Internal service error |

## Examples

### cURL

```bash
curl -X POST http://localhost:8000/v1/retrieval/search \
  -H "Content-Type: application/json" \
  -H "X-Zam-AI-Key: <your-api-key>" \
  -d '{
    "query": "What is the dosage of amoxicillin?",
    "limit": 5
  }'
```

### JavaScript (fetch)

```javascript
const response = await fetch('http://localhost:8000/v1/retrieval/search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-Zam-AI-Key': '<your-api-key>'
  },
  body: JSON.stringify({
    query: 'What is the dosage of amoxicillin?',
    limit: 5
  })
});

const data = await response.json();
console.log(data);
```

### Python (requests)

```python
import requests

response = requests.post(
    "http://localhost:8000/v1/retrieval/search",
    headers={
        "Content-Type": "application/json",
        "X-Zam-AI-Key": "<your-api-key>"
    },
    json={
        "query": "What is the dosage of amoxicillin?",
        "limit": 5
    }
)

print(response.json())
```

### Node.js (axios)

```javascript
const axios = require('axios');

const response = await axios.post('http://localhost:8000/v1/retrieval/search', {
  query: 'What is the dosage of amoxicillin?',
  limit: 5
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
        "query": "What is the dosage of amoxicillin?",
        "limit": 5,
    }
    jsonBody, _ := json.Marshal(body)
    req, _ := http.NewRequest("POST", "http://localhost:8000/v1/retrieval/search", bytes.NewBuffer(jsonBody))
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
$ch = curl_init('http://localhost:8000/v1/retrieval/search');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'X-Zam-AI-Key: <your-api-key>'
]);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
    'query' => 'What is the dosage of amoxicillin?',
    'limit' => 5
]));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$response = curl_exec($ch);
curl_close($ch);
echo $response;
```
