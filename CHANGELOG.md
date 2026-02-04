# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Analytics API routers (search, aggregations, index management) - in progress
- Alerting service implementation - pending
- Operational scripts (bootstrap, health checks) - pending

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
