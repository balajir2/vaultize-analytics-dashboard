# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] - 2026-02-21 (Prometheus Metrics Integration)

### Added
- **Prometheus Metrics for Analytics API**: `prometheus-fastapi-instrumentator` dependency; auto-exposed `/metrics` endpoint with request count, latency histograms, in-progress gauges
- **Prometheus Metrics for Alerting Service**: Same instrumentator integration with `/metrics` endpoint
- **OpenSearch Exporter Sidecar**: `opensearch-exporter` service (prometheuscommunity/elasticsearch-exporter:v1.7.0) translates OpenSearch cluster stats into Prometheus metrics
- **Fluent Bit Metrics Port**: Exposed port 2020 in docker-compose.yml for Prometheus scraping
- **Grafana Service Metrics Panels**: 4 new panels in "Service Metrics" row (API/Alerting request rate + P95 latency)
- **Grafana OpenSearch Panels**: Cluster Status, Node Count, Active Shards via exporter metrics
- **Rate Limiter /metrics Exclusion**: `/metrics` endpoint excluded from per-IP rate limiting
- **RT-019 Regression Test** (23 tests): Prometheus metrics integration validation
- **API Metrics Unit Tests** (12 new): /metrics endpoint behavior tests
- **Alerting Metrics Unit Tests** (4 new): /metrics endpoint behavior tests
- **Integration Guide**: `docs/integration/log-integration-guide.md` — connecting log-generating systems to the platform

### Fixed
- RT-012 regression tests: corrected path references from `/var/log/app-logs` to `/app/logs`

### Changed
- Prometheus scrape config: OpenSearch target now uses opensearch-exporter sidecar
- Grafana dashboard: replaced node UP/DOWN panels with exporter-based cluster metrics
- Test counts: 469 total (103 API + 105 Alerting + 261 Regression), up from 437
- Docker Compose: 10 services total (added opensearch-exporter under metrics profile)
- Documentation updates across all files to reflect new services and test counts

---

## [1.0.0] - 2026-02-17 (Documentation Rationalization + Bug Fixes)

### Fixed
- Analytics API: Added `GET /search/count` endpoint (was returning 404)
- Analytics API: Added `GET /health/cluster` endpoint (was returning 404)
- Analytics API: Health check returns "degraded" instead of "unhealthy" when OpenSearch is down
- Analytics API: Readiness probe returns JSON response instead of HTTPException
- Test fix: URL-encoded `?` as `%3F` in index deletion wildcard test
- Fixed 11 dead links across 8 documentation files (quickstart, configuration, environment-setup, DRM guide, etc.)
- Updated stale dates in 7 documentation files (from 2026-02-04 to 2026-02-17)

### Added
- docs/operations/ui-testing-guide.md — 100% browser-based manual testing guide (zero CLI commands)
  - Covers OpenSearch Dashboards, Analytics API Swagger UI, Alerting Service Swagger UI, Grafana, Prometheus
  - Includes testing checklist and browser-only troubleshooting

### Changed
- Root README.md updated from v0.3.0 Alpha (65%) to v1.0.0 Complete (100%)
- MILESTONES.md detail sections updated (M0, M3-M6) with final test counts and checked-off items
- Documentation rationalized: removed 6 stub/duplicate files, consolidated into single hub
- docs/README.md rewritten as single documentation entry point with zero dead links
- docs/user-guides/README.md cleaned up (removed 7 dead links to never-created sub-docs)
- analytics/api/tests/COVERAGE_REPORT.md updated (98 tests passing, 0 failures)
- AUTHORS.md updated (Claude model name, session dates)

### Removed
- docs/architecture/README.md (stub with 6 dead links)
- docs/deployment/README.md (stub with 4 dead links)
- docs/operations/README.md (stub with 5 dead links)
- docs/DOCUMENTATION_MAP.md (listed ~30 non-existent docs)
- docs/api/README.md (all 7 sub-docs never created)
- docs/operations/full-platform-test-guide.md (duplicate of testing-guide.md)

---

## [0.4.0] - 2026-02-17 (M7: Production Hardening + M6: Testing Completion)

### Added

**File-Based Log Ingestion**:
- Fluent Bit tail inputs for `*.log` (JSON) and `*.txt` (structured) files
- Sample log directory with README and sample data
- Log file generator script (`scripts/data/generate_sample_log_files.py`)

**TLS Certificate Infrastructure**:
- Certificate generation scripts (bash + Python)
- OpenSearch security configs: internal_users, roles, roles_mapping, config

**OpenSearch Security Plugin**:
- Docker Compose overlay (`docker-compose.security.yml`) for secure mode
- Secure configs for OpenSearch, Dashboards, and Fluent Bit
- Start and initialize scripts for secure mode

**JWT Authentication Middleware**:
- Analytics API: auth middleware, rate limiter, user models, auth router
- Alerting Service: JWT token validation middleware
- Auth opt-in via `AUTH_ENABLED=false` (default)

**CORS Hardening & Grafana Setup**:
- Restrictive CORS in production/staging
- Grafana datasource provisioning (OpenSearch + Prometheus)
- Platform health Grafana dashboard (14 panels)
- Secrets management documentation

**Operations Scripts**:
- backup_opensearch.py, restore_opensearch.py, health_check.py, bootstrap.sh
- Disaster recovery guide

**E2E, Integration, and Performance Tests**:
- E2E: log ingestion flow, alert flow, dashboard flow
- Integration: Fluent Bit, ingestion pipeline, alerting
- Performance: bulk indexing, query latency, API throughput

**Documentation**:
- Architecture diagrams (Mermaid), security checklist, resource sizing, performance tuning

**Regression Tests** (RT-012 through RT-018, 174 new tests):
- RT-012 (18), RT-013 (28), RT-014 (22), RT-015 (25), RT-016 (30), RT-017 (29), RT-018 (22)

### Changed
- `analytics/api/app/config.py` — Auth, JWT, and rate limit settings
- `analytics/api/app/main.py` — CORS hardening, auth router, rate limit middleware
- `analytics/alerting/app/config.py` — Auth settings
- `docker-compose.yml` — Sample-logs volume mount
- `ingestion/configs/fluent-bit/fluent-bit.conf` — Tail inputs and record modifier
- `.gitignore` — Cert patterns, sample log exception

---

## [0.3.0] - 2026-02-10 (M5: Alerting System)

### Added

**Alerting Service** (complete implementation):
- Python alerting service with FastAPI management API (port 8001)
- APScheduler-based periodic alert checks with configurable intervals
- OpenSearch query executor supporting count and aggregation queries
- Condition evaluator with 5 operators: gt, gte, lt, lte, eq
- State machine: OK -> FIRING -> RESOLVED -> OK with throttle enforcement
- Webhook notifier with async HTTP (httpx), retry with exponential backoff
- Template renderer for webhook bodies ({{alert.variable}} substitution)
- Environment variable substitution in JSON rule configs (${ENV_VAR} pattern)
- Alert state persistence in `.alerts-state` OpenSearch index
- Alert history tracking in `.alerts-history` OpenSearch index
- Management API endpoints:
  - `GET /health/` - overall health with OpenSearch and scheduler status
  - `GET /health/liveness` - Kubernetes liveness probe
  - `GET /health/readiness` - Kubernetes readiness probe
  - `GET /api/v1/alerts/rules` - list all rules with current state
  - `GET /api/v1/alerts/rules/{name}/status` - detailed rule status
  - `POST /api/v1/alerts/rules/{name}/trigger` - manual trigger
  - `GET /api/v1/alerts/history` - query alert history
  - `POST /api/v1/alerts/rules/reload` - force reload rules from disk
- Dockerfile with multi-stage build, non-root user, health check
- Docker Compose integration with port mapping, healthcheck, alert-rules volume

**Testing**:
- 94 unit tests for alerting service (81% coverage, exceeds >80% requirement)
- Test files: conftest.py, test_rule_loader.py, test_query_executor.py, test_condition_evaluator.py, test_state_manager.py, test_webhook_notifier.py, test_template_renderer.py, test_health_router.py, test_alerts_router.py
- RT-010: Alert rule config validation regression test (9 tests)
- RT-011: Alert state machine transitions regression test (14 tests)
- Full regression suite: 64 tests passing (up from 41)

**Documentation**:
- Updated testing guide (`docs/operations/testing-guide.md`) covering entire platform (Tests 1-8)
- Updated REGRESSION_TESTS.md with RT-010 and RT-011 entries

### Changed
- Docker Compose alerting-service: added port mapping (8001), healthcheck, ALERT_RULES_DIR env var
- Docker Compose alerting-service: removed conflicting `./analytics/alerting:/app:ro` volume mount
- Updated requirements to use compatible version ranges (>= instead of ==) for Python 3.13 support

---

## [0.2.1] - 2026-02-04 (Deployment Fixes)

### Fixed
- **OpenSearch Configuration** (Critical):
  - Removed index-level settings from opensearch.yml (caused "node settings must not contain any index level settings" error)
  - Moved index settings to index templates where they belong
  - Increased HTTP header size limit to 16kb (fixed "HTTP header is larger than 8192 bytes" error)

- **OpenSearch Dashboards Configuration** (Critical):
  - Fixed server.basePath empty string causing "must start with a slash" validation error
  - Changed server.cors.enabled to server.cors (boolean expected, not object)
  - Removed unsupported config keys: opensearch_security.*, telemetry.* (not supported in version 2.11.1)

- **Fluent Bit Configuration**:
  - Disabled storage buffering (storage path permissions issue)
  - Disabled tail inputs for Docker logs and syslog (pending proper volume mounts)
  - Removed ${TIMESTAMP} variable reference causing warnings

- **Docker Compose**:
  - Removed obsolete version field
  - Made all ports configurable via environment variables (OpenSearch, Dashboards, Prometheus, Grafana, Fluent Bit, Analytics API)

### Changed
- Grafana now runs on port 3100 (configurable via GRAFANA_PORT environment variable)
- All service ports now use environment variables with sensible defaults

### Added
- **Regression Tests** (3 new tests):
  - RT-001: OpenSearch config validation (verifies no index-level settings in node config)
  - RT-002: OpenSearch Dashboards config validation (verifies all config keys are valid)
  - RT-003: Docker Compose port configuration (verifies no hardcoded ports)
- Test coverage for all deployment configuration issues

### Notes
- Platform successfully deployed and tested on Windows with Docker Desktop
- All services running and healthy (OpenSearch green cluster status)
- Deployment-ready for development and staging environments

---

## [0.2.0] - 2026-02-04

### Added

**Infrastructure & Deployment**:
- Complete Docker Compose configuration with 3-node OpenSearch cluster
- OpenSearch configuration (opensearch.yml) with performance tuning
- OpenSearch Dashboards configuration (opensearch_dashboards.yml)
- Fluent Bit configuration with multiple log parsers
- Prometheus configuration for metrics collection
- Environment configuration system (.env.example, .env.staging.example, .env.production.example)
- Comprehensive .gitignore for all environments

**Configuration Management**:
- Index templates (logs-template.json) with optimized mappings
- ILM lifecycle policies (logs-lifecycle-policy.json) - Hot/Warm/Cold/Delete
- Alert rule examples (high-error-rate.json, slow-api-response.json)
- Environment-specific configuration templates for dev/staging/production

**Documentation**:
- Complete documentation structure (architecture/, deployment/, operations/, api/, user-guides/)
- Technology stack documentation with detailed comparison tables (tech-stack.md)
- Architecture decisions document (10 key decisions documented in Claude.md)
- Deployment guides (quickstart.md, configuration.md, environment-setup.md)
- Documentation organization map (DOCUMENTATION_MAP.md)
- Comprehensive README files for all major sections

**Testing Framework**:
- Testing requirements added to Claude.md (regression tests mandatory)
- Test directory structure (unit/, integration/, regression/, e2e/)
- Pytest configuration (conftest.py) with shared fixtures
- Regression test registry (REGRESSION_TESTS.md)
- Test documentation (tests/README.md)

**Legal & Attribution**:
- LICENSE.md (Apache 2.0) with complete license text and distribution constraints
- AUTHORS.md with proper attribution to Balaji Rajan and Claude (Anthropic)
- Copyright headers added to all configuration files

**Analytics API (Partial - Foundation)**:
- Project structure for Analytics API service
- Dockerfile and .dockerignore for containerization
- requirements.txt with all Python dependencies
- Configuration module (app/config.py) with environment variable loading
- OpenSearch client module (app/opensearch_client.py) with connection pooling
- Main FastAPI application (app/main.py) with CORS and error handling

### Changed
- Updated Claude.md with:
  - Session continuity protocol
  - Key architecture decisions (10 decisions documented)
  - Testing requirements (regression tests mandatory)
- Enhanced .env.example with URL configuration for all environments

### Security
- Added security warnings in production environment templates
- Documented secrets management best practices
- Included deployment security checklist in .env.production.example

### Notes
- Infrastructure layer is ~90% complete and deployment-ready
- Analytics API is ~40% complete (foundation built, routers pending)
- Platform can be deployed with `docker compose up -d`
- All URLs are configurable via environment variables (no hardcoded localhost)

---

## [0.1.0] - 2026-02-04 (Morning)

### Added
- Project directory structure:
  - `analytics/` - API, alerting, and indexing services
  - `configs/` - Index templates, ILM policies, alert rules, schemas
  - `dashboards/` - OpenSearch Dashboards and Grafana configurations
  - `docs/` - Architecture, deployment, operations, and user guides
  - `infrastructure/` - Docker and Kubernetes deployment configs
  - `ingestion/` - Fluent Bit, Logstash, and Prometheus configurations
  - `scripts/` - Operational tooling (dev, ops, data, utils)
  - `tests/` - E2E, integration, performance, and regression tests
  - `tools/` - CLI and monitoring utilities
- Initial project documentation:
  - `Claude.md` - Agent instructions and project context
  - `Claude Prompt.txt` - Project initialization requirements
  - Session continuity files (TODO.md, CHANGELOG.md, MILESTONES.md, SESSION_NOTES.md)

### Notes
- Initial scaffold created
- Starting infrastructure layer development

---

## Template for Future Entries

```markdown
## [Version] - YYYY-MM-DD

### Added
- New features or files

### Changed
- Changes to existing functionality

### Deprecated
- Features that will be removed in future versions

### Removed
- Features or files that were removed

### Fixed
- Bug fixes

### Security
- Security-related changes
```
