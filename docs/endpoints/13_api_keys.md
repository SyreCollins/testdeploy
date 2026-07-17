# API Key Management

Admin endpoints for managing internal API keys used to authenticate to the Zam AI service.

## Authentication

These endpoints require a valid admin-level internal API key via the `X-Zam-AI-Key` header. Admin keys have elevated privileges for key management operations.

---

## Create API Key

`POST /v1/admin/keys`

Creates a new internal API key with a human-readable label and optional expiration.

### Request

```json
{
  "label": "staging-backend-key",
  "expires_at": "2027-01-01T00:00:00Z"
}
```

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `label` | string | Yes | Human-readable label (1-100 characters) |
| `expires_at` | datetime | No | Optional expiration date |

### Response

`201 Created`

```json
{
  "id": "key_abc123",
  "label": "staging-backend-key",
  "key": "zam-ai-a1b2c3d4e5f6g7h8i9j0k",
  "prefix": "zam-ai-a1b2",
  "created_at": "2026-07-17T10:30:00Z",
  "expires_at": "2027-01-01T00:00:00Z",
  "is_active": true
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Internal key identifier |
| `label` | string | Human-readable label |
| `key` | string | The full API key (only returned on creation) |
| `prefix` | string | First few characters of the key for identification |
| `created_at` | datetime | Creation timestamp |
| `expires_at` | datetime | Expiration timestamp (null = never) |
| `is_active` | boolean | Whether the key is active |

---

## List API Keys

`GET /v1/admin/keys`

Lists all API keys with their metadata. Full key values are not returned — only prefixes.

### Response

```json
{
  "keys": [
    {
      "id": "key_abc123",
      "label": "staging-backend-key",
      "prefix": "zam-ai-a1b2",
      "created_at": "2026-07-17T10:30:00Z",
      "expires_at": "2027-01-01T00:00:00Z",
      "is_active": true,
      "last_used_at": "2026-07-17T14:00:00Z"
    }
  ]
}
```

---

## Rotate API Key

`POST /v1/admin/keys/{key_id}/rotate`

Revokes the current key and generates a new one with the same label and permissions.

### Response

```json
{
  "id": "key_abc123",
  "new_key": "zam-ai-x9y8z7w6v5u4t3s2r1q0p"
}
```

---

## Revoke API Key

`POST /v1/admin/keys/{key_id}/revoke`

Immediately revokes an API key. The key can no longer authenticate requests.

### Response

```json
{
  "id": "key_abc123",
  "revoked": true
}
```

---

## Status Codes

| Code | Description |
|------|-------------|
| `200` | Operation successful |
| `201` | Key created successfully |
| `400` | Validation error |
| `401` | Missing or invalid API key |
| `404` | Key not found |
| `409` | Key already revoked |
| `422` | Invalid request body |
| `500` | Internal service error |

## Examples

### cURL

```bash
# Create a key
curl -X POST http://localhost:8000/v1/admin/keys \
  -H "Content-Type: application/json" \
  -H "X-Zam-AI-Key: <admin-api-key>" \
  -d '{ "label": "test-key", "expires_at": "2027-01-01T00:00:00Z" }'

# List keys
curl -H "X-Zam-AI-Key: <admin-api-key>" \
  http://localhost:8000/v1/admin/keys

# Rotate a key
curl -X POST http://localhost:8000/v1/admin/keys/key_abc123/rotate \
  -H "X-Zam-AI-Key: <admin-api-key>"

# Revoke a key
curl -X POST http://localhost:8000/v1/admin/keys/key_abc123/revoke \
  -H "X-Zam-AI-Key: <admin-api-key>"
```

### JavaScript (fetch)

```javascript
const headers = {
  'Content-Type': 'application/json',
  'X-Zam-AI-Key': '<admin-api-key>'
};

// Create a key
const createRes = await fetch('http://localhost:8000/v1/admin/keys', {
  method: 'POST',
  headers,
  body: JSON.stringify({ label: 'test-key', expires_at: '2027-01-01T00:00:00Z' })
});
console.log(await createRes.json());

// List keys
const listRes = await fetch('http://localhost:8000/v1/admin/keys', { headers });
console.log(await listRes.json());

// Rotate a key
const rotateRes = await fetch('http://localhost:8000/v1/admin/keys/key_abc123/rotate', {
  method: 'POST', headers
});
console.log(await rotateRes.json());

// Revoke a key
const revokeRes = await fetch('http://localhost:8000/v1/admin/keys/key_abc123/revoke', {
  method: 'POST', headers
});
console.log(await revokeRes.json());
```

### Python (requests)

```python
import requests

headers = {
    "Content-Type": "application/json",
    "X-Zam-AI-Key": "<admin-api-key>"
}

# Create a key
response = requests.post(
    "http://localhost:8000/v1/admin/keys",
    headers=headers,
    json={"label": "test-key", "expires_at": "2027-01-01T00:00:00Z"}
)
print(response.json())

# List keys
response = requests.get("http://localhost:8000/v1/admin/keys", headers=headers)
print(response.json())

# Rotate a key
response = requests.post("http://localhost:8000/v1/admin/keys/key_abc123/rotate", headers=headers)
print(response.json())

# Revoke a key
response = requests.post("http://localhost:8000/v1/admin/keys/key_abc123/revoke", headers=headers)
print(response.json())
```

### Node.js (axios)

```javascript
const axios = require('axios');

const headers = {
  'Content-Type': 'application/json',
  'X-Zam-AI-Key': '<admin-api-key>'
};

// Create a key
const createRes = await axios.post('http://localhost:8000/v1/admin/keys', {
  label: 'test-key',
  expires_at: '2027-01-01T00:00:00Z'
}, { headers });
console.log(createRes.data);

// List keys
const listRes = await axios.get('http://localhost:8000/v1/admin/keys', { headers });
console.log(listRes.data);

// Rotate a key
const rotateRes = await axios.post('http://localhost:8000/v1/admin/keys/key_abc123/rotate', null, { headers });
console.log(rotateRes.data);

// Revoke a key
const revokeRes = await axios.post('http://localhost:8000/v1/admin/keys/key_abc123/revoke', null, { headers });
console.log(revokeRes.data);
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
    headers := map[string]string{
        "Content-Type": "application/json",
        "X-Zam-AI-Key": "<admin-api-key>",
    }

    // Create a key
    createBody, _ := json.Marshal(map[string]interface{}{
        "label": "test-key",
        "expires_at": "2027-01-01T00:00:00Z",
    })
    req1, _ := http.NewRequest("POST", "http://localhost:8000/v1/admin/keys", bytes.NewBuffer(createBody))
    for k, v := range headers { req1.Header.Set(k, v) }
    resp1, _ := client.Do(req1)
    defer resp1.Body.Close()
    io.Copy(os.Stdout, resp1.Body)

    // List keys
    req2, _ := http.NewRequest("GET", "http://localhost:8000/v1/admin/keys", nil)
    req2.Header.Set("X-Zam-AI-Key", "<admin-api-key>")
    resp2, _ := client.Do(req2)
    defer resp2.Body.Close()
    io.Copy(os.Stdout, resp2.Body)
}
```

### PHP

```php
<?php
$headers = [
    'Content-Type: application/json',
    'X-Zam-AI-Key: <admin-api-key>'
];

// Create a key
$ch = curl_init('http://localhost:8000/v1/admin/keys');
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
    'label' => 'test-key',
    'expires_at' => '2027-01-01T00:00:00Z'
]));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
echo curl_exec($ch);
curl_close($ch);
```
