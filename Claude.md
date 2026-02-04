# `claude.md`

## Project Context

This repository contains an **on-premise analytics and observability platform** inspired by **Splunk**, built entirely using **open-source components**.

The system is intended to be:

* Self-hosted / on-prem deployable
* Production-grade
* Modular and extensible
* Focused on **log analytics first**

This is **not** a cloud-native SaaS project and **must not introduce managed cloud dependencies**.

---

## Core Goal

Build a platform that supports:

* Centralized log ingestion
* Search and analytics over logs/events
* Dashboards and visualizations
* Alerting on log-derived signals
* Optional metrics integration

The primary engine is **OpenSearch** (self-hosted).

---

## Hard Constraints (Do Not Violate)

Claude **must respect these constraints** when generating code, structure, or recommendations:

* **Deployment**: On-prem only
* **Search engine**: OpenSearch (self-hosted)
* **Visualization**: OpenSearch Dashboards (primary), Grafana (optional)
* **Log ingestion**: Fluent Bit preferred, Logstash optional
* **Metrics**: Prometheus (optional, complementary)
* **No AWS-managed services**
* **No SaaS dependencies**
* **No proprietary software**
* **No assumption of Kubernetes in v1** (Docker Compose first)

---

## Mental Model to Use

Claude should reason using this model:

* OpenSearch = **search + analytics engine**, not a vector DB
* Logs are the **primary data type**
* Metrics are **complementary**, not a replacement for logs
* Dashboards are **derived artifacts**, not the core system
* Configuration > code where possible

Avoid framing the system as:

* A BI tool
* A pure observability stack
* A vector database platform
* A cloud-native SaaS

---

## Expected Architecture (Conceptual)

```
Applications / Servers
        |
        v
  Fluent Bit / Logstash
        |
        v
   OpenSearch Cluster
        |
        v
 OpenSearch Dashboards
```

Optional additions:

* Prometheus for metrics
* Grafana for unified dashboards
* Kafka for ingestion buffering (future)

---

## Repository Design Expectations

Claude should assume a **mono-repo** with clear separation of concerns.

High-level structure should resemble:

* `infrastructure/` – deployment, Docker, configs
* `ingestion/` – log pipelines and agents
* `analytics/` – index templates, queries, alerts
* `dashboards/` – saved dashboards and visualizations
* `configs/` – shared YAML/JSON configuration
* `scripts/` – operational tooling
* `docs/` – architecture and usage documentation

Each directory must have:

* A clear responsibility
* Minimal coupling to others

---

## Coding Guidelines

When generating code:

* Prefer **Python** for scripts and services
* Prefer **YAML / JSON** for configuration
* Avoid over-engineering
* Favor readability over clever abstractions
* Assume other engineers will maintain this

Do **not** generate:

* Massive frameworks
* Overly generic abstractions
* Unnecessary microservices

---

## Testing Requirements

**CRITICAL**: Every new functionality MUST have associated regression tests.

### Test Coverage Mandate

Claude **must** adhere to these testing requirements:

1. **Unit Tests Required**
   - All Python functions/methods must have unit tests
   - Target: >80% code coverage minimum
   - Location: `<module>/tests/test_<feature>.py`
   - Framework: pytest

2. **Integration Tests Required**
   - All service integrations must have integration tests
   - Test actual connections to OpenSearch, APIs, etc.
   - Location: `tests/integration/`
   - Use test fixtures and mocks appropriately

3. **Regression Tests Required**
   - Every bug fix must include a regression test
   - Every new feature must have regression test coverage
   - Location: `tests/regression/`
   - Tests must be named clearly: `test_regression_<issue_number>_<description>.py`

4. **E2E Tests for Critical Flows**
   - Complete log ingestion → search → visualization flow
   - Alert creation → trigger → notification flow
   - Location: `tests/e2e/`

### Test Development Workflow

When adding new functionality:

1. **Write tests first** (TDD approach preferred) or immediately after implementation
2. **Run tests locally** before committing
3. **Update regression suite** in `tests/regression/` with new test cases
4. **Document test coverage** in code comments and docstrings
5. **Never commit untested code**

### Regression Test Suite Structure

```
tests/
├── regression/
│   ├── test_regression_001_opensearch_connection.py
│   ├── test_regression_002_index_creation.py
│   ├── test_regression_003_log_ingestion.py
│   └── README.md  # Documents all regression tests
├── unit/
│   ├── analytics/
│   ├── alerting/
│   └── indexing/
├── integration/
│   ├── test_opensearch_integration.py
│   ├── test_fluent_bit_integration.py
│   └── test_api_integration.py
└── e2e/
    ├── test_log_flow.py
    ├── test_alert_flow.py
    └── test_dashboard_flow.py
```

### Test Naming Conventions

- **Unit**: `test_<function_name>_<scenario>.py`
- **Integration**: `test_<service>_integration.py`
- **Regression**: `test_regression_<number>_<issue_description>.py`
- **E2E**: `test_<flow_name>_flow.py`

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Regression suite
pytest tests/regression/

# With coverage
pytest --cov=analytics --cov=ingestion --cov-report=html
```

### Test Quality Standards

- Tests must be **isolated** (no dependencies between tests)
- Tests must be **deterministic** (same input = same output)
- Tests must be **fast** (unit tests < 100ms, integration < 5s)
- Tests must be **readable** (clear arrange-act-assert structure)
- Tests must **clean up** after themselves (no side effects)

**Failure to provide tests for new functionality is considered incomplete work.**

---

## Alerting Philosophy

Alerts should be:

* Derived from OpenSearch queries
* Threshold-based initially
* Config-driven
* Transport-agnostic (webhook-first)

Avoid ML-based alerting in v1 unless explicitly requested.

---

## Metrics Philosophy (Prometheus)

Prometheus, if referenced, should be used for:

* System health
* Resource utilization
* Latency and error rates

Prometheus **must not** replace:

* Log search
* Root-cause analysis
* Event forensics

---

## Vector Search Guidance

Vector search:

* Is **optional**
* Is **not a primary design goal**
* Should be treated as a future extension point only

Claude should not redesign the system around embeddings unless explicitly asked.

---

## Output Expectations

When responding, Claude should:

* Be explicit about trade-offs
* Clearly label assumptions
* Prefer architectural clarity
* Think like a platform engineer, not a tutorial author
* Avoid marketing language

---

## Success Criteria

A senior engineer should be able to:

* Understand the system in minutes
* Run it locally with Docker Compose
* Extend it safely
* Operate it on-prem without cloud dependencies

---

## Key Architecture Decisions

This section documents critical architectural decisions made for the platform. Understanding these decisions helps maintain consistency and avoid revisiting settled questions.

### Decision 1: OpenSearch Over Elasticsearch

**Decision**: Use OpenSearch as the core search and analytics engine.

**Rationale**:
- **Open Source License**: Apache 2.0 vs Elastic License 2.0 (ELv2)
- **Community-Driven**: Managed by AWS but open governance
- **API Compatibility**: Elasticsearch-compatible APIs (easy migration)
- **No Vendor Lock-in**: True open source allows self-hosting without restrictions
- **Active Development**: Regular releases, security patches, new features

**Alternatives Considered**:
- Elasticsearch (rejected due to licensing concerns post-7.10)
- Solr (less suitable for log analytics use case)
- ClickHouse (optimized for metrics, not full-text search)

**Impact**: All code, configurations, and documentation assume OpenSearch APIs.

---

### Decision 2: Docker Compose First, Kubernetes Later

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

### Decision 3: Python for Services, Not Java/Go

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

### Decision 4: Fluent Bit Over Logstash

**Decision**: Use Fluent Bit as the primary log collector.

**Rationale**:
- **Lightweight**: ~450KB binary, minimal memory footprint (~1MB)
- **High Performance**: Written in C, handles high throughput
- **Cloud Native**: CNCF project, designed for containers
- **Lower Resource Cost**: Important for on-prem deployments
- **Sufficient for Most Cases**: Built-in parsers handle 90% of use cases

**Alternatives Considered**:
- Logstash (optional for complex parsing; JVM overhead too high for default)
- Fluentd (Ruby-based, higher memory usage)
- Filebeat (Elastic stack, requires Elasticsearch)

**Impact**: Default ingestion pipeline uses Fluent Bit; Logstash available for edge cases.

---

### Decision 5: Configuration-Driven Over Code-Driven

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

### Decision 6: Logs First, Metrics Complementary

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

### Decision 7: Webhook-Based Alerting

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

### Decision 8: On-Prem Only, No Cloud Dependencies

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

### Decision 9: Threshold-Based Alerting Initially

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

### Decision 10: Mono-Repo Structure

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

---

### Decision Summary Table

| Decision | Rationale | Trade-off | Status |
|----------|-----------|-----------|--------|
| OpenSearch over Elasticsearch | Open source licensing | Smaller community than Elasticsearch | ✅ Final |
| Docker Compose first | Simplicity, on-prem friendly | Less scalable than K8s | ✅ Final |
| Python for services | Fast development, good libraries | Slower runtime than Go | ✅ Final |
| Fluent Bit over Logstash | Lightweight, high performance | Less powerful parsing | ✅ Final |
| Configuration-driven | Flexibility, no redeployment | More config files to manage | ✅ Final |
| Logs first, metrics complementary | Forensics capability | Metrics storage separate | ✅ Final |
| Webhook-based alerting | Universal, extensible | Requires webhook receiver | ✅ Final |
| On-prem only | Data sovereignty, cost control | No managed service convenience | ✅ Final |
| Threshold alerting initially | Simple, predictable | Less intelligent than ML | ✅ Final |
| Mono-repo | Atomic changes, easy development | Larger repo size | ✅ Final |

---

## Session Continuity Protocol

**CRITICAL**: At the end of each session, Claude **must** update the following files to ensure continuity across sessions:

1. **`TODO.md`**
   - Update current tasks with latest status (pending/in-progress/completed)
   - Add new tasks discovered during the session
   - Mark completed tasks with completion date
   - Document any blockers or issues

2. **`CHANGELOG.md`**
   - Log all significant changes made during the session
   - Include file creations, modifications, deletions
   - Note configuration changes
   - Document any architectural decisions

3. **`MILESTONES.md`**
   - Update milestone progress
   - Mark completed milestones with completion date
   - Add new milestones if scope has changed
   - Update percentage completion estimates

4. **`docs/SESSION_NOTES.md`**
   - Write a brief session summary
   - Document what was accomplished
   - Note next steps
   - Record any important context or decisions
   - Include current state of the system (what's working, what's not)

**When to update**: Before the user ends the session (e.g., phrases like "let's stop for today", "closing for the day", "that's all for now", etc.)

**Purpose**: These files serve as the primary mechanism for session continuity since conversation context doesn't persist between sessions.

