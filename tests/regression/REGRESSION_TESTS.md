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

_No regression tests yet. This section will be populated as bugs are discovered and fixed._

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
| **Total Regression Tests** | 0 |
| **Critical Severity** | 0 |
| **High Severity** | 0 |
| **Medium Severity** | 0 |
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
