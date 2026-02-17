# Vaultize Analytics Platform - Documentation Hub

> **On-Premise Log Analytics and Observability Platform**
> Built with OpenSearch, FastAPI, Fluent Bit, Grafana, and Prometheus

**Last Updated**: 2026-02-17 | **Platform Version**: 1.0.0 | **Status**: Complete

---

## Architecture

```
Applications / Servers
        |
        v
  Fluent Bit (log collection)
        |
        v
   OpenSearch Cluster (search + analytics)
      |           |
      v           v
  Analytics    OpenSearch Dashboards
    API            |
      |            v
      v        Grafana (unified dashboards)
  Alerting         |
  Service          v
      |        Prometheus (system metrics)
      v
  Webhooks / Notifications
```

**Key Components**:
- **OpenSearch** - Core search and analytics engine (self-hosted, Apache 2.0)
- **Fluent Bit** - Lightweight log collector (CNCF, ~450KB binary)
- **Analytics API** - FastAPI service for search, aggregations, index management, auth
- **Alerting Service** - Threshold-based alerts with webhook notifications
- **OpenSearch Dashboards** - Log exploration and visualization
- **Grafana** - Unified dashboards across OpenSearch + Prometheus
- **Prometheus** - System health metrics (optional, complementary)

For detailed technology choices and rationale, see [Technology Stack](./architecture/tech-stack.md).
For system architecture diagrams (Mermaid), see [System Architecture Diagrams](./architecture/diagrams/system-architecture.md).

---

## Document Index

### Architecture
| Document | Description |
|----------|-------------|
| [Technology Stack](./architecture/tech-stack.md) | Component choices, versions, and rationale |
| [System Architecture Diagrams](./architecture/diagrams/system-architecture.md) | Mermaid diagrams of data flow, deployment, and component interactions |

### Deployment
| Document | Description |
|----------|-------------|
| [Quick Start Guide](./deployment/quickstart.md) | Get the platform running in minutes with Docker Compose |
| [Configuration Reference](./deployment/configuration.md) | All environment variables and configuration options |
| [Environment Setup](./deployment/environment-setup.md) | Prerequisites, system requirements, and environment preparation |

### Operations
| Document | Description |
|----------|-------------|
| [Testing Guide](./operations/testing-guide.md) | Complete manual testing walkthrough (Tests 1-8) |
| [UI Testing Guide](./operations/ui-testing-guide.md) | Browser-only testing — no CLI required |
| [Performance Tuning](./operations/performance-tuning.md) | OpenSearch and system performance optimization |
| [Resource Sizing Guide](./operations/resource-sizing-guide.md) | Hardware requirements by deployment size |
| [Security Hardening Checklist](./operations/security-hardening-checklist.md) | Production security configuration |
| [Secrets Management](./operations/secrets-management.md) | Managing credentials and sensitive configuration |
| [Disaster Recovery](./operations/disaster-recovery.md) | Backup, restore, and disaster recovery procedures |

### Integration
| Document | Description |
|----------|-------------|
| [DRM Integration Guide](./integration/DRM_INTEGRATION_GUIDE.md) | Complete guide for integrating DRM/file-security event logs |

### User Guides
| Document | Description |
|----------|-------------|
| [User Guides](./user-guides/README.md) | Search cheat sheet, common use cases, dashboard and alert best practices |

### Configuration References
| Document | Description |
|----------|-------------|
| [Index Templates](../configs/index-templates/README.md) | OpenSearch index template definitions and field mappings |
| [ILM Policies](../configs/ilm-policies/README.md) | Index Lifecycle Management policy configuration |
| [Alert Rules](../configs/alert-rules/README.md) | Alert rule definitions, thresholds, and webhook configuration |

### API Documentation

The Analytics API provides interactive documentation via Swagger UI:

| Resource | URL |
|----------|-----|
| Swagger UI | `http://localhost:8000/docs` |
| ReDoc | `http://localhost:8000/redoc` |
| OpenAPI JSON | `http://localhost:8000/openapi.json` |

**API Endpoints**:
- `GET /health` - Health check, readiness, liveness, cluster status
- `POST /api/v1/search` - Full-text log search with Lucene syntax
- `GET /api/v1/search/simple` - GET-based simple search
- `GET /api/v1/search/count` - Document count
- `POST /api/v1/aggregations` - Aggregation queries (terms, date_histogram, stats, etc.)
- `GET /api/v1/indices/` - Index listing, stats, mappings, settings, deletion
- `POST /auth/token` - JWT authentication

### Testing
| Document | Description |
|----------|-------------|
| [Test Suite Overview](../tests/README.md) | Test structure and running instructions |
| [Regression Tests](../tests/regression/REGRESSION_TESTS.md) | Regression test catalog (RT-001 through RT-011) |
| [API Test Coverage](../analytics/api/tests/COVERAGE_REPORT.md) | API unit test coverage report (89%) |

---

## Quick Reference

### Service URLs (Default)

| Service | URL | Credentials |
|---------|-----|-------------|
| OpenSearch | `https://localhost:9200` | admin / admin |
| OpenSearch Dashboards | `http://localhost:5601` | admin / admin |
| Analytics API | `http://localhost:8000` | JWT token via `/auth/token` |
| Grafana | `http://localhost:3000` | admin / admin |
| Prometheus | `http://localhost:9090` | None |

### Common Commands

```bash
# Start all services
docker compose up -d

# Start with optional services (Grafana, Prometheus)
docker compose --profile monitoring --profile grafana up -d

# Check service health
curl http://localhost:8000/health
curl -k https://localhost:9200/_cluster/health -u admin:admin

# View logs
docker compose logs -f analytics-api
docker compose logs -f opensearch

# Run API unit tests
cd analytics/api && python -m pytest tests/ -v

# Run alerting unit tests
cd analytics/alerting && python -m pytest tests/ -v

# Run regression tests
python -m pytest tests/regression/ -v

# Stop all services
docker compose down

# Stop and remove volumes (destructive)
docker compose down -v
```

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 4 cores | 8+ cores |
| RAM | 8 GB | 16+ GB |
| Disk | 50 GB | 200+ GB SSD |
| Docker | 20.10+ | Latest |
| Docker Compose | 2.0+ | Latest |
| Python | 3.11+ | 3.13+ |

---

## Project Files

| File | Description |
|------|-------------|
| [README.md](../README.md) | Project overview and getting started |
| [CLAUDE.md](../CLAUDE.md) | AI assistant instructions and architecture decisions |
| [TODO.md](../TODO.md) | Task tracking |
| [CHANGELOG.md](../CHANGELOG.md) | Change history |
| [MILESTONES.md](../MILESTONES.md) | Milestone progress |
| [SESSION_NOTES.md](./SESSION_NOTES.md) | Development session notes |
| [AUTHORS.md](../AUTHORS.md) | Contributors |
| [LICENSE.md](../LICENSE.md) | Apache 2.0 License |
