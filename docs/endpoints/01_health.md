# Health Check

`GET /v1/health`

Returns the current health status of the Zam AI service.

## Purpose

Used by load balancers, orchestrators, and monitoring systems to verify the service process is alive and responding.

## Authentication

Not required.

## Request

No request body. No query parameters.

## Response

```json
{
  "status": "ok",
  "service": "zam-ai",
  "version": "0.1.0",
  "environment": "production"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Always `"ok"` if the process is running |
| `service` | string | Service name identifier |
| `version` | string | Current deployed version |
| `environment` | string | Deployment environment (production, staging, development) |

## Status Codes

| Code | Description |
|------|-------------|
| `200` | Service is healthy |
| `500` | Service process is unhealthy |

## Examples

### cURL

```bash
curl http://localhost:8000/v1/health
```

### JavaScript (fetch)

```javascript
fetch('http://localhost:8000/v1/health')
  .then(res => res.json())
  .then(data => console.log(data));
```

### Python (requests)

```python
import requests

response = requests.get("http://localhost:8000/v1/health")
print(response.json())
```

### Node.js (axios)

```javascript
const axios = require('axios');

const response = await axios.get('http://localhost:8000/v1/health');
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
    resp, _ := http.Get("http://localhost:8000/v1/health")
    body, _ := io.ReadAll(resp.Body)
    defer resp.Body.Close()
    fmt.Println(string(body))
}
```

### PHP

```php
<?php
$response = file_get_contents('http://localhost:8000/v1/health');
echo $response;
```
