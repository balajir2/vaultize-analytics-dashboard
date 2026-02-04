# API Documentation

> RESTful API reference for programmatic access to Vaultize Analytics Platform

---

## Overview

The Vaultize Analytics Platform exposes a RESTful API for programmatic access to search, analytics, and management functions.

**Base URL**: `http://localhost:8000/api/v1`

**API Framework**: FastAPI (Python)

---

## Documents

### [API Overview](./overview.md)
Introduction to the API, authentication, and common patterns.

**Topics Covered**:
- API architecture
- Versioning strategy
- Request/response formats
- Error handling
- Rate limiting
- Pagination

**Status**: 🔴 Not Started

---

### [Authentication](./authentication.md)
How to authenticate API requests.

**Topics Covered**:
- Authentication methods (API keys, OAuth, etc.)
- Authorization and permissions
- Token management
- Security best practices

**Status**: 🔴 Not Started

---

### [Search API](./search.md)
Query and search logs programmatically.

**Topics Covered**:
- Search endpoint
- Query syntax
- Filtering
- Time range queries
- Sorting and pagination
- Full-text search
- Field-based queries

**Status**: 🔴 Not Started

---

### [Aggregation API](./aggregations.md)
Run analytics and aggregations.

**Topics Covered**:
- Aggregation endpoint
- Metric aggregations (count, sum, avg, min, max)
- Bucket aggregations (terms, histogram, date_histogram)
- Pipeline aggregations
- Nested aggregations

**Status**: 🔴 Not Started

---

### [Index Management API](./index-management.md)
Manage indices and lifecycle policies.

**Topics Covered**:
- List indices
- Create/delete indices
- Index settings and mappings
- ILM policy management
- Rollover operations
- Force merge

**Status**: 🔴 Not Started

---

### [Alert API](./alerts.md)
Manage alerts and alert rules.

**Topics Covered**:
- List alerts
- Create/update/delete alert rules
- Alert status and history
- Trigger alerts manually
- Notification configuration

**Status**: 🔴 Not Started

---

### [OpenAPI Specification](./openapi.yaml)
Machine-readable API specification.

**Format**: OpenAPI 3.0 (Swagger)

**Status**: 🔴 Not Started

---

## Quick Start

### Authentication
```bash
# Get API token (example)
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "secret"}'

# Use token in requests
export TOKEN="your-token-here"
```

### Search Logs
```bash
# Simple search
curl -X POST http://localhost:8000/api/v1/search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "error",
    "time_range": {
      "from": "now-1h",
      "to": "now"
    },
    "size": 100
  }'
```

### Run Aggregation
```bash
# Count logs by level
curl -X POST http://localhost:8000/api/v1/aggregate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "aggregations": {
      "logs_by_level": {
        "terms": {
          "field": "level.keyword"
        }
      }
    },
    "time_range": {
      "from": "now-24h",
      "to": "now"
    }
  }'
```

### Create Alert Rule
```bash
curl -X POST http://localhost:8000/api/v1/alerts/rules \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "High Error Rate",
    "query": "level:ERROR",
    "condition": {
      "type": "threshold",
      "operator": "gt",
      "value": 100
    },
    "interval": "5m",
    "actions": [
      {
        "type": "webhook",
        "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
      }
    ]
  }'
```

---

## API Endpoints Summary

### Search & Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/search` | Search logs |
| `POST` | `/api/v1/aggregate` | Run aggregations |
| `GET` | `/api/v1/saved-searches` | List saved searches |
| `POST` | `/api/v1/saved-searches` | Create saved search |

### Index Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/indices` | List all indices |
| `POST` | `/api/v1/indices` | Create index |
| `DELETE` | `/api/v1/indices/{name}` | Delete index |
| `GET` | `/api/v1/indices/{name}/stats` | Get index stats |

### Alerting
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/alerts/rules` | List alert rules |
| `POST` | `/api/v1/alerts/rules` | Create alert rule |
| `GET` | `/api/v1/alerts/rules/{id}` | Get alert rule |
| `PUT` | `/api/v1/alerts/rules/{id}` | Update alert rule |
| `DELETE` | `/api/v1/alerts/rules/{id}` | Delete alert rule |
| `GET` | `/api/v1/alerts/history` | Get alert history |

### System
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | Health check |
| `GET` | `/api/v1/version` | API version |
| `GET` | `/api/v1/stats` | Platform statistics |

---

## Response Format

### Success Response
```json
{
  "status": "success",
  "data": {
    "results": [...],
    "total": 1234,
    "took_ms": 45
  },
  "meta": {
    "page": 1,
    "page_size": 100,
    "total_pages": 13
  }
}
```

### Error Response
```json
{
  "status": "error",
  "error": {
    "code": "INVALID_QUERY",
    "message": "Query syntax error at line 1",
    "details": {
      "line": 1,
      "column": 15
    }
  }
}
```

---

## Common Query Patterns

### Time-Based Queries
```json
{
  "time_range": {
    "from": "now-1h",
    "to": "now"
  }
}
```

### Field Filtering
```json
{
  "filters": [
    { "field": "level", "operator": "eq", "value": "ERROR" },
    { "field": "service", "operator": "in", "value": ["api", "web"] }
  ]
}
```

### Full-Text Search with Filters
```json
{
  "query": "authentication failed",
  "filters": [
    { "field": "timestamp", "operator": "gte", "value": "now-24h" }
  ]
}
```

---

## SDK Examples

### Python
```python
from vaultize_client import VaultizeClient

client = VaultizeClient(
    base_url="http://localhost:8000",
    api_key="your-api-key"
)

# Search logs
results = client.search(
    query="error",
    time_range={"from": "now-1h", "to": "now"},
    size=100
)

# Run aggregation
agg_results = client.aggregate(
    aggregations={
        "errors_by_service": {
            "terms": {"field": "service.keyword"}
        }
    },
    time_range={"from": "now-24h", "to": "now"}
)
```

### JavaScript
```javascript
const VaultizeClient = require('vaultize-client');

const client = new VaultizeClient({
  baseURL: 'http://localhost:8000',
  apiKey: 'your-api-key'
});

// Search logs
const results = await client.search({
  query: 'error',
  timeRange: {
    from: 'now-1h',
    to: 'now'
  },
  size: 100
});
```

---

## Rate Limiting

- **Default**: 1000 requests per minute per API key
- **Burst**: Up to 100 concurrent requests
- **Headers**: Rate limit info in response headers
  - `X-RateLimit-Limit`: Total requests allowed
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Time when limit resets

---

## Interactive API Documentation

Once the platform is running, interactive API documentation is available at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

---

## Next Steps

1. Review [API Overview](./overview.md) for detailed concepts
2. Check [Authentication](./authentication.md) to set up access
3. Explore [Search API](./search.md) for query capabilities
4. See [OpenAPI Specification](./openapi.yaml) for complete reference

---

**Last Updated**: 2026-02-04
