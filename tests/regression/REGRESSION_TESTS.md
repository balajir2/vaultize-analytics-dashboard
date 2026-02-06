# Regression Test Registry

> Complete registry of all regression tests to prevent bug reoccurrence

**Last Updated**: 2026-02-06

---

## Overview

This document maintains a registry of all regression tests. Each regression test corresponds to a specific bug that was fixed, ensuring it never reoccurs.

**Naming Convention**: `test_regression_<number>_<short_description>.py`

---

## How to Add a Regression Test

When fixing a bug:

1. **Create a regression test** in `tests/regression/`
2. **Name it**: `test_regression_<next_number>_<description>.py`
3. **Document it** in this registry below
4. **Include in the test**:
   - Original bug description
   - How it was fixed
   - Date fixed
   - Related issue/ticket number

---

## Regression Test Registry

### Template Entry

```markdown
### RT-XXX: Short Description

**File**: `test_regression_XXX_short_description.py`
**Date**: YYYY-MM-DD
**Issue**: #XXX (if applicable)
**Severity**: Critical | High | Medium | Low

**Original Bug**:
Description of what was broken

**How to Reproduce** (original bug):
Steps to reproduce the original bug

**Fix Applied**:
Description of the fix

**Test Coverage**:
What the regression test verifies
```

---

## Tests

### RT-001: OpenSearch Node Config Must Not Contain Index-Level Settings

**File**: `test_regression_001_opensearch_config_validation.py`
**Date**: 2026-02-04
**Severity**: Critical

**Original Bug**:
OpenSearch node configuration (opensearch.yml) contained index-level settings like `index.number_of_shards`, `index.number_of_replicas`, and slow log settings. This caused OpenSearch to fail startup with error: "node settings must not contain any index level settings"

**How to Reproduce** (original bug):
1. Add `index.number_of_shards: 3` to opensearch.yml
2. Start OpenSearch container
3. Container fails with IllegalArgumentException

**Fix Applied**:
- Removed all index-level settings from opensearch.yml
- Moved them to index templates (configs/index-templates/logs-template.json)
- Added documentation comments explaining where index settings belong
- Also fixed HTTP header size limit (increased to 16kb)

**Test Coverage**:
- Verifies no forbidden index-level settings in node config
- Verifies http.max_header_size is set to prevent header size errors

---

### RT-002: OpenSearch Dashboards Config Validation Errors

**File**: `test_regression_002_opensearch_dashboards_config.py`
**Date**: 2026-02-04
**Severity**: Critical

**Original Bug**:
OpenSearch Dashboards configuration had multiple invalid settings:
1. `server.basePath` set to empty string `""` causing "must start with a slash" error
2. `server.cors.enabled` instead of `server.cors` causing "expected boolean got Object" error
3. Unsupported config keys: `opensearch_security.*`, `telemetry.*` causing "Unknown configuration key" errors

These caused container restart loops with validation errors.

**How to Reproduce** (original bug):
1. Set `server.basePath: ""` in opensearch_dashboards.yml
2. Set `server.cors.enabled: false`
3. Add `opensearch_security.auth.type: ""`
4. Start Dashboards container
5. Container fails with config validation errors

**Fix Applied**:
- Commented out server.basePath (use default)
- Changed `server.cors.enabled` to `server.cors: false`
- Removed all `opensearch_security.*` and `telemetry.*` keys

**Test Coverage**:
- Verifies server.basePath is not set to empty string
- Verifies server.cors is boolean, not object
- Verifies no unsupported security and telemetry keys

---

### RT-003: Docker Compose Hardcoded Ports

**File**: `test_regression_003_docker_compose_ports.py`
**Date**: 2026-02-04
**Severity**: Medium

**Original Bug**:
Docker Compose had hardcoded ports instead of using environment variables. This made it impossible to change ports without editing docker-compose.yml. Example: Grafana port was hardcoded as `"3000:3000"` instead of `"${GRAFANA_PORT:-3000}:3000"`

**How to Reproduce** (original bug):
1. Try to change Grafana port by setting `GRAFANA_PORT=3100` in .env
2. Run `docker compose up -d`
3. Grafana still binds to port 3000 (hardcoded value ignored environment variable)

**Fix Applied**:
Updated all port mappings in docker-compose.yml to use environment variables with defaults:
- OpenSearch: `${OPENSEARCH_PORT:-9200}`
- Dashboards: `${OPENSEARCH_DASHBOARDS_PORT:-5601}`
- Prometheus: `${PROMETHEUS_PORT:-9090}`
- Grafana: `${GRAFANA_PORT:-3000}`
- Fluent Bit: `${FLUENT_BIT_FORWARD_PORT:-24224}`
- Analytics API: `${API_PORT:-8000}`

**Test Coverage**:
- Verifies no hardcoded port mappings exist
- Verifies all port variables have default values
- Verifies common service ports are configurable

---

### RT-004: Analytics API Endpoints

**File**: `tests/integration/test_regression_004_analytics_api_endpoints.py`
**Date**: 2026-02-04
**Severity**: High
**Moved**: Relocated from `tests/regression/` to `tests/integration/` (2026-02-06) - requires running services (OpenSearch + API), making it an integration test

**Original Feature**:
Analytics API with comprehensive endpoints for health checks, search, aggregations, and index management was implemented in version 0.2.1+. The API provides a RESTful interface to OpenSearch with full Pydantic validation and OpenAPI documentation.

**How to Use**:
1. Ensure OpenSearch is running at http://localhost:9200
2. Ensure Analytics API is running at http://localhost:8000
3. Generate sample data: `python scripts/data/generate_sample_logs.py`
4. Run test: `pytest tests/integration/test_regression_004_analytics_api_endpoints.py -v`

**Implementation Details**:
- Health check endpoints (/health/, /health/liveness, /health/readiness)
- Search endpoints (GET /search/simple, POST /search)
- Aggregation endpoints (POST /aggregate, GET /top-values/{field})
- Index management endpoints (GET /indices/, GET /indices/{name}/stats, etc.)
- All endpoints follow standard response format with proper error handling
- Support for terms, date_histogram, stats, and cardinality aggregations

**Test Coverage**:
- Verifies all health check endpoints return correct status
- Validates search functionality with various query types
- Tests aggregation types (terms, date_histogram) with filters
- Confirms index management operations (list, stats, mappings)
- Validates error handling for invalid queries and non-existent indices
- Ensures all responses follow the standard API response format

---

### RT-005: Dashboard Panel References Must Match

**File**: `test_regression_005_dashboard_panel_references.py`
**Date**: 2026-02-06
**Severity**: High

**Original Bug**:
OpenSearch Dashboards showed "Could not find reference 'panel_1'" errors when loading imported dashboards. The panelRefName values in panelsJSON did not match the reference name values in the references array.

**How to Reproduce** (original bug):
1. Import dashboards.ndjson into OpenSearch Dashboards
2. Open Operations Dashboard or Analytics Dashboard
3. Panels fail to load with "Could not find reference" errors

**Fix Applied**:
- Corrected reference naming in dashboards.ndjson
- Ensured panelRefName in panelsJSON uses 0-based indexing (panel_0, panel_1, ...)
- Ensured references array name field matches panelRefName exactly

**Test Coverage**:
- Verifies every panelRefName has a matching reference entry
- Verifies references point to valid visualization IDs (viz-* naming)
- Verifies panel indices are 0-based sequential
- Verifies panel count matches reference count

---

### RT-006: Sample Data Generator Windows Encoding Compatibility

**File**: `test_regression_006_sample_data_encoding.py`
**Date**: 2026-02-06
**Severity**: Medium

**Original Bug**:
The sample log generator used Unicode symbols (checkmarks, crosses) in output messages. On Windows systems with default cp1252 encoding, this caused UnicodeEncodeError crashes when printing to console.

**How to Reproduce** (original bug):
1. Run generate_sample_logs.py on Windows with default console encoding
2. Script crashes with UnicodeEncodeError on first Unicode symbol output

**Fix Applied**:
- Replaced Unicode symbols with ASCII equivalents: [OK], [ERROR]
- Ensured all output strings use only ASCII-safe characters
- JSON data itself uses UTF-8 (handled by json.dumps)

**Test Coverage**:
- Verifies no problematic Unicode symbols in generator source
- Verifies ASCII-safe status indicators are used
- Verifies generator is valid Python (parses without errors)
- Verifies log entries are JSON serializable

---

### RT-007: Fluent Bit Configuration Validation

**File**: `test_regression_007_fluent_bit_config_validation.py`
**Date**: 2026-02-06
**Severity**: High

**Original Bug**:
Fluent Bit configuration must follow strict INI-style format with required sections and valid directives. Misconfigured Fluent Bit causes silent log loss - events are dropped without errors.

**How to Reproduce** (original bug):
1. Remove [SERVICE] section or required directives from fluent-bit.conf
2. Start Fluent Bit container
3. Logs are silently dropped or ingestion fails without clear errors

**Fix Applied**:
- Ensured [SERVICE] section has Flush, Daemon, and Log_Level directives
- Configured forward input on standard port 24224
- OpenSearch output has Logstash_Format On and Suppress_Type_Name On

**Test Coverage**:
- Verifies [SERVICE] section exists with required directives
- Verifies at least one [INPUT] and [OUTPUT] section exist
- Verifies OpenSearch output has Logstash_Format On
- Verifies Suppress_Type_Name On for OpenSearch 2.x compatibility
- Verifies forward input on port 24224
- Verifies parsers file is referenced

---

### RT-008: ILM Policy Validation

**File**: `test_regression_008_ilm_policy_validation.py`
**Date**: 2026-02-06
**Severity**: High

**Original Bug**:
A misconfigured ILM policy causes indices to accumulate without cleanup (disk exhaustion) or premature deletion of logs needed for compliance. All four lifecycle phases must be present with correct min_age progression.

**How to Reproduce** (original bug):
1. Remove or misconfigure a phase in logs-lifecycle-policy.json
2. Apply policy to OpenSearch
3. Indices either never get deleted (disk fills up) or get deleted too early

**Fix Applied**:
- Ensured all 4 phases (hot/warm/cold/delete) are defined
- Hot phase has rollover with max_age and max_primary_shard_size
- Warm phase has forcemerge and shrink for storage optimization
- Cold phase reduces replicas to 0
- Delete phase set to 30d minimum for compliance retention

**Test Coverage**:
- Verifies all four lifecycle phases exist
- Verifies min_age increases monotonically across phases
- Verifies hot phase has rollover action
- Verifies delete phase has delete action
- Verifies warm phase optimization actions (forcemerge, shrink)
- Verifies cold phase reduces replicas to 0
- Verifies policy is valid JSON
- Verifies delete min_age is at least 30 days

---

### RT-009: OpenSearch Cluster Formation Validation

**File**: `test_regression_009_docker_compose_cluster_formation.py`
**Date**: 2026-02-06
**Severity**: Critical

**Original Bug**:
Mismatched cluster names, missing seed hosts, or inconsistent initial manager nodes in Docker Compose prevent the OpenSearch cluster from forming properly, causing split-brain or single-node operation.

**How to Reproduce** (original bug):
1. Change cluster.name on one node to a different value
2. Start docker compose
3. Nodes form separate clusters instead of joining together

**Fix Applied**:
- All 3 nodes share cluster.name=vaultize-cluster
- discovery.seed_hosts lists all 3 nodes
- cluster.initial_cluster_manager_nodes lists all 3 nodes
- All nodes on same Docker network with shared opensearch.yml

**Test Coverage**:
- Verifies exactly 3 OpenSearch nodes defined
- Verifies consistent cluster.name across all nodes
- Verifies discovery.seed_hosts lists all nodes
- Verifies cluster.initial_cluster_manager_nodes lists all nodes
- Verifies all nodes on same Docker network
- Verifies shared opensearch.yml config mounted
- Verifies bootstrap.memory_lock enabled
- Verifies healthchecks defined on all nodes
- Verifies consistent OpenSearch image version

---

## Example (For Reference)

### RT-001: OpenSearch Index Creation Race Condition

**File**: `test_regression_001_index_creation_race_condition.py`
**Date**: 2026-02-04 (Example)
**Issue**: #001
**Severity**: High

**Original Bug**:
When multiple workers tried to create the same index concurrently, the second worker would fail with a "resource_already_exists_exception" and crash.

**How to Reproduce** (original bug):
1. Start two API workers simultaneously
2. Both try to create the `logs-2026-02-04` index on startup
3. Second worker receives exception and exits

**Fix Applied**:
Added idempotency check: before creating an index, check if it exists. If it exists, log a warning and continue instead of failing.

```python
if not client.indices.exists(index=index_name):
    client.indices.create(index=index_name, body=index_config)
else:
    logger.warning(f"Index {index_name} already exists, skipping creation")
```

**Test Coverage**:
The regression test verifies that:
- Multiple concurrent calls to `create_index()` with the same name succeed
- No exceptions are raised
- The index is created exactly once
- All callers return successfully

---

## Statistics

| Category | Count |
|----------|-------|
| **Total Regression Tests** | 8 |
| **Integration Tests (moved)** | 1 (RT-004) |
| **Critical Severity** | 3 |
| **High Severity** | 3 |
| **Medium Severity** | 2 |
| **Low Severity** | 0 |

---

## Regression Test Guidelines

1. **Every bug fix requires a regression test**
   - No exceptions
   - Test must fail before fix, pass after fix

2. **Tests are never deleted**
   - Even if the feature changes, update the test
   - Tests serve as documentation of historical issues

3. **Tests must be well-documented**
   - Include detailed comments in the test file
   - Update this registry with each new test

4. **Tests must be isolated**
   - No dependencies on other tests
   - Clean up after themselves
   - Use fixtures for common setup

5. **Tests should be fast**
   - Target: < 5 seconds per test
   - Use mocks where appropriate
   - Skip integration tests if unit test sufficient

---

## Running Regression Tests

```bash
# Run all regression tests
pytest tests/regression/

# Run specific regression test
pytest tests/regression/test_regression_001_*.py

# Run with verbose output to see descriptions
pytest tests/regression/ -v

# Check regression test coverage
pytest tests/regression/ --cov=analytics --cov=ingestion
```

---

## Regression Test Template

Use this template when creating a new regression test:

```python
"""
Regression Test RT-XXX: Short Description

Original Bug:
    Description of what was broken

How to Reproduce:
    1. Step 1
    2. Step 2
    3. Expected failure

Fix Applied:
    Description of the fix

Date: YYYY-MM-DD
Issue: #XXX
Severity: Critical | High | Medium | Low
"""

import pytest


class TestRegressionXXX:
    """Regression tests for issue #XXX"""

    def test_regression_XXX_specific_scenario(self):
        """
        Verify that [specific scenario] no longer causes [original bug].

        This test would have failed before the fix and passes after.
        """
        # Arrange
        # Set up the conditions that triggered the bug

        # Act
        # Execute the code that previously failed

        # Assert
        # Verify the bug is fixed
        assert True  # Replace with actual assertion

    def test_regression_XXX_edge_case(self):
        """
        Verify edge cases related to the fix.
        """
        # Additional test for edge cases
        pass
```

---

## Maintenance

- **Weekly**: Review regression test failures in CI
- **Monthly**: Audit regression tests for relevance
- **Quarterly**: Refactor slow regression tests
- **Annually**: Review and document regression test trends

---

## Next Steps

1. As bugs are discovered and fixed, add them to this registry
2. Ensure all regression tests are documented
3. Run regression suite before every release
4. Review failed regression tests immediately (may indicate new bugs)

---

**Last Updated**: 2026-02-06 (Updated: Added RT-005 through RT-009 regression tests)
