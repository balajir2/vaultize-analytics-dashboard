# Regression Test Registry

> Complete registry of all regression tests to prevent bug reoccurrence

**Last Updated**: 2026-02-04

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
| **Total Regression Tests** | 3 |
| **Critical Severity** | 2 |
| **High Severity** | 0 |
| **Medium Severity** | 1 |
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

**Last Updated**: 2026-02-04
