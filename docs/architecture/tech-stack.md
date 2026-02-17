# Technology Stack

> Comprehensive overview of all technologies used in the Vaultize Analytics Platform

**Last Updated**: 2026-02-17

---

## Overview

This document provides a complete reference of all technologies, tools, and frameworks used in the platform, organized by architectural layer.

---

## Core Stack Summary

| Layer | Technology | Version | Purpose | Status |
|-------|------------|---------|---------|--------|
| **Search & Analytics** | OpenSearch | 2.x | Core search engine, log storage, and analytics | Required |
| **Visualization** | OpenSearch Dashboards | 2.x | Primary UI for search, dashboards, and visualizations | Required |
| **Log Ingestion** | Fluent Bit | 2.x | Lightweight log collection and forwarding | Required |
| **Metrics** | Prometheus | 2.x | System and application metrics collection | Optional |
| **Unified Dashboards** | Grafana | 10.x | Combined logs + metrics visualization | Optional |
| **API Services** | Python 3.11+ | 3.11+ | Analytics API and alerting services | Required |
| **API Framework** | FastAPI | 0.100+ | RESTful API framework | Required |
| **Containerization** | Docker | 20.10+ | Container runtime | Required |
| **Orchestration** | Docker Compose | 2.0+ | Multi-container orchestration (v1) | Required |
| **Configuration** | YAML/JSON | - | Infrastructure as code | Required |

---

## Detailed Technology Breakdown

### 1. Data Storage & Search

| Technology | Purpose | Why This Choice | Alternatives Considered |
|------------|---------|-----------------|------------------------|
| **OpenSearch 2.x** | - Full-text search engine<br>- Log storage and indexing<br>- Analytics and aggregations<br>- Time-series data management | - Open source (Apache 2.0)<br>- Elasticsearch-compatible API<br>- Built-in security<br>- Active community<br>- No licensing concerns | - Elasticsearch (licensing issues)<br>- Solr (less suitable for logs)<br>- ClickHouse (metrics-focused) |
| **OpenSearch Cluster** | - Distributed architecture<br>- High availability<br>- Horizontal scaling | - Production-grade reliability<br>- Data redundancy<br>- Fault tolerance | - Single-node setup (dev only) |

**Key Features Used**:
- Inverted index for full-text search
- Document-oriented storage (JSON)
- Index lifecycle management (ILM)
- Snapshot and restore
- Cross-cluster replication (future)

---

### 2. Visualization & UI

| Technology | Purpose | Why This Choice | Alternatives Considered |
|------------|---------|-----------------|------------------------|
| **OpenSearch Dashboards 2.x** | - Web UI for OpenSearch<br>- Interactive dashboards<br>- Visualization builder<br>- Discover interface (search) | - Native OpenSearch integration<br>- Feature-complete UI<br>- Open source<br>- Familiar interface (Kibana-like) | - Kibana (Elasticsearch only)<br>- Custom React app (too much effort) |
| **Grafana 10.x** | - Unified logs + metrics dashboards<br>- Prometheus visualization<br>- Multi-datasource support | - Industry standard for metrics<br>- Beautiful visualizations<br>- OpenSearch plugin available<br>- Optional enhancement | - Built-in OpenSearch Dashboards only |

**Key Features Used**:
- Dashboard builder
- Saved searches
- Visualizations (time series, pie, bar, table, etc.)
- Alert integration (future)
- Reporting (future)

---

### 3. Log Ingestion & Collection

| Technology | Purpose | Why This Choice | Alternatives Considered |
|------------|---------|-----------------|------------------------|
| **Fluent Bit 2.x** | - Log collection from sources<br>- Log parsing and enrichment<br>- Buffering and retry logic<br>- Forward to OpenSearch | - Lightweight (low memory footprint)<br>- High performance<br>- Rich plugin ecosystem<br>- Cloud Native Computing Foundation project | - Fluentd (heavier, Ruby-based)<br>- Logstash (JVM, more resources)<br>- Filebeat (Elastic stack only) |
| **Logstash 8.x** | - Complex log parsing<br>- Data transformation<br>- Enrichment with external data | - Powerful parsing (grok patterns)<br>- Rich filter plugins<br>- Optional for complex use cases | - Use Fluent Bit exclusively |

**Key Features Used**:
- Tail input (file watching)
- Syslog input
- Docker/container logs input
- JSON parser
- Regex parser
- OpenSearch output
- Buffering and retry

---

### 4. Metrics Collection (Optional)

| Technology | Purpose | Why This Choice | Alternatives Considered |
|------------|---------|-----------------|------------------------|
| **Prometheus 2.x** | - Metrics scraping<br>- Time-series metrics storage<br>- Alerting on metrics<br>- Service discovery | - Industry standard for metrics<br>- Pull-based model<br>- Powerful query language (PromQL)<br>- Integrates with Grafana | - InfluxDB (different use case)<br>- Graphite (older tech)<br>- OpenSearch for metrics (not optimal) |
| **Node Exporter** | - Host-level metrics<br>- CPU, memory, disk, network | - Standard Prometheus exporter<br>- Comprehensive system metrics | - cAdvisor (container-only) |
| **Prometheus Exporters** | - Application metrics<br>- OpenSearch metrics<br>- Custom metrics | - Standardized exposition format<br>- Wide ecosystem | - Custom metrics endpoints |

**Key Features Used**:
- Service discovery
- Multi-target scraping
- PromQL queries
- Alertmanager integration (future)
- Long-term storage (future)

---

### 5. API & Services Layer

| Technology | Purpose | Why This Choice | Alternatives Considered |
|------------|---------|-----------------|------------------------|
| **Python 3.11+** | - Analytics API service<br>- Alerting service<br>- Index management<br>- Operational scripts | - Excellent OpenSearch client library<br>- Fast development<br>- Rich ecosystem<br>- Team expertise | - Go (more boilerplate)<br>- Node.js (less suitable for data processing)<br>- Java (too heavy) |
| **FastAPI** | - RESTful API framework<br>- Async request handling<br>- Auto-generated OpenAPI docs<br>- High performance | - Modern async framework<br>- Automatic validation (Pydantic)<br>- Built-in API docs (Swagger)<br>- Type hints support<br>- High performance (async) | - Flask (no async, manual docs)<br>- Django (too heavy for APIs)<br>- Express.js (different language) |
| **Pydantic** | - Request/response validation<br>- Data modeling<br>- Type safety | - Built into FastAPI<br>- Runtime validation<br>- Clear error messages | - Marshmallow (older)<br>- Manual validation |
| **OpenSearch Python Client** | - OpenSearch SDK<br>- Query building<br>- Index management | - Official client library<br>- Full feature support<br>- Active maintenance | - Direct HTTP requests (too low-level)<br>- Elasticsearch client (incompatible) |

**Key Features Used**:
- Async/await for I/O operations
- Dependency injection
- Background tasks
- WebSocket support (future)
- API versioning

---

### 6. Alerting & Notifications

| Technology | Purpose | Why This Choice | Alternatives Considered |
|------------|---------|-----------------|------------------------|
| **Custom Python Service** | - Alert rule evaluation<br>- Scheduled query execution<br>- Threshold checking<br>- Notification dispatch | - Full control over logic<br>- Custom requirements<br>- Tightly integrated with platform | - OpenSearch Alerting Plugin (less flexible)<br>- Prometheus Alertmanager (metrics-only)<br>- Third-party SaaS (violates on-prem requirement) |
| **Webhooks** | - Generic notification transport<br>- Integration with external systems | - Universal protocol<br>- Works with Slack, Teams, PagerDuty, etc.<br>- Easy to implement | - Email only (limited)<br>- Custom integrations per service |
| **APScheduler** | - Job scheduling<br>- Periodic alert evaluation<br>- Cron-like scheduling | - Pure Python solution<br>- No external dependencies<br>- Flexible scheduling | - Celery (requires message broker)<br>- Cron (external to service) |

**Key Features Used**:
- Interval-based scheduling
- Cron-style scheduling
- Job persistence (future)
- Distributed locking (future)

---

### 7. Deployment & Infrastructure

| Technology | Purpose | Why This Choice | Alternatives Considered |
|------------|---------|-----------------|------------------------|
| **Docker** | - Container runtime<br>- Isolation<br>- Reproducible environments | - Industry standard<br>- Portable<br>- Easy development setup<br>- Production-ready | - Podman (Docker more common)<br>- LXC (lower-level) |
| **Docker Compose** | - Multi-container orchestration<br>- Local development<br>- On-prem deployment (v1) | - Simple YAML definition<br>- No cluster required<br>- Easy to understand<br>- Good for small-medium deployments | - Kubernetes (overkill for v1)<br>- Docker Swarm (less popular) |
| **Kubernetes** | - Container orchestration<br>- Auto-scaling<br>- High availability (future) | - Production-grade orchestration<br>- Auto-healing<br>- Horizontal scaling<br>- Industry standard | - Only when scale requires it |
| **YAML/JSON** | - Configuration files<br>- Infrastructure as code<br>- Declarative setup | - Human-readable<br>- Version controllable<br>- Standard formats | - TOML (less common)<br>- Hardcoded config (anti-pattern) |

**Key Features Used**:
- Docker networks (service discovery)
- Named volumes (data persistence)
- Health checks
- Resource limits
- Environment variables

---

### 8. Development & Testing

| Technology | Purpose | Why This Choice | Alternatives Considered |
|------------|---------|-----------------|------------------------|
| **pytest** | - Unit testing<br>- Integration testing<br>- Test fixtures | - De facto Python testing standard<br>- Powerful fixtures<br>- Great plugins | - unittest (less features)<br>- nose2 (less popular) |
| **pytest-asyncio** | - Async test support<br>- FastAPI testing | - Native async/await support<br>- Works with FastAPI | - Manual event loop management |
| **httpx** | - Async HTTP client<br>- API testing | - Async support<br>- Requests-like API | - aiohttp (different API)<br>- requests (sync only) |
| **Black** | - Code formatting<br>- Style consistency | - Opinionated (no config needed)<br>- Standard in Python community | - autopep8 (less opinionated)<br>- YAPF (more config) |
| **pylint** | - Code linting<br>- Static analysis | - Comprehensive checks<br>- Catches bugs early | - flake8 (less comprehensive) |
| **mypy** | - Type checking<br>- Static type analysis | - Catches type errors<br>- Works with type hints | - pyright (newer) |

**Key Features Used**:
- Fixture-based testing
- Parametrized tests
- Coverage reporting
- Mock/patch functionality

---

### 9. Security & Authentication

| Technology | Purpose | Why This Choice | Alternatives Considered |
|------------|---------|-----------------|------------------------|
| **OpenSearch Security Plugin** | - Authentication<br>- Authorization (RBAC)<br>- TLS/SSL<br>- Audit logging | - Built-in to OpenSearch<br>- Production-ready<br>- Fine-grained permissions | - External auth proxy (more complex) |
| **JWT (JSON Web Tokens)** | - API authentication<br>- Stateless auth<br>- Token-based access | - Standard protocol<br>- Scalable<br>- Works with microservices | - Session-based (stateful)<br>- API keys only (less secure) |
| **Python-Jose** | - JWT creation and validation<br>- Token signing | - Lightweight<br>- Standards-compliant | - PyJWT (similar) |
| **Passlib** | - Password hashing<br>- Bcrypt support | - Industry-standard hashing<br>- Configurable rounds | - Built-in hashlib (weaker) |

**Key Features Used**:
- TLS/SSL encryption
- Role-based access control
- API key management
- Audit logging

---

### 10. Monitoring & Observability

| Technology | Purpose | Why This Choice | Alternatives Considered |
|------------|---------|-----------------|------------------------|
| **OpenSearch (Self-monitoring)** | - Platform logs ingestion<br>- Meta-monitoring | - Dog-fooding<br>- Unified platform | - Separate logging system |
| **Prometheus** | - Platform metrics<br>- Service health<br>- Resource utilization | - Standard for metrics<br>- Grafana integration | - CloudWatch (cloud only)<br>- Datadog (SaaS) |
| **Grafana** | - Monitoring dashboards<br>- Alerting (future) | - Beautiful dashboards<br>- Multi-source support | - OpenSearch Dashboards only |

**Key Features Used**:
- Health check endpoints
- Metrics exposition
- Log aggregation
- Dashboard templates

---

## Technology Decision Criteria

When selecting technologies, we evaluated based on:

1. **Open Source**: Apache 2.0 or similar permissive license
2. **On-Premise Ready**: No cloud dependencies, self-hostable
3. **Production-Grade**: Battle-tested, widely adopted
4. **Community Support**: Active development, good documentation
5. **Performance**: Suitable for high-volume log analytics
6. **Extensibility**: Pluggable, customizable
7. **Team Expertise**: Reasonable learning curve

---

## Version Requirements

### Minimum Versions

| Component | Minimum Version | Recommended Version |
|-----------|----------------|---------------------|
| Docker | 20.10 | 24.0+ |
| Docker Compose | 2.0 | 2.20+ |
| Python | 3.11 | 3.11+ |
| OpenSearch | 2.0 | 2.11+ |
| OpenSearch Dashboards | 2.0 | 2.11+ |
| Fluent Bit | 2.0 | 2.2+ |
| Prometheus | 2.40 | 2.48+ |
| Grafana | 10.0 | 10.2+ |

### Compatibility Matrix

| OpenSearch | OpenSearch Dashboards | Python Client |
|------------|----------------------|---------------|
| 2.11.x | 2.11.x | 2.4.x |
| 2.10.x | 2.10.x | 2.3.x |
| 2.9.x | 2.9.x | 2.3.x |

---

## Third-Party Libraries

### Python Dependencies

```python
# Core API
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0

# OpenSearch
opensearch-py==2.4.0

# Async support
httpx==0.25.0
aiofiles==23.2.1

# Scheduling (Alerting)
apscheduler==3.10.4

# Auth & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Configuration
pyyaml==6.0.1
python-dotenv==1.0.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.0  # for testing

# Code Quality
black==23.11.0
pylint==3.0.2
mypy==1.7.0
```

---

## License Summary

| Technology | License | Commercial Use | Modifications Allowed |
|------------|---------|----------------|----------------------|
| OpenSearch | Apache 2.0 | ✅ Yes | ✅ Yes |
| OpenSearch Dashboards | Apache 2.0 | ✅ Yes | ✅ Yes |
| Fluent Bit | Apache 2.0 | ✅ Yes | ✅ Yes |
| Prometheus | Apache 2.0 | ✅ Yes | ✅ Yes |
| Grafana | AGPL 3.0 | ⚠️ Yes (with conditions) | ✅ Yes |
| Python | PSF | ✅ Yes | ✅ Yes |
| FastAPI | MIT | ✅ Yes | ✅ Yes |
| Docker | Apache 2.0 | ✅ Yes | ✅ Yes |

**Note**: Grafana uses AGPL 3.0. For production use without open-sourcing modifications, consider the commercial license or use OpenSearch Dashboards exclusively.

---

## Technology Roadmap

### Planned Additions

| Technology | Purpose | Timeline | Priority |
|------------|---------|----------|----------|
| **Redis** | Alert state caching, rate limiting | Q2 2026 | Medium |
| **PostgreSQL** | Alert history, user management | Q2 2026 | Medium |
| **Kafka** | Log ingestion buffering, high throughput | Q3 2026 | Low |
| **OpenSearch ML** | Anomaly detection, forecasting | Q4 2026 | Low |
| **Keycloak** | SSO, advanced auth | Q3 2026 | Medium |

### Under Consideration

- **Traefik**: Reverse proxy and load balancing
- **Vault**: Secrets management
- **Consul**: Service discovery (if moving to microservices)
- **Telegraf**: Additional metrics collection

---

## Deprecated / Not Used

| Technology | Reason Not Used |
|------------|-----------------|
| **Elasticsearch** | Licensing concerns (Elastic License vs Apache 2.0) |
| **Kibana** | Requires Elasticsearch, not compatible with OpenSearch |
| **Logstash** | Too heavy for v1, Fluent Bit preferred |
| **Beats** | Elastic stack only |
| **Splunk** | Proprietary, expensive, violates open-source requirement |
| **AWS OpenSearch Service** | Managed service, violates on-prem requirement |
| **CloudWatch** | AWS-specific, violates on-prem requirement |
| **Datadog** | SaaS, violates on-prem requirement |

---

## Technology Maintenance Plan

### Update Schedule
- **Security patches**: Applied within 7 days
- **Minor updates**: Quarterly
- **Major updates**: Annually (with testing period)

### End of Life Monitoring
- Track EOL dates for all components
- Plan migrations 6 months before EOL
- Test upgrades in staging environment

---

**Next Steps**:
1. Validate version compatibility
2. Set up dependency scanning
3. Create upgrade procedures
4. Document migration paths

---

**Last Updated**: 2026-02-17
