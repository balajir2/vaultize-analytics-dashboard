# Quick Start Guide

> Get the Vaultize Analytics Platform running in under 10 minutes

**Authors**: Balaji Rajan and Claude (Anthropic)
**Last Updated**: 2026-02-17

---

## Prerequisites

Before you begin, ensure you have:

- [x] **Docker** 20.10 or later ([Install Docker](https://docs.docker.com/get-docker/))
- [x] **Docker Compose** 2.0 or later ([Install Docker Compose](https://docs.docker.com/compose/install/))
- [x] **8GB RAM minimum** (16GB+ recommended for production)
- [x] **50GB disk space** (plus space for log retention)
- [x] **Linux, macOS, or Windows** with WSL2

**Verify Installation**:
```bash
docker --version        # Should be 20.10+
docker compose version  # Should be 2.0+
```

---

## Quick Start (Development)

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-org/vaultize-analytics.git
cd vaultize-analytics
```

### Step 2: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Optional: Edit if needed (defaults work for local development)
nano .env
```

### Step 3: Start the Platform

```bash
# Start core services (OpenSearch + Dashboards + Fluent Bit)
docker compose up -d

# Check all services are running
docker compose ps
```

**Expected Output**:
```
NAME                   STATUS    PORTS
opensearch-node-1      healthy   0.0.0.0:9200->9200/tcp
opensearch-node-2      healthy
opensearch-node-3      healthy
opensearch-dashboards  healthy   0.0.0.0:5601->5601/tcp
fluent-bit             running   0.0.0.0:24224->24224/tcp
```

### Step 4: Verify Installation

```bash
# Check OpenSearch cluster health
curl http://localhost:9200/_cluster/health?pretty

# Expected response: "status": "green"
```

### Step 5: Access the Platform

Open your browser and navigate to:

**OpenSearch Dashboards**: http://localhost:5601

**Default Credentials**: No authentication required in development mode

---

## First Steps After Installation

### 1. Create Index Pattern

1. Open OpenSearch Dashboards: http://localhost:5601
2. Click **☰ Menu** → **Stack Management** → **Index Patterns**
3. Click **Create index pattern**
4. Enter pattern: `logs-*`
5. Select time field: `@timestamp`
6. Click **Create index pattern**

### 2. View Logs

1. Click **☰ Menu** → **Discover**
2. Select `logs-*` index pattern
3. Adjust time range (top-right)
4. Start exploring your logs!

### 3. Send Test Logs

```bash
# Send a test log via Fluent Bit
echo '{"message": "Hello from Vaultize!", "level": "INFO", "service": "test"}' | \
  docker run --rm -i --network vaultize-analytics_vaultize-network \
  fluent/fluent-bit:2.2.0 \
  -i stdin -t logs -o forward://fluent-bit:24224
```

Or use our test script:
```bash
./scripts/dev/generate-sample-logs.sh
```

---

## Optional: Start with Metrics (Prometheus + Grafana)

```bash
# Stop current services
docker compose down

# Start with metrics profile
docker compose --profile metrics up -d

# Access services
open http://localhost:3000  # Grafana (admin/admin)
open http://localhost:9090  # Prometheus
```

---

## Optional: Start Complete Stack (All Services)

```bash
# Start everything including API and Alerting services
docker compose --profile metrics --profile services up -d
```

**Services Available**:
- **OpenSearch Dashboards**: http://localhost:5601
- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090
- **Analytics API**: http://localhost:8000/docs

---

## Stopping the Platform

```bash
# Stop all services (data preserved)
docker compose down

# Stop and remove all data (DESTRUCTIVE)
docker compose down -v
```

---

## Troubleshooting

### Services Won't Start

**Problem**: `docker compose up` fails

**Solutions**:
```bash
# Check for port conflicts
lsof -i :9200  # OpenSearch
lsof -i :5601  # Dashboards

# Check Docker is running
docker ps

# Check disk space
df -h

# View service logs
docker compose logs opensearch-node-1
```

### Cluster Status is Yellow/Red

**Problem**: OpenSearch cluster unhealthy

**Solutions**:
```bash
# Check cluster health
curl http://localhost:9200/_cluster/health?pretty

# If yellow: Wait for all nodes to join (can take 1-2 minutes)
# If red: Check logs
docker compose logs opensearch-node-1
```

### Can't Access OpenSearch Dashboards

**Problem**: http://localhost:5601 not loading

**Solutions**:
```bash
# Check if service is running
docker compose ps opensearch-dashboards

# Check logs for errors
docker compose logs opensearch-dashboards

# Restart the service
docker compose restart opensearch-dashboards
```

### Out of Memory Errors

**Problem**: Services crashing with OOM

**Solutions**:
```bash
# Reduce memory limits in .env
OPENSEARCH_JAVA_OPTS=-Xms256m -Xmx256m  # Lower for development

# Or increase Docker memory limit
# Docker Desktop → Settings → Resources → Memory → 8GB+
```

---

## Common Commands

```bash
# View all services status
docker compose ps

# View logs (all services)
docker compose logs -f

# View logs (specific service)
docker compose logs -f opensearch-node-1

# Restart a service
docker compose restart opensearch-dashboards

# Stop services
docker compose down

# Start services
docker compose up -d

# Remove all data and start fresh
docker compose down -v
docker compose up -d
```

---

## Directory Structure

After cloning, you'll see:

```
vaultize-analytics/
├── docker-compose.yml          # Main deployment file
├── .env.example                # Environment template
├── configs/                    # Configuration files
│   ├── index-templates/        # OpenSearch templates
│   ├── ilm-policies/           # Lifecycle policies
│   └── alert-rules/            # Alert definitions
├── infrastructure/             # Docker configs
│   └── docker/
│       ├── opensearch/
│       ├── opensearch-dashboards/
│       └── fluent-bit/
├── ingestion/                  # Log ingestion configs
│   └── configs/
│       ├── fluent-bit/
│       └── prometheus/
├── docs/                       # Documentation
└── scripts/                    # Operational scripts
```

---

## What's Next?

Now that you have the platform running, explore:

1. **[User Guides](../user-guides/README.md)** - Search cheat sheet, dashboards, alerts
2. **[Configuration Guide](./configuration.md)** - Customize settings
3. **[Testing Guide](../operations/testing-guide.md)** - Manual testing walkthrough
4. **API Documentation** - Interactive Swagger UI at `http://localhost:8000/docs`

---

## Development Workflow

### Daily Development

```bash
# Start services
docker compose up -d

# Work on code...

# View logs
docker compose logs -f

# Restart after code changes
docker compose restart analytics-api

# Stop when done
docker compose down
```

### Testing Changes

```bash
# Rebuild services after code changes
docker compose up -d --build

# Run tests
./scripts/dev/run-tests.sh

# Check health
./scripts/ops/health-check.sh
```

---

## Quick Reference

| Service | URL | Default Credentials |
|---------|-----|---------------------|
| **OpenSearch** | http://localhost:9200 | None (dev mode) |
| **OpenSearch Dashboards** | http://localhost:5601 | None (dev mode) |
| **Grafana** | http://localhost:3000 | admin / admin |
| **Prometheus** | http://localhost:9090 | None |
| **Analytics API** | http://localhost:8000/docs | None (dev mode) |

---

## Getting Help

- **Documentation**: Browse [Documentation Hub](../README.md)
- **Testing**: See [Testing Guide](../operations/testing-guide.md)
- **Issues**: [GitHub Issues](https://github.com/your-org/vaultize-analytics/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/vaultize-analytics/discussions)

---

## Production Deployment

**Warning**: This quick start is for development only!

For production deployment:
1. Review [Environment Setup](./environment-setup.md)
2. Read [Security Hardening Checklist](../operations/security-hardening-checklist.md)
3. Configure [Secrets Management](../operations/secrets-management.md)
4. Set up [Disaster Recovery](../operations/disaster-recovery.md)

---

**Ready to explore?** Start with the [User Guides](../user-guides/README.md)!

---

**Last Updated**: 2026-02-17
