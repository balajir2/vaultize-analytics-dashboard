# Installation and Integration Guide

> Step-by-step guide to install the Vaultize Analytics Platform and connect it to your existing application

**Authors**: Balaji Rajan and Claude (Anthropic)
**Last Updated**: 2026-03-11
**License**: Apache 2.0
**Estimated Time**: 30-45 minutes (installation + first integration)

---

## Table of Contents

1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [Step 1: Install the Platform](#3-step-1-install-the-platform)
4. [Step 2: Verify Installation](#4-step-2-verify-installation)
5. [Step 3: Generate Sample Data](#5-step-3-generate-sample-data)
6. [Step 4: Connect Your Application](#6-step-4-connect-your-application)
7. [Step 5: Create Dashboards](#7-step-5-create-dashboards)
8. [Step 6: Set Up Alerts](#8-step-6-set-up-alerts)
9. [Step 7: Production Considerations](#9-step-7-production-considerations)
10. [Verification Checklist](#10-verification-checklist)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Overview

The Vaultize Analytics Platform is an on-premise log analytics and observability solution built on open-source components. It provides:

- **Centralized log ingestion** from any application
- **Full-text search** across all logs
- **Real-time dashboards** and visualizations
- **Threshold-based alerting** with webhook notifications
- **REST API** for programmatic access

### Architecture

```
Your Application(s)
        |
        |--- Log files -------> Fluent Bit -----> OpenSearch Cluster
        |--- TCP forward -----> (port 24224)         |
        |--- HTTP POST -------> (port 9200)          |
                                                     v
                                              +--------------+
                                              | Dashboards   |
                                              | - OpenSearch  |  (port 5601)
                                              | - Grafana     |  (port 3100)
                                              +--------------+
                                              | Services     |
                                              | - API        |  (port 8000)
                                              | - Alerting   |  (port 8001)
                                              | - Prometheus |  (port 9090)
                                              +--------------+
```

### Components

| Component | Purpose | Port |
|-----------|---------|------|
| OpenSearch (3 nodes) | Search and analytics engine | 9200 |
| OpenSearch Dashboards | Log exploration and visualization | 5601 |
| Fluent Bit | Log collection and forwarding | 24224 |
| Analytics API | REST API for search and aggregations | 8000 |
| Alerting Service | Threshold-based alerts with webhooks | 8001 |
| Prometheus | Metrics collection (optional) | 9090 |
| Grafana | Unified dashboards (optional) | 3100 |

---

## 2. Prerequisites

### Hardware Requirements

| Environment | CPU | RAM | Disk |
|-------------|-----|-----|------|
| Development / Demo | 4 cores | 8 GB | 50 GB |
| Staging | 8 cores | 16 GB | 200 GB |
| Production | 16+ cores | 32+ GB | 500+ GB SSD |

### Software Requirements

| Software | Minimum Version | Check Command |
|----------|----------------|---------------|
| Docker | 20.10+ | `docker --version` |
| Docker Compose | 2.0+ | `docker compose version` |
| Git | 2.0+ | `git --version` |
| Python | 3.10+ (optional, for data scripts) | `python --version` |

### Network Requirements

Ensure the following ports are available on the host machine:

```
9200  - OpenSearch API
5601  - OpenSearch Dashboards
24224 - Fluent Bit (log ingestion)
8000  - Analytics API
8001  - Alerting Service
9090  - Prometheus
3100  - Grafana
```

---

## 3. Step 1: Install the Platform

### 3.1 Clone the Repository

```bash
git clone https://github.com/balajir2/vaultize-analytics-dashboard.git
cd vaultize-analytics-dashboard
```

### 3.2 Configure Environment

```bash
# Copy the example environment file
cp .env.example .env
```

The defaults work for local development. For production, edit `.env`:

```bash
# Key settings to review
OPENSEARCH_PORT=9200           # OpenSearch API port
GRAFANA_PORT=3100              # Grafana web UI port
API_PORT=8000                  # Analytics API port
ALERTING_API_PORT=8001         # Alerting service port
GRAFANA_ADMIN_PASSWORD=admin   # CHANGE in production
```

### 3.3 Start the Platform

Choose the deployment level that matches your needs:

```bash
# Option A: Core only (OpenSearch + Dashboards + Fluent Bit)
docker compose up -d

# Option B: Core + API + Alerting
docker compose --profile services up -d

# Option C: Full stack (recommended for demos and production)
docker compose --profile metrics --profile services up -d
```

**First startup will take 3-5 minutes** as Docker pulls images and OpenSearch initializes the cluster.

### 3.4 Wait for Services to be Healthy

```bash
# Watch container status until all show "healthy"
docker compose ps
```

Expected output (Option C):

```
NAME                    STATUS                  PORTS
opensearch-node-1       Up (healthy)            0.0.0.0:9200->9200/tcp
opensearch-node-2       Up (healthy)            9200/tcp
opensearch-node-3       Up (healthy)            9200/tcp
opensearch-dashboards   Up (healthy)            0.0.0.0:5601->5601/tcp
fluent-bit              Up                      0.0.0.0:24224->24224/tcp
analytics-api           Up (healthy)            0.0.0.0:8000->8000/tcp
alerting-service        Up (healthy)            0.0.0.0:8001->8001/tcp
prometheus              Up (healthy)            0.0.0.0:9090->9090/tcp
grafana                 Up (healthy)            0.0.0.0:3100->3000/tcp
opensearch-exporter     Up (healthy)            0.0.0.0:9114->9114/tcp
```

---

## 4. Step 2: Verify Installation

Open each service in your browser to confirm everything is running:

| Service | URL | What You Should See |
|---------|-----|---------------------|
| OpenSearch Dashboards | http://localhost:5601 | Dashboard home page |
| Analytics API Docs | http://localhost:8000/docs | Swagger UI with all endpoints |
| Alerting Service Docs | http://localhost:8001/docs | Swagger UI with alert endpoints |
| Grafana | http://localhost:3100 | Login page (admin/admin) |
| Prometheus | http://localhost:9090 | Prometheus targets page |

### Quick Health Check via Command Line

```bash
# OpenSearch cluster health
curl http://localhost:9200/_cluster/health?pretty

# Analytics API health
curl http://localhost:8000/health/

# Alerting service health
curl http://localhost:8001/health/liveness
```

All should return healthy/green status.

---

## 5. Step 3: Generate Sample Data

Before connecting your real application, verify the platform works with sample data.

### Option A: Generic Sample Logs (1,000 logs)

```bash
cd scripts/data
python generate_sample_logs.py
```

### Option B: Document Management Sample Logs (5,000 logs)

This generates realistic Vaultize-style DMS logs with 10 services, 14 users, and 10 departments:

```bash
cd scripts/data
python generate_vaultize_logs.py
```

### Import Pre-Built Dashboards

After generating data, import the OpenSearch dashboards:

```bash
# From the project root directory
cd dashboards/opensearch-dashboards

# Import index pattern, visualizations, and dashboards
curl -X POST "http://localhost:5601/api/saved_objects/_import?overwrite=true" \
  -H "osd-xsrf: true" \
  --form file=@saved-objects/index-pattern.ndjson

curl -X POST "http://localhost:5601/api/saved_objects/_import?overwrite=true" \
  -H "osd-xsrf: true" \
  --form file=@saved-objects/visualizations.ndjson

curl -X POST "http://localhost:5601/api/saved_objects/_import?overwrite=true" \
  -H "osd-xsrf: true" \
  --form file=@saved-objects/dashboards.ndjson
```

**On Windows (PowerShell)**:
```powershell
.\import_dashboards.ps1
```

### Verify Data is Searchable

1. Open **OpenSearch Dashboards** at http://localhost:5601
2. Go to **Discover** (left menu)
3. Select the `logs-*` index pattern
4. Set time range to **Last 3 days**
5. You should see thousands of log entries

Or via API:
```bash
curl "http://localhost:8000/api/v1/search/simple?q=*&size=5"
```

---

## 6. Step 4: Connect Your Existing Application

There are three ways to send logs from your application to the platform. Choose the method that best fits your architecture.

### Method 1: File-Based Ingestion (Simplest)

**Best for**: Applications that already write log files to disk.

**How it works**: Your application writes logs to a shared directory. Fluent Bit monitors this directory and automatically ingests new log lines.

#### Step 1: Prepare Your Log Directory

Create a directory accessible by both your application and the Docker container:

```bash
# The platform already monitors this directory
ls ingestion/sample-logs/
```

#### Step 2: Write JSON Log Files

Your application should write logs in JSON format, one object per line, to files with `.log` extension:

**Python Example**:
```python
import json
import logging
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "@timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": "your-app-name",
            "message": record.getMessage(),
            "host": "your-hostname",
            "module": record.module,
            "function": record.funcName,
        }
        if record.exc_info:
            log_entry["stack_trace"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)

# Configure logger
logger = logging.getLogger("your-app")
handler = logging.FileHandler("/path/to/ingestion/sample-logs/your-app.log")
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Use it
logger.info("Document uploaded successfully")
logger.error("Storage quota exceeded for vault: Finance-Vault")
```

**Java Example (Logback)**:
```xml
<!-- logback.xml -->
<appender name="JSON_FILE" class="ch.qos.logback.core.FileAppender">
    <file>/path/to/ingestion/sample-logs/java-app.log</file>
    <encoder class="net.logstash.logback.encoder.LogstashEncoder">
        <customFields>{"service":"your-java-app"}</customFields>
    </encoder>
</appender>
```

**Node.js Example (Winston)**:
```javascript
const winston = require('winston');

const logger = winston.createLogger({
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  defaultMeta: { service: 'your-node-app' },
  transports: [
    new winston.transports.File({
      filename: '/path/to/ingestion/sample-logs/node-app.log'
    })
  ]
});

logger.info('Document downloaded', { user: 'john.doe', file: 'report.pdf' });
```

#### Step 3: Mount Your Log Directory

If your application runs outside Docker, mount its log directory into the Fluent Bit container. Edit `docker-compose.yml`:

```yaml
fluent-bit:
  volumes:
    - ./ingestion/sample-logs:/app/logs:ro                    # existing
    - /var/log/your-application:/app/external-logs:ro         # add this
```

Then update `ingestion/configs/fluent-bit/fluent-bit.conf` to add a new input:

```ini
[INPUT]
    Name        tail
    Path        /app/external-logs/*.log
    Parser      app_json
    Tag         external.logs
    Refresh_Interval  5
    Read_from_Head    true
```

Restart Fluent Bit:
```bash
docker compose restart fluent-bit
```

---

### Method 2: Forward Protocol (TCP)

**Best for**: Containerized applications, microservices, applications with Fluent Bit or Fluentd agents.

**How it works**: Your application (or a local Fluent Bit agent) sends logs over TCP to the platform's Fluent Bit instance on port 24224.

#### Step 1: Install Fluent Bit on Your Application Server

```bash
# Ubuntu/Debian
curl https://raw.githubusercontent.com/fluent/fluent-bit/master/install.sh | sh

# Or via Docker
docker run -d fluent/fluent-bit:2.2.0 \
  -o forward://ANALYTICS_SERVER_IP:24224
```

#### Step 2: Configure the Local Agent

Create a Fluent Bit config on your application server:

```ini
# /etc/fluent-bit/fluent-bit.conf

[INPUT]
    Name        tail
    Path        /var/log/your-app/*.log
    Parser      json
    Tag         your-app.logs

[OUTPUT]
    Name        forward
    Match       *
    Host        ANALYTICS_SERVER_IP
    Port        24224
```

Replace `ANALYTICS_SERVER_IP` with the IP address of the machine running the analytics platform.

#### Step 3: Verify Logs Arrive

```bash
# Check Fluent Bit metrics on the platform
curl http://ANALYTICS_SERVER_IP:2020/api/v1/metrics

# Search for your app's logs
curl "http://ANALYTICS_SERVER_IP:8000/api/v1/search/simple?q=service:your-app&size=5"
```

#### Docker Compose Example (Sidecar Pattern)

If your application runs in Docker, add Fluent Bit as a sidecar:

```yaml
services:
  your-app:
    image: your-app:latest
    volumes:
      - app-logs:/var/log/app

  fluent-bit-agent:
    image: fluent/fluent-bit:2.2.0
    volumes:
      - app-logs:/var/log/app:ro
      - ./fluent-bit-agent.conf:/fluent-bit/etc/fluent-bit.conf:ro
    depends_on:
      - your-app

volumes:
  app-logs:
```

---

### Method 3: Direct OpenSearch API

**Best for**: Custom scripts, batch imports, applications that can make HTTP calls directly.

**How it works**: Your application POSTs log documents directly to the OpenSearch API.

#### Single Document

```bash
curl -X POST "http://localhost:9200/logs-$(date +%Y-%m-%d)/_doc" \
  -H "Content-Type: application/json" \
  -d '{
    "@timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%S.000Z)'",
    "level": "INFO",
    "service": "your-app",
    "message": "User uploaded document: report.pdf",
    "user": "john.doe",
    "host": "app-server-01"
  }'
```

#### Bulk Import (Recommended for High Volume)

```bash
curl -X POST "http://localhost:9200/_bulk" \
  -H "Content-Type: application/x-ndjson" \
  --data-binary @- << 'EOF'
{"index":{"_index":"logs-2026-03-11"}}
{"@timestamp":"2026-03-11T10:00:00.000Z","level":"INFO","service":"your-app","message":"Document uploaded","user":"john.doe"}
{"index":{"_index":"logs-2026-03-11"}}
{"@timestamp":"2026-03-11T10:00:01.000Z","level":"ERROR","service":"your-app","message":"Storage quota exceeded","user":"jane.smith"}
EOF
```

#### Python Integration

```python
import requests
import json
from datetime import datetime, timezone

OPENSEARCH_URL = "http://localhost:9200"

def send_log(level, service, message, **extra_fields):
    """Send a single log entry to OpenSearch."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    doc = {
        "@timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "service": service,
        "message": message,
        **extra_fields
    }
    requests.post(
        f"{OPENSEARCH_URL}/logs-{today}/_doc",
        json=doc,
        headers={"Content-Type": "application/json"}
    )

# Usage
send_log("INFO", "doc-gateway", "File uploaded: contract.pdf",
         user="balaji.rajan", department="Legal", duration_ms=145)

send_log("ERROR", "vault-storage", "Encryption failed: HSM unavailable",
         user="system", error_code="VLT-5001")
```

---

### Recommended Log Schema

For best results with the pre-built dashboards and alerts, use this field schema:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `@timestamp` | ISO 8601 | Yes | Event timestamp (UTC recommended) |
| `level` | keyword | Yes | DEBUG, INFO, WARN, ERROR, FATAL |
| `service` | keyword | Yes | Application or service name |
| `message` | text | Yes | Human-readable log message |
| `host` | keyword | Recommended | Server hostname |
| `user` | keyword | Recommended | User who triggered the event |
| `department` | keyword | Optional | Organizational department |
| `duration_ms` | integer | Optional | Operation duration in milliseconds |
| `status_code` | integer | Optional | HTTP status code |
| `error_code` | keyword | Optional | Application-specific error code |
| `request_id` | keyword | Optional | Correlation ID for tracing |
| `client_ip` | ip | Optional | Client IP address |
| `stack_trace` | text | Optional | Error stack trace |

---

## 7. Step 5: Create Dashboards

### OpenSearch Dashboards

The platform includes pre-built dashboards. If you haven't imported them yet:

```bash
# From project root
powershell dashboards/opensearch-dashboards/import_dashboards.ps1
# Or on Linux/Mac:
bash dashboards/opensearch-dashboards/import_dashboards.sh
```

**To create custom visualizations:**

1. Open http://localhost:5601
2. Go to **Visualize** > **Create visualization**
3. Choose a chart type (line, bar, pie, data table)
4. Select `logs-*` index pattern
5. Configure metrics and buckets:
   - **Y-axis**: Count (log volume) or Unique Count (unique users)
   - **X-axis**: Date Histogram (@timestamp) or Terms (service, level, user)
6. Save and add to a dashboard

**Example: "Errors by Department" Pie Chart**:
- Visualization type: Pie
- Metrics: Count
- Buckets: Terms on `department.keyword`
- Filter: `level:ERROR OR level:FATAL`

### Grafana Dashboards

The platform includes two auto-provisioned Grafana dashboards:

| Dashboard | URL | Description |
|-----------|-----|-------------|
| Platform Health | http://localhost:3100/d/vaultize-platform-health | Cluster metrics, API performance, service health |
| Log Analytics | http://localhost:3100/d/vaultize-log-analytics | Log volume, error rates, service breakdown, recent errors |

**To create custom Grafana panels:**

1. Open http://localhost:3100 (admin/admin)
2. Go to **Dashboards** > **New Dashboard**
3. Add a panel, select **OpenSearch** datasource
4. Write a Lucene query (e.g., `service:doc-gateway AND level:ERROR`)
5. Choose visualization (time series, bar chart, stat, table)

**Useful Grafana Queries for Document Management:**

| Panel | Query | Visualization |
|-------|-------|---------------|
| Upload Volume | `service:doc-gateway AND message:*uploaded*` | Time series |
| Failed Logins | `service:access-control AND level:ERROR AND message:*login*` | Stat |
| DLP Violations | `service:policy-engine AND level:WARN AND message:*violation*` | Bar chart |
| External Shares | `service:audit-service AND message:*externally*` | Table |
| Storage Warnings | `service:vault-storage AND level:WARN AND message:*utilization*` | Gauge |

---

## 8. Step 6: Set Up Alerts

### Built-In Alert Rules

The platform ships with two alert rules in `configs/alert-rules/`:

| Rule | Trigger | Action |
|------|---------|--------|
| `high-error-rate` | Error count > 100 in 5 minutes | Webhook POST |
| `slow-api-response` | P95 latency > 2 seconds | Webhook POST |

### Create Custom Alert Rules

Create a new JSON file in `configs/alert-rules/`:

```json
{
    "name": "storage-quota-warning",
    "description": "Alert when storage quota warnings spike",
    "enabled": true,
    "schedule": "*/5 * * * *",
    "query": {
        "type": "count",
        "index": "logs-*",
        "query_string": "service:vault-storage AND level:WARN AND message:*quota*",
        "time_range": "5m"
    },
    "condition": {
        "operator": "gt",
        "threshold": 5
    },
    "actions": [
        {
            "type": "webhook",
            "url": "${WEBHOOK_URL:-http://localhost:9999/alerts}",
            "method": "POST",
            "headers": {
                "Content-Type": "application/json"
            },
            "body_template": {
                "alert": "{{alert.name}}",
                "severity": "warning",
                "message": "Storage quota warnings detected: {{alert.current_value}} in last 5 minutes",
                "timestamp": "{{alert.timestamp}}"
            }
        }
    ]
}
```

Reload alert rules without restarting the service:

```bash
curl -X POST http://localhost:8001/api/v1/alerts/reload
```

### Webhook Integration Examples

**Slack:**
```json
{
    "type": "webhook",
    "url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
    "body_template": {
        "text": ":rotating_light: *{{alert.name}}*\nValue: {{alert.current_value}} (threshold: {{alert.threshold}})"
    }
}
```

**Microsoft Teams:**
```json
{
    "type": "webhook",
    "url": "https://outlook.office.com/webhook/YOUR/TEAMS/WEBHOOK",
    "body_template": {
        "title": "Alert: {{alert.name}}",
        "text": "Current value: {{alert.current_value}}, Threshold: {{alert.threshold}}"
    }
}
```

**PagerDuty:**
```json
{
    "type": "webhook",
    "url": "https://events.pagerduty.com/v2/enqueue",
    "body_template": {
        "routing_key": "YOUR_PAGERDUTY_KEY",
        "event_action": "trigger",
        "payload": {
            "summary": "{{alert.name}}: {{alert.current_value}} exceeds {{alert.threshold}}",
            "severity": "error",
            "source": "vaultize-analytics"
        }
    }
}
```

---

## 9. Step 7: Production Considerations

### Security (Opt-In)

Enable authentication and TLS for production deployments:

```bash
# Generate TLS certificates
python scripts/ops/generate_certs.py

# Start with security overlay
docker compose -f docker-compose.yml -f docker-compose.security.yml \
  --profile metrics --profile services up -d

# Initialize security (first time only)
bash scripts/ops/initialize_security.sh
```

Key settings in `.env`:

```bash
AUTH_ENABLED=true                      # Enable JWT authentication
AUTH_ADMIN_PASSWORD=<strong-password>  # Admin password
API_SECRET_KEY=<random-256-bit-key>   # JWT signing key
ENVIRONMENT=production                 # Enforces security checks
```

See [Security Hardening Checklist](../operations/security-hardening-checklist.md) for the full production security guide.

### Backup and Restore

```bash
# Backup all indices
python scripts/ops/backup_opensearch.py

# Restore from backup
python scripts/ops/restore_opensearch.py --snapshot latest
```

See [Disaster Recovery Guide](../operations/disaster-recovery.md) for detailed procedures.

### Resource Sizing

See [Resource Sizing Guide](../operations/resource-sizing-guide.md) for hardware recommendations based on log volume.

### Performance Tuning

See [Performance Tuning Guide](../operations/performance-tuning.md) for OpenSearch optimization.

---

## 10. Verification Checklist

After completing the installation and integration, verify everything works:

### Platform Health

- [ ] All Docker containers show "healthy" (`docker compose ps`)
- [ ] OpenSearch cluster status is "green" (`curl http://localhost:9200/_cluster/health`)
- [ ] Analytics API responds (`curl http://localhost:8000/health/`)
- [ ] Alerting service responds (`curl http://localhost:8001/health/liveness`)

### Data Ingestion

- [ ] Logs from your application appear in OpenSearch Dashboards (http://localhost:5601 > Discover)
- [ ] Log fields are correctly parsed (@timestamp, level, service, message)
- [ ] Time range filter works (logs appear at correct timestamps)
- [ ] Search works (`level:ERROR` returns only error logs)

### Dashboards

- [ ] OpenSearch Operations Dashboard loads with data
- [ ] OpenSearch Analytics Dashboard loads with data
- [ ] Grafana Platform Health dashboard shows metrics
- [ ] Grafana Log Analytics dashboard shows log data

### API Access

- [ ] Simple search returns results: `curl "http://localhost:8000/api/v1/search/simple?q=*&size=5"`
- [ ] Aggregation works: `curl -X POST http://localhost:8000/api/v1/aggregate -H "Content-Type: application/json" -d '{"query":"*","agg_type":"terms","field":"service","size":10}'`

### Alerting

- [ ] Alert rules are loaded: `curl http://localhost:8001/api/v1/alerts/rules`
- [ ] Manual trigger works: `curl -X POST http://localhost:8001/api/v1/alerts/rules/high-error-rate/trigger`

---

## 11. Troubleshooting

### "No data" in Dashboards

1. **Check time range**: Set to "Last 24 hours" or "Last 3 days"
2. **Verify index pattern**: Go to Management > Index Patterns, ensure `logs-*` exists with `@timestamp`
3. **Check data exists**: `curl http://localhost:9200/logs-*/_count`
4. **Check Fluent Bit**: `docker compose logs fluent-bit`

### Logs Not Appearing from Your Application

1. **File-based**: Verify the file is in the mounted directory and has `.log` extension
2. **Forward protocol**: Test connectivity: `echo '{"test":true}' | nc ANALYTICS_SERVER_IP 24224`
3. **Direct API**: Check OpenSearch response for errors in the POST response body
4. **Timestamp format**: Ensure `@timestamp` is ISO 8601 (e.g., `2026-03-11T10:00:00.000Z`)

### OpenSearch Cluster is Yellow/Red

```bash
# Check cluster status
curl http://localhost:9200/_cluster/health?pretty

# Check unassigned shards
curl http://localhost:9200/_cat/shards?v&h=index,shard,prirep,state,unassigned.reason

# Check node status
curl http://localhost:9200/_cat/nodes?v
```

Yellow usually means replicas are unassigned (normal on a single machine). Red means primary shards are missing.

### Container Keeps Restarting

```bash
# Check container logs
docker compose logs <service-name> --tail 50

# Common issues:
# - OpenSearch: insufficient memory (increase OPENSEARCH_JAVA_OPTS)
# - Analytics API: OpenSearch not ready yet (check depends_on)
# - Alerting: Invalid alert rule JSON in configs/alert-rules/
```

### Grafana Shows "Unable to find datasource plugin"

The OpenSearch datasource plugin must be installed. This is handled automatically via `GF_INSTALL_PLUGINS` in docker-compose.yml. If missing:

```bash
docker exec grafana grafana cli plugins install grafana-opensearch-datasource
docker compose restart grafana
```

### Port Already in Use

```bash
# Check what's using a port (Windows)
netstat -ano | findstr :9200

# Check what's using a port (Linux/Mac)
lsof -i :9200

# Change the port in .env
OPENSEARCH_PORT=9201
```

---

## Quick Reference

### Start/Stop Commands

```bash
# Start full stack
docker compose --profile metrics --profile services up -d

# Stop all services
docker compose --profile metrics --profile services down

# Stop and remove all data (DESTRUCTIVE)
docker compose down -v

# View logs
docker compose logs -f analytics-api

# Restart a single service
docker compose restart fluent-bit
```

### Service URLs

| Service | URL |
|---------|-----|
| OpenSearch API | http://localhost:9200 |
| OpenSearch Dashboards | http://localhost:5601 |
| Analytics API (Swagger) | http://localhost:8000/docs |
| Alerting Service (Swagger) | http://localhost:8001/docs |
| Grafana | http://localhost:3100 (admin/admin) |
| Prometheus | http://localhost:9090 |

### Related Documentation

| Document | Description |
|----------|-------------|
| [Quick Start](../deployment/quickstart.md) | Minimal 10-minute setup |
| [Configuration Reference](../deployment/configuration.md) | All environment variables |
| [Log Integration Guide](./log-integration-guide.md) | Detailed integration methods |
| [Security Hardening](../operations/security-hardening-checklist.md) | Production security |
| [Resource Sizing](../operations/resource-sizing-guide.md) | Hardware planning |
| [Testing Guide](../operations/testing-guide.md) | Manual testing procedures |

---

*Authors: Balaji Rajan and Claude (Anthropic) | License: Apache 2.0*
