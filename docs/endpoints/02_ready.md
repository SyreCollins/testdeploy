# Readiness Check

`GET /v1/ready`

Returns the readiness status of the service and its dependencies.

## Purpose

Used by load balancers and orchestrators to determine if the service is ready to accept traffic. Checks critical dependencies like the vector store, model gateway, and metadata store.

## Authentication

Not required.

## Request

No request body. No query parameters.

## Response

```json
{
  "status": "ready",
  "dependencies": {
    "api": { "status": "ok" },
    "metadata_store": { "status": "ok" },
    "vector_store": { "status": "ok" },
    "redis": { "status": "ok" },
    "model_gateway": { "status": "ok" }
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `"ready"` if all required dependencies are healthy |
| `dependencies` | object | Map of dependency name to status object |

Each dependency has:

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `"ok"`, `"degraded"`, or `"unavailable"` |
| `detail` | string | Optional detail message |

## Status Codes

| Code | Description |
|------|-------------|
| `200` | Service is ready to accept traffic |
| `503` | One or more critical dependencies are unavailable |

## Examples

### cURL

```bash
curl http://localhost:8000/v1/ready
```

### JavaScript (fetch)

```javascript
fetch('http://localhost:8000/v1/ready')
  .then(res => res.json())
  .then(data => console.log(data));
```

### Python (requests)

```python
import requests

response = requests.get("http://localhost:8000/v1/ready")
print(response.json())
```

### Node.js (axios)

```javascript
const axios = require('axios');

const response = await axios.get('http://localhost:8000/v1/ready');
console.log(response.data);
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
    resp, _ := http.Get("http://localhost:8000/v1/ready")
    body, _ := io.ReadAll(resp.Body)
    defer resp.Body.Close()
    fmt.Println(string(body))
}
```

### PHP

```php
<?php
$response = file_get_contents('http://localhost:8000/v1/ready');
echo $response;
```
