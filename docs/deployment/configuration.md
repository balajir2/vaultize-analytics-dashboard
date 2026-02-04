# Configuration Reference

> Complete configuration guide for all deployment environments

**Authors**: Balaji Rajan and Claude (Anthropic)
**Last Updated**: 2026-02-04

---

## Overview

The Vaultize Analytics Platform uses **environment-based configuration** to support multiple deployment scenarios without code changes.

**Configuration Priority**:
1. Environment variables (highest priority)
2. `.env` file
3. Default values in code (fallback)

---

## Environment-Specific URLs

### Development (Local)
```bash
# .env.development
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200
OPENSEARCH_DASHBOARDS_URL=http://localhost:5601
API_BASE_URL=http://localhost:8000
GRAFANA_URL=http://localhost:3000
PROMETHEUS_URL=http://localhost:9090
```

### Staging
```bash
# .env.staging
OPENSEARCH_HOST=opensearch.staging.internal
OPENSEARCH_PORT=9200
OPENSEARCH_DASHBOARDS_URL=https://dashboards.staging.example.com
API_BASE_URL=https://api.staging.example.com
GRAFANA_URL=https://grafana.staging.example.com
PROMETHEUS_URL=https://prometheus.staging.example.com
```

### Production
```bash
# .env.production
OPENSEARCH_HOST=opensearch.prod.internal
OPENSEARCH_PORT=9200
OPENSEARCH_DASHBOARDS_URL=https://dashboards.example.com
API_BASE_URL=https://api.example.com
GRAFANA_URL=https://grafana.example.com
PROMETHEUS_URL=https://prometheus.example.com
```

---

## Complete Environment Variables Reference

### OpenSearch Configuration

| Variable | Default | Description | Example |
|----------|---------|-------------|---------|
| `OPENSEARCH_HOST` | `localhost` | OpenSearch hostname | `opensearch.example.com` |
| `OPENSEARCH_PORT` | `9200` | OpenSearch port | `9200` |
| `OPENSEARCH_SCHEME` | `http` | Protocol (http/https) | `https` |
| `OPENSEARCH_USER` | `admin` | Admin username | `admin` |
| `OPENSEARCH_PASSWORD` | `admin` | Admin password | `${SECRET_PASSWORD}` |
| `OPENSEARCH_VERIFY_CERTS` | `false` | Verify SSL certificates | `true` |

**Full URL Construction**:
```
${OPENSEARCH_SCHEME}://${OPENSEARCH_HOST}:${OPENSEARCH_PORT}
```

### OpenSearch Dashboards

| Variable | Default | Description | Example |
|----------|---------|-------------|---------|
| `OPENSEARCH_DASHBOARDS_HOST` | `0.0.0.0` | Bind address | `0.0.0.0` |
| `OPENSEARCH_DASHBOARDS_PORT` | `5601` | Dashboard port | `5601` |
| `OPENSEARCH_DASHBOARDS_BASE_PATH` | `` | Base path for reverse proxy | `/dashboards` |
| `OPENSEARCH_DASHBOARDS_PUBLIC_URL` | `` | Public-facing URL | `https://dashboards.example.com` |

### Analytics API

| Variable | Default | Description | Example |
|----------|---------|-------------|---------|
| `API_HOST` | `0.0.0.0` | Bind address | `0.0.0.0` |
| `API_PORT` | `8000` | API port | `8000` |
| `API_BASE_URL` | `http://localhost:8000` | Public API URL | `https://api.example.com` |
| `API_ROOT_PATH` | `/api/v1` | API path prefix | `/api/v1` |
| `API_CORS_ORIGINS` | `*` | Allowed CORS origins | `https://example.com` |

### Fluent Bit

| Variable | Default | Description | Example |
|----------|---------|-------------|---------|
| `FLUENT_BIT_OPENSEARCH_HOST` | `opensearch-node-1` | Output host | `opensearch.internal` |
| `FLUENT_BIT_OPENSEARCH_PORT` | `9200` | Output port | `9200` |
| `FLUENT_BIT_HTTP_PORT` | `2020` | Metrics port | `2020` |
| `FLUENT_BIT_FORWARD_PORT` | `24224` | Forward input port | `24224` |

### Prometheus

| Variable | Default | Description | Example |
|----------|---------|-------------|---------|
| `PROMETHEUS_URL` | `http://localhost:9090` | Prometheus URL | `https://prometheus.example.com` |
| `PROMETHEUS_RETENTION` | `15d` | Data retention | `30d` |

### Grafana

| Variable | Default | Description | Example |
|----------|---------|-------------|---------|
| `GRAFANA_URL` | `http://localhost:3000` | Grafana URL | `https://grafana.example.com` |
| `GRAFANA_ADMIN_USER` | `admin` | Admin username | `admin` |
| `GRAFANA_ADMIN_PASSWORD` | `admin` | Admin password | `${SECRET_PASSWORD}` |
| `GRAFANA_ROOT_URL` | `http://localhost:3000` | Public-facing URL | `https://grafana.example.com` |

### Alerting

| Variable | Default | Description | Example |
|----------|---------|-------------|---------|
| `ALERT_WEBHOOK_URL` | `` | Default webhook URL | `https://hooks.slack.com/...` |
| `ALERTING_CHECK_INTERVAL` | `60` | Check interval (seconds) | `300` |
| `ALERTING_WEBHOOK_TIMEOUT` | `10` | Webhook timeout (seconds) | `30` |

---

## Deployment Scenarios

### Scenario 1: Single Server (Docker Compose)

**Network**: All services on same Docker network
**URLs**: Use Docker service names

```bash
# .env
OPENSEARCH_HOST=opensearch-node-1
OPENSEARCH_DASHBOARDS_URL=http://localhost:5601
API_BASE_URL=http://localhost:8000
```

**Access**:
- Internal (containers): `http://opensearch-node-1:9200`
- External (browser): `http://localhost:5601`

---

### Scenario 2: Multi-Server Deployment

**Network**: Services on different servers
**URLs**: Use actual hostnames/IPs

```bash
# .env
OPENSEARCH_HOST=10.0.1.10
OPENSEARCH_DASHBOARDS_URL=http://10.0.1.11:5601
API_BASE_URL=http://10.0.1.12:8000
```

---

### Scenario 3: Behind Reverse Proxy (Nginx/Traefik)

**Network**: Services behind load balancer
**URLs**: Use public domain names

```bash
# .env
OPENSEARCH_HOST=opensearch.internal
OPENSEARCH_DASHBOARDS_URL=https://dashboards.example.com
API_BASE_URL=https://api.example.com

# Additional config for path-based routing
OPENSEARCH_DASHBOARDS_BASE_PATH=/dashboards
API_ROOT_PATH=/api
```

**Nginx Config Example**:
```nginx
server {
    server_name example.com;

    location /dashboards/ {
        proxy_pass http://opensearch-dashboards:5601/;
    }

    location /api/ {
        proxy_pass http://analytics-api:8000/;
    }
}
```

---

### Scenario 4: Kubernetes Deployment

**Network**: Kubernetes Services
**URLs**: Use service DNS names

```bash
# .env
OPENSEARCH_HOST=opensearch-cluster.vaultize.svc.cluster.local
OPENSEARCH_PORT=9200
OPENSEARCH_DASHBOARDS_URL=http://opensearch-dashboards.vaultize.svc.cluster.local:5601
API_BASE_URL=http://analytics-api.vaultize.svc.cluster.local:8000
```

---

## Configuration Best Practices

### 1. Never Hardcode URLs

**❌ Bad**:
```python
OPENSEARCH_URL = "http://localhost:9200"
```

**✅ Good**:
```python
import os

OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "localhost")
OPENSEARCH_PORT = os.getenv("OPENSEARCH_PORT", "9200")
OPENSEARCH_SCHEME = os.getenv("OPENSEARCH_SCHEME", "http")
OPENSEARCH_URL = f"{OPENSEARCH_SCHEME}://{OPENSEARCH_HOST}:{OPENSEARCH_PORT}"
```

### 2. Use Environment-Specific Files

```bash
# Directory structure
.env.example           # Template with all variables
.env.development       # Local development
.env.staging           # Staging environment
.env.production        # Production environment
```

**Load environment-specific file**:
```bash
# Development
docker compose --env-file .env.development up

# Production
docker compose --env-file .env.production up
```

### 3. Secrets Management

**❌ Never commit secrets**:
- `.env.production` should NOT be in Git
- Use `.gitignore` to exclude it

**✅ Use secrets management**:
```bash
# Option 1: Docker secrets
echo "my-password" | docker secret create opensearch_password -

# Option 2: Environment variable injection
export OPENSEARCH_PASSWORD=$(vault read -field=password secret/opensearch)

# Option 3: HashiCorp Vault, AWS Secrets Manager, etc.
```

### 4. Validate Configuration on Startup

**Example validation script**:
```python
# analytics/api/app/config.py
import os
from typing import Optional

class Settings:
    opensearch_host: str = os.getenv("OPENSEARCH_HOST", "localhost")
    opensearch_port: int = int(os.getenv("OPENSEARCH_PORT", "9200"))

    def validate(self):
        required = ["OPENSEARCH_HOST", "OPENSEARCH_PORT"]
        missing = [var for var in required if not os.getenv(var)]

        if missing:
            raise ValueError(f"Missing required environment variables: {missing}")

settings = Settings()
settings.validate()
```

---

## Dynamic URL Configuration

### For Docker Compose

Services use **Docker network DNS**:
```yaml
services:
  analytics-api:
    environment:
      # Uses Docker service name, works across all environments
      - OPENSEARCH_HOST=opensearch-node-1

  fluent-bit:
    environment:
      # Same pattern
      - OPENSEARCH_HOST=opensearch-node-1
```

### For External Access

Public URLs configured via environment:
```bash
# Users access via these URLs (configured per environment)
OPENSEARCH_DASHBOARDS_PUBLIC_URL=https://dashboards.example.com
API_PUBLIC_URL=https://api.example.com
```

---

## Example: Complete Production Configuration

```bash
# .env.production

# ============================================================================
# OpenSearch Cluster
# ============================================================================
OPENSEARCH_HOST=opensearch-lb.prod.internal
OPENSEARCH_PORT=9200
OPENSEARCH_SCHEME=https
OPENSEARCH_USER=admin
OPENSEARCH_PASSWORD=${VAULT_OPENSEARCH_PASSWORD}
OPENSEARCH_VERIFY_CERTS=true

# Public URL for documentation/links
OPENSEARCH_DASHBOARDS_PUBLIC_URL=https://logs.example.com

# ============================================================================
# API Configuration
# ============================================================================
API_HOST=0.0.0.0
API_PORT=8000
API_BASE_URL=https://api.example.com
API_ROOT_PATH=/api/v1
API_CORS_ORIGINS=https://example.com,https://app.example.com
API_WORKERS=4
API_LOG_LEVEL=INFO

# ============================================================================
# Alerting
# ============================================================================
ALERT_WEBHOOK_URL=https://hooks.slack.com/services/PROD/WEBHOOK/URL
ALERTING_CHECK_INTERVAL=300
ALERTING_WEBHOOK_TIMEOUT=30

# ============================================================================
# Monitoring
# ============================================================================
PROMETHEUS_URL=https://prometheus.example.com
GRAFANA_URL=https://grafana.example.com
GRAFANA_ROOT_URL=https://grafana.example.com

# ============================================================================
# Security
# ============================================================================
ENVIRONMENT=production
DEBUG=false
```

---

## Updating Configuration

### Development to Staging

1. Copy `.env.development` to `.env.staging`
2. Update URLs to staging hostnames
3. Update credentials to staging secrets
4. Test connectivity: `./scripts/ops/test-connection.sh`

### Staging to Production

1. Copy `.env.staging` to `.env.production`
2. Update URLs to production hostnames
3. **Use production secrets** (never copy passwords!)
4. Enable security features (TLS, auth)
5. Test in production-like environment first

---

## Configuration Checklist

Before deploying to a new environment:

- [ ] All URLs updated (no localhost)
- [ ] Credentials rotated (no default passwords)
- [ ] TLS enabled for production
- [ ] Firewall rules configured
- [ ] DNS records created
- [ ] Health checks passing
- [ ] Backup strategy in place
- [ ] Monitoring configured
- [ ] Logs flowing correctly
- [ ] Alerts tested

---

## Troubleshooting

### Connection Refused

**Problem**: Service can't connect to OpenSearch

**Check**:
```bash
# Verify host is reachable
ping $OPENSEARCH_HOST

# Verify port is open
telnet $OPENSEARCH_HOST $OPENSEARCH_PORT

# Check environment variables are loaded
docker compose config | grep OPENSEARCH_HOST
```

### Wrong URL in Logs

**Problem**: Logs show localhost instead of actual URL

**Solution**: Update `API_BASE_URL` to public-facing URL

### CORS Errors

**Problem**: Browser blocks API requests

**Solution**: Add frontend URL to `API_CORS_ORIGINS`

---

## Related Documentation

- [Quick Start](./quickstart.md) - Local development setup
- [Docker Compose Deployment](./docker-compose.md) - Single-server deployment
- [Kubernetes Deployment](./kubernetes.md) - Multi-server deployment
- [Security Guide](../operations/security-ops.md) - SSL/TLS configuration

---

**Last Updated**: 2026-02-04
