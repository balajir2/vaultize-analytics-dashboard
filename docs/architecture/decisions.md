# Architecture Decision Records (ADRs)

> **Project**: Vaultize Analytics Platform
> **Purpose**: Documents the key architectural decisions made for the platform, including rationale, alternatives considered, and impact. Understanding these decisions helps maintain consistency and avoid revisiting settled questions.

---

## Decision Summary

| # | Decision | Choice | Trade-off | Status |
|---|---|---|---|---|
| 1 | Search engine | OpenSearch over Elasticsearch | Smaller community | ✅ Final |
| 2 | Deployment | Docker Compose first, K8s later | Less scalable initially | ✅ Final |
| 3 | Language | Python 3.11+ over Go/Java | Slower runtime | ✅ Final |
| 4 | Log collector | Fluent Bit over Logstash | Less powerful parsing | ✅ Final |
| 5 | Config approach | YAML/JSON-driven over code | More config files | ✅ Final |
| 6 | Data primary type | Logs first, metrics complementary | Separate metrics storage | ✅ Final |
| 7 | Alerts transport | Webhooks | Requires receiver endpoint | ✅ Final |
| 8 | Deployment model | On-prem only, no cloud dependencies | No managed service convenience | ✅ Final |
| 9 | Alert logic | Threshold-based (no ML in v1) | Less intelligent | ✅ Final |
| 10 | Repo structure | Mono-repo | Larger repo size | ✅ Final |

---

## ADR-001: OpenSearch Over Elasticsearch

**Decision**: Use OpenSearch as the core search and analytics engine.

**Rationale**:
- **Open Source License**: Apache 2.0 vs Elastic License 2.0 (ELv2)
- **Community-Driven**: Managed by AWS but open governance
- **API Compatibility**: Elasticsearch-compatible APIs (easy migration)
- **No Vendor Lock-in**: True open source allows self-hosting without restrictions
- **Active Development**: Regular releases, security patches, new features

**Alternatives Considered**:
- Elasticsearch (rejected: licensing concerns post-7.10)
- Solr (rejected: less suitable for log analytics use case)
- ClickHouse (rejected: optimized for metrics, not full-text search)

**Impact**: All code, configurations, and documentation assume OpenSearch APIs.

---

## ADR-002: Docker Compose First, Kubernetes Later

**Decision**: Use Docker Compose for v1 deployment, defer Kubernetes to post-MVP.

**Rationale**:
- **Simplicity**: Easier to develop, test, and deploy locally
- **On-Prem Friendly**: No cluster management overhead
- **Faster Iteration**: Simple YAML, no complex orchestration
- **Sufficient for Small-Medium Scale**: Handles up to ~100K logs/sec
- **Lower Barrier to Entry**: Most engineers familiar with Docker

**Alternatives Considered**:
- Kubernetes from day 1 (rejected: too complex for initial development)
- Docker Swarm (rejected: less popular, unclear future)
- Nomad (rejected: smaller ecosystem)

**Impact**: Infrastructure code starts with docker-compose.yml; Kubernetes manifests created later.

---

## ADR-003: Python for Services, Not Java/Go

**Decision**: Use Python 3.11+ for analytics API, alerting, and operational services.

**Rationale**:
- **Excellent OpenSearch Client**: Official opensearch-py library
- **Fast Development**: Less boilerplate than Java/Go
- **Rich Ecosystem**: Libraries for data processing, scheduling, HTTP
- **Team Expertise**: Broader accessibility
- **FastAPI Framework**: Modern, async, auto-generated API docs

**Alternatives Considered**:
- Go (rejected: more boilerplate, fewer data processing libraries)
- Java (rejected: heavy runtime, slower development)
- Node.js (rejected: less suitable for data-heavy processing)

**Impact**: All service code in Python; expect async/await patterns.

---

## ADR-004: Fluent Bit Over Logstash

**Decision**: Use Fluent Bit as the primary log collector.

**Rationale**:
- **Lightweight**: ~450KB binary, minimal memory footprint (~1MB)
- **High Performance**: Written in C, handles high throughput
- **Cloud Native**: CNCF project, designed for containers
- **Lower Resource Cost**: Important for on-prem deployments
- **Sufficient for Most Cases**: Built-in parsers handle 90% of use cases

**Alternatives Considered**:
- Logstash (optional for complex parsing; JVM overhead too high for default)
- Fluentd (rejected: Ruby-based, higher memory usage)
- Filebeat (rejected: Elastic stack, requires Elasticsearch)

**Impact**: Default ingestion pipeline uses Fluent Bit; Logstash available for edge cases.

---

## ADR-005: Configuration-Driven Over Code-Driven

**Decision**: Prefer YAML/JSON configuration files over hardcoded logic.

**Rationale**:
- **No Redeployment**: Changes don't require code recompilation
- **Version Control**: Config changes tracked in Git
- **Environment Separation**: Different configs for dev/staging/prod
- **User-Friendly**: Operators can modify without coding knowledge
- **Testable**: Config validation separate from application logic

**Examples**:
- Index templates: YAML files, not Python code
- Alert rules: JSON definitions, not hardcoded thresholds
- ILM policies: YAML configuration
- Fluent Bit pipelines: Configuration files

**Impact**: Expect configs/ directory to be extensive; services load config at runtime.

---

## ADR-006: Logs First, Metrics Complementary

**Decision**: Logs are the primary data type; metrics (Prometheus) are optional and complementary.

**Rationale**:
- **Root Cause Analysis**: Logs provide event-level detail
- **Forensics**: Can reconstruct what happened from logs
- **Flexibility**: Logs can be aggregated into metrics, but not vice versa
- **Platform Focus**: Competing with Splunk (log analytics), not Datadog (APM)
- **Metrics for Trends**: Prometheus handles aggregated trends, not event details

**Mental Model**:
- **Logs**: "Why did request X fail at timestamp Y?" (forensics)
- **Metrics**: "What's the error rate trend over the last hour?" (monitoring)

**Impact**: OpenSearch is primary data store; Prometheus is optional for system health.

---

## ADR-007: Webhook-Based Alerting

**Decision**: Use webhooks as the primary notification transport for alerts.

**Rationale**:
- **Universal Protocol**: Works with Slack, Teams, PagerDuty, custom endpoints
- **Decoupled**: Alert engine doesn't need to know notification specifics
- **Extensible**: Easy to add new integrations via webhook receivers
- **Standard**: De facto standard for event notifications

**Alternatives Considered**:
- Email only (rejected: too limited, delivery delays)
- Hardcoded integrations (rejected: not extensible)
- Message queue (rejected: too complex for v1)

**Impact**: Alert service POSTs JSON to configured webhook URLs.

---

## ADR-008: On-Prem Only, No Cloud Dependencies

**Decision**: System must be fully self-hosted with no managed cloud services.

**Rationale**:
- **Target Market**: Enterprises with on-prem requirements (compliance, data sovereignty)
- **Cost Predictability**: No cloud billing surprises
- **Data Control**: Logs stay within customer infrastructure
- **Vendor Independence**: Not tied to AWS/GCP/Azure availability or pricing

**Hard Constraints**:
- ❌ No AWS OpenSearch Service
- ❌ No CloudWatch, Datadog, or SaaS monitoring
- ❌ No managed Kafka, RDS, etc.
- ✅ Docker-based, self-contained deployment

**Impact**: All documentation and code assumes self-hosted deployment.

---

## ADR-009: Threshold-Based Alerting Initially

**Decision**: V1 alerting uses threshold-based rules; defer ML-based anomaly detection.

**Rationale**:
- **Simplicity**: Easier to implement and understand
- **Predictability**: Users know exactly when alerts fire
- **Sufficient for Most Cases**: 80% of alerts are threshold-based
- **No Training Data Required**: Works from day 1
- **ML as Enhancement**: Can add later without breaking existing alerts

**Examples**:
- "Alert if error count > 100 in 5 minutes"
- "Alert if 95th percentile latency > 500ms"

**Impact**: Alert rules defined with simple operators (gt, lt, eq); ML features post-MVP.

---

## ADR-010: Mono-Repo Structure

**Decision**: Single repository with clear separation of concerns, not microrepo.

**Rationale**:
- **Atomic Changes**: Infrastructure + code changes in single commit
- **Easier Development**: Clone once, see everything
- **Consistent Versioning**: All components versioned together
- **Simplified CI/CD**: One pipeline for entire platform
- **Clear Structure**: Directories enforce separation

**Structure**:
```
infrastructure/  → deployment configs
ingestion/       → log collection configs
analytics/       → services (API, alerting, indexing)
configs/         → index templates, ILM, alert rules
dashboards/      → visualizations and dashboards
scripts/         → operational tooling
docs/            → documentation
tests/           → all tests
```

**Impact**: Single Git repo; directories must maintain clear boundaries.
