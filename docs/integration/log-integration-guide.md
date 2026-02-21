# Log Integration Guide

> How to connect your application's logs to the Vaultize Analytics Platform

**Authors**: Balaji Rajan and Claude (Anthropic)
**Last Updated**: 2026-02-21
**License**: Apache 2.0

---

## Overview

This guide explains how to integrate any log-generating system with the Vaultize Analytics Platform. Your application's logs will flow into OpenSearch where they become searchable, visualizable, and alertable.

**Three integration methods** are available:

| Method | Best For | Complexity | Latency |
|--------|----------|------------|---------|
| [File-Based](#method-1-file-based-ingestion) | Applications that write log files | Low | ~5 seconds |
| [Forward Protocol](#method-2-forward-protocol-tcp) | Containerized apps, Fluent Bit agents | Medium | Real-time |
| [Direct API](#method-3-direct-opensearch-api) | Custom scripts, batch imports | Medium | Immediate |

---

## Architecture

```
Your Application
      |
      |--- writes log files ---> /ingestion/sample-logs/ ---> Fluent Bit (tail) ---> OpenSearch
      |
      |--- TCP forward --------> Fluent Bit (port 24224) ---> OpenSearch
      |
      |--- HTTP POST ----------> OpenSearch (port 9200) -----> Searchable
```

Once logs are in OpenSearch, they are automatically available in:
- **OpenSearch Dashboards** (http://localhost:5601) - search, filter, visualize
- **Analytics API** (http://localhost:8000) - programmatic search and aggregations
- **Alerting Service** (http://localhost:8001) - threshold-based alerts
- **Grafana** (http://localhost:3000) - unified dashboards with metrics

---

## Prerequisites

Start the platform before integrating:

```bash
# Core stack (OpenSearch, Dashboards, Fluent Bit)
docker compose up -d

# With API and Alerting services
docker compose --profile services up -d

# With metrics (Prometheus, Grafana, OpenSearch Exporter)
docker compose --profile metrics --profile services up -d
```

Verify services are healthy:

```bash
docker compose ps
```

---

## Method 1: File-Based Ingestion

**The simplest method.** Drop log files into a shared directory and Fluent Bit automatically reads, parses, and sends them to OpenSearch.

### Step 1: Prepare Your Log Files

Fluent Bit monitors two file patterns:

| Pattern | Parser | Format |
|---------|--------|--------|
| `*.log` | `app_json` | JSON lines (one JSON object per line) |
| `*.txt` | `app_structured` | Structured text (timestamp, level, message) |

### Step 2: Format Your Logs

**JSON format (recommended)** - save as `*.log`:

```json
{"timestamp": "2026-02-21T10:30:00Z", "level": "INFO", "service": "my-app", "message": "User login successful", "user_id": "u-1234"}
{"timestamp": "2026-02-21T10:30:01Z", "level": "ERROR", "service": "my-app", "message": "Database connection timeout", "db_host": "db-01"}
{"timestamp": "2026-02-21T10:30:02Z", "level": "WARN", "service": "my-app", "message": "Rate limit approaching", "current_rate": 95}
```

**Required fields**: `timestamp`, `level`, `message`
**Recommended fields**: `service`, `host`, `environment`
**Optional fields**: Any additional key-value pairs you want searchable

**Structured text format** - save as `*.txt`:

```
2026-02-21T10:30:00Z INFO my-app User login successful
2026-02-21T10:30:01Z ERROR my-app Database connection timeout
2026-02-21T10:30:02Z WARN my-app Rate limit approaching
```

### Step 3: Drop Files into the Shared Directory

Copy your log files to `ingestion/sample-logs/`:

```bash
# From your project root
cp /path/to/your/app.log ingestion/sample-logs/

# Or write directly
your-application --log-file ./ingestion/sample-logs/my-app.log
```

Fluent Bit reads from the head of new files and tracks position, so:
- New files are read from the beginning
- Appended lines are picked up within ~5 seconds (Refresh_Interval)
- Position is tracked in a DB file, so restarts don't re-read old lines

### Step 4: Verify Ingestion

Check your logs arrived in OpenSearch:

```bash
# Count documents
curl http://localhost:9200/logs-*/_count?pretty

# Search for your service
curl "http://localhost:8000/api/v1/search/simple?q=service:my-app&size=5"
```

Or open OpenSearch Dashboards at http://localhost:5601 and search in the Discover tab.

### Step 5: Configure Your Application

To continuously send logs, configure your application to write to the shared directory:

**Python (logging module)**:
```python
import logging
import json
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": "my-app",
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)

# Set up handler writing to the shared directory
handler = logging.FileHandler("/path/to/ingestion/sample-logs/my-app.log")
handler.setFormatter(JSONFormatter())

logger = logging.getLogger("my-app")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Use it
logger.info("Application started")
logger.error("Connection failed", exc_info=True)
```

**Java (Log4j2 JSON layout)**:
```xml
<Appenders>
    <File name="JsonLog" fileName="/path/to/ingestion/sample-logs/my-app.log">
        <JsonLayout compact="true" eventEol="true">
            <KeyValuePair key="service" value="my-app"/>
        </JsonLayout>
    </File>
</Appenders>
```

**Node.js (Winston)**:
```javascript
const winston = require('winston');

const logger = winston.createLogger({
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  defaultMeta: { service: 'my-app' },
  transports: [
    new winston.transports.File({
      filename: '/path/to/ingestion/sample-logs/my-app.log'
    })
  ]
});

logger.info('Application started');
logger.error('Connection failed', { db_host: 'db-01' });
```

### Docker Volume Mount

If your application runs in Docker, mount the shared logs directory:

```yaml
# In your application's docker-compose.yml
services:
  my-app:
    image: my-app:latest
    volumes:
      - ./ingestion/sample-logs:/app/logs
    environment:
      - LOG_FILE=/app/logs/my-app.log
```

---

## Method 2: Forward Protocol (TCP)

Send logs directly to Fluent Bit over TCP using the Forward protocol. This is the standard method for containerized applications.

### Step 1: Send Logs via Docker Log Driver

The simplest approach for Docker containers:

```yaml
# In your application's docker-compose.yml
services:
  my-app:
    image: my-app:latest
    logging:
      driver: fluentd
      options:
        fluentd-address: localhost:24224
        tag: app.my-app
```

### Step 2: Send Logs via Fluent Bit Client Libraries

**Python (fluent-logger)**:

```bash
pip install fluent-logger
```

```python
from fluent import sender
from datetime import datetime, timezone

# Connect to Fluent Bit
logger = sender.FluentSender('app', host='localhost', port=24224)

# Send a log event
logger.emit('my-app', {
    'timestamp': datetime.now(timezone.utc).isoformat(),
    'level': 'INFO',
    'service': 'my-app',
    'message': 'User login successful',
    'user_id': 'u-1234'
})
```

**Node.js (fluent-logger)**:

```bash
npm install fluent-logger
```

```javascript
const fluent = require('fluent-logger');

fluent.configure('app', {
  host: 'localhost',
  port: 24224,
  timeout: 3.0
});

fluent.emit('my-app', {
  timestamp: new Date().toISOString(),
  level: 'INFO',
  service: 'my-app',
  message: 'User login successful'
});
```

### Step 3: Verify

```bash
# Check Fluent Bit is receiving
docker compose logs fluent-bit | tail -5

# Search via API
curl "http://localhost:8000/api/v1/search/simple?q=service:my-app"
```

---

## Method 3: Direct OpenSearch API

For batch imports or custom integration, write directly to OpenSearch.

### Single Document

```bash
curl -X POST "http://localhost:9200/logs-$(date +%Y.%m.%d)/_doc" \
  -H "Content-Type: application/json" \
  -d '{
    "@timestamp": "2026-02-21T10:30:00Z",
    "level": "INFO",
    "service": "my-app",
    "message": "Direct API log entry",
    "host": "server-01"
  }'
```

### Bulk Import

For high-volume imports, use the Bulk API:

```bash
curl -X POST "http://localhost:9200/logs-2026.02.21/_bulk" \
  -H "Content-Type: application/x-ndjson" \
  --data-binary @- << 'EOF'
{"index":{}}
{"@timestamp":"2026-02-21T10:00:00Z","level":"INFO","service":"my-app","message":"Server started"}
{"index":{}}
{"@timestamp":"2026-02-21T10:00:01Z","level":"ERROR","service":"my-app","message":"DB connection failed"}
{"index":{}}
{"@timestamp":"2026-02-21T10:00:02Z","level":"INFO","service":"my-app","message":"Retry succeeded"}
EOF
```

### Python Bulk Import

```python
from opensearchpy import OpenSearch, helpers

client = OpenSearch(
    hosts=[{"host": "localhost", "port": 9200}],
    use_ssl=False
)

logs = [
    {
        "_index": "logs-2026.02.21",
        "@timestamp": "2026-02-21T10:00:00Z",
        "level": "INFO",
        "service": "my-app",
        "message": "Server started"
    },
    {
        "_index": "logs-2026.02.21",
        "@timestamp": "2026-02-21T10:00:01Z",
        "level": "ERROR",
        "service": "my-app",
        "message": "Database connection failed"
    }
]

helpers.bulk(client, logs)
print(f"Imported {len(logs)} documents")
```

### Use the Sample Data Generator

The platform includes a built-in sample data generator:

```bash
cd scripts/data
python generate_sample_logs.py
```

This generates 1,000 realistic log entries across 5 services, useful for testing dashboards and alerts.

---

## Log Format Best Practices

### Required Fields

Every log entry should include at minimum:

| Field | Type | Example | Purpose |
|-------|------|---------|---------|
| `timestamp` or `@timestamp` | ISO 8601 | `2026-02-21T10:30:00Z` | When the event occurred |
| `level` | String | `INFO`, `ERROR`, `WARN`, `DEBUG`, `FATAL` | Severity classification |
| `message` | String | `User login successful` | Human-readable description |

### Recommended Fields

| Field | Type | Example | Purpose |
|-------|------|---------|---------|
| `service` | String | `api-service`, `auth-service` | Which application generated the log |
| `host` | String | `server-01`, `pod-abc123` | Which server/container |
| `environment` | String | `production`, `staging` | Deployment environment |
| `trace_id` | String | `abc123def456` | Request correlation |
| `user_id` | String | `u-1234` | User context |

### Formatting Tips

1. **Use UTC timestamps**: Always use ISO 8601 with timezone (`Z` or `+00:00`)
2. **Consistent log levels**: Stick to `DEBUG`, `INFO`, `WARN`, `ERROR`, `FATAL`
3. **Structured data**: Use JSON wherever possible (much easier to search and filter)
4. **Keep messages concise**: Put details in separate fields, not in the message string
5. **Include context**: Add request IDs, user IDs, and service names for correlation

**Good example**:
```json
{"timestamp": "2026-02-21T10:30:00Z", "level": "ERROR", "service": "payment-service", "message": "Payment failed", "order_id": "ord-789", "error_code": "CARD_DECLINED", "user_id": "u-1234"}
```

**Bad example**:
```
ERROR: Payment failed for order ord-789 with error CARD_DECLINED for user u-1234 at 2026-02-21 10:30:00
```

---

## Setting Up Alerts on Your Logs

Once your logs are flowing, create alerts to detect issues automatically.

### Step 1: Create an Alert Rule

Create a JSON file in `configs/alert-rules/`:

```json
{
  "name": "my-app-high-errors",
  "description": "Alert when my-app error rate exceeds threshold",
  "enabled": true,
  "query": {
    "index": "logs-*",
    "type": "count",
    "filter": "service:my-app AND level:ERROR",
    "time_range": "5m"
  },
  "condition": {
    "operator": "gt",
    "threshold": 50
  },
  "schedule": {
    "interval": "1m"
  },
  "throttle": {
    "value": 15,
    "unit": "minutes"
  },
  "actions": [
    {
      "type": "webhook",
      "config": {
        "url": "${ALERT_WEBHOOK_URL}",
        "method": "POST",
        "headers": {
          "Content-Type": "application/json"
        },
        "body": {
          "text": "Alert: {{alert.name}} - {{alert.description}}. Current value: {{alert.current_value}}"
        }
      }
    }
  ],
  "metadata": {
    "severity": "high",
    "category": "application",
    "owner": "your-team"
  }
}
```

### Step 2: Reload Rules

```bash
curl -X POST http://localhost:8001/api/v1/alerts/rules/reload
```

### Step 3: Verify

```bash
# Check rule loaded
curl http://localhost:8001/api/v1/alerts/rules | python -m json.tool

# Manually trigger evaluation
curl -X POST http://localhost:8001/api/v1/alerts/rules/my-app-high-errors/trigger
```

---

## Monitoring Your Integration

### Check Fluent Bit Metrics

Fluent Bit exposes metrics on port 2020:

```bash
# Fluent Bit internal metrics
curl http://localhost:2020/api/v1/metrics/prometheus
```

### Check Prometheus Targets

Open Prometheus at http://localhost:9090/targets to verify all scrape targets are UP:

| Target | Port | Metrics Path |
|--------|------|-------------|
| fluent-bit | 2020 | /api/v1/metrics/prometheus |
| analytics-api | 8000 | /metrics |
| alerting-service | 8001 | /metrics |
| opensearch-exporter | 9114 | /metrics |

### Check Grafana Dashboard

Open Grafana at http://localhost:3000 and view the **Vaultize Platform Health** dashboard for:
- API and Alerting request rates
- P95 latency
- OpenSearch cluster health, node count, and active shards
- Log ingestion metrics from Fluent Bit

---

## Troubleshooting

### Logs not appearing in OpenSearch

1. **Check Fluent Bit is running**: `docker compose logs fluent-bit`
2. **Check file permissions**: Ensure the log file is readable
3. **Check file format**: JSON files must have valid JSON on each line
4. **Check index exists**: `curl http://localhost:9200/_cat/indices?v`
5. **Check Fluent Bit metrics**: `curl http://localhost:2020/api/v1/metrics`

### Logs appearing but not searchable

1. **Check index pattern**: In OpenSearch Dashboards, verify `logs-*` index pattern exists
2. **Check time range**: Expand the time range in Dashboards to cover your log timestamps
3. **Check field mappings**: `curl http://localhost:9200/logs-*/_mapping?pretty`

### Forward protocol not working

1. **Check port**: `telnet localhost 24224`
2. **Check Docker network**: Ensure your app can reach Fluent Bit
3. **Check Fluent Bit logs**: `docker compose logs fluent-bit | grep -i error`

### High latency or dropped logs

1. **Check buffer limits**: Fluent Bit has `Mem_Buf_Limit 5MB` per input
2. **Check OpenSearch health**: `curl http://localhost:9200/_cluster/health?pretty`
3. **Scale up**: Increase Fluent Bit buffer or add more OpenSearch nodes

---

## Quick Reference

### Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| OpenSearch | http://localhost:9200 | Direct API access |
| OpenSearch Dashboards | http://localhost:5601 | Visual log exploration |
| Analytics API | http://localhost:8000 | Programmatic search |
| Analytics API Docs | http://localhost:8000/docs | Swagger UI |
| Alerting Service | http://localhost:8001 | Alert management |
| Alerting Service Docs | http://localhost:8001/docs | Swagger UI |
| Prometheus | http://localhost:9090 | Metrics (optional) |
| Grafana | http://localhost:3000 | Unified dashboards (optional) |
| Fluent Bit Metrics | http://localhost:2020 | Ingestion metrics |

### Integration Checklist

- [ ] Platform running (`docker compose up -d`)
- [ ] Chose integration method (file, forward, or API)
- [ ] Log format includes timestamp, level, message
- [ ] Logs arriving in OpenSearch (check via API or Dashboards)
- [ ] Index pattern `logs-*` created in Dashboards
- [ ] Can search your logs in Discover tab
- [ ] (Optional) Alert rules configured for your service
- [ ] (Optional) Grafana dashboard showing your service metrics

---

**Related Documentation**:
- [Quick Start Guide](../deployment/quickstart.md) - Platform deployment
- [Configuration Reference](../deployment/configuration.md) - Environment variables
- [Testing Guide](../operations/testing-guide.md) - Manual testing walkthrough
- [DRM Integration Guide](./DRM_INTEGRATION_GUIDE.md) - Specialized DRM log integration
