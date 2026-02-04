# Test Suite

> Comprehensive testing documentation for Vaultize Analytics Platform

**Last Updated**: 2026-02-04

---

## Overview

This directory contains all tests for the platform, organized by test type and scope.

**Testing Philosophy**: Every piece of functionality must have associated tests. Untested code is considered incomplete.

---

## Test Structure

```
tests/
├── unit/              # Fast, isolated tests for individual functions/methods
├── integration/       # Tests for service integrations (OpenSearch, APIs, etc.)
├── regression/        # Tests to prevent previously fixed bugs from reoccurring
├── e2e/              # End-to-end tests for complete user flows
├── performance/       # Load and performance tests
├── fixtures/          # Shared test fixtures and data
├── conftest.py       # Pytest configuration and shared fixtures
└── README.md         # This file
```

---

## Test Categories

### Unit Tests (`tests/unit/`)

**Purpose**: Test individual functions, methods, and classes in isolation.

**Characteristics**:
- Fast (< 100ms per test)
- No external dependencies (use mocks/stubs)
- High coverage (>80% target)
- Test one thing per test

**Example**:
```python
# tests/unit/analytics/test_query_builder.py
def test_build_search_query_with_time_range():
    builder = QueryBuilder()
    query = builder.build_search(
        query_string="error",
        time_range={"from": "now-1h", "to": "now"}
    )
    assert query["query"]["bool"]["must"][0]["match"]["message"] == "error"
    assert "range" in query["query"]["bool"]["filter"][0]
```

**Run**: `pytest tests/unit/`

---

### Integration Tests (`tests/integration/`)

**Purpose**: Test interactions between components and external systems.

**Characteristics**:
- Slower (< 5s per test typically)
- May use real services (OpenSearch, databases)
- Test service boundaries
- Use test containers where possible

**Example**:
```python
# tests/integration/test_opensearch_integration.py
def test_index_document_to_opensearch(opensearch_client):
    """Test actual document indexing to OpenSearch test cluster"""
    doc = {"message": "test log", "level": "INFO"}
    response = opensearch_client.index(
        index="test-logs",
        body=doc
    )
    assert response["result"] == "created"
```

**Run**: `pytest tests/integration/`

**Requirements**:
- Docker Compose test environment must be running
- See `tests/integration/README.md` for setup

---

### Regression Tests (`tests/regression/`)

**Purpose**: Prevent previously fixed bugs from reoccurring.

**Characteristics**:
- Each test documents a specific bug/issue
- Named with issue number: `test_regression_<number>_<description>.py`
- Includes comments explaining the original bug
- Never deleted (even if feature changes, test is updated)

**Example**:
```python
# tests/regression/test_regression_001_index_creation_race_condition.py
def test_regression_001_concurrent_index_creation():
    """
    Regression test for issue #001

    Bug: Creating the same index concurrently caused conflicts
    Fix: Added idempotency check before index creation
    Date: 2026-02-04
    """
    # Test that concurrent index creation is idempotent
    ...
```

**Run**: `pytest tests/regression/`

**Registry**: See [REGRESSION_TESTS.md](./regression/REGRESSION_TESTS.md) for complete list

---

### E2E Tests (`tests/e2e/`)

**Purpose**: Test complete user workflows from start to finish.

**Characteristics**:
- Slowest (may take 10s-60s)
- Test entire system integration
- Use real services in test mode
- Simulate actual user scenarios

**Example**:
```python
# tests/e2e/test_log_ingestion_flow.py
def test_complete_log_flow():
    """Test: Log file → Fluent Bit → OpenSearch → Query → Dashboard"""
    # 1. Generate test log file
    # 2. Configure Fluent Bit to read it
    # 3. Wait for ingestion
    # 4. Query OpenSearch for the log
    # 5. Verify log appears in dashboard
    ...
```

**Run**: `pytest tests/e2e/`

---

### Performance Tests (`tests/performance/`)

**Purpose**: Validate system performance under load.

**Characteristics**:
- Long-running (minutes to hours)
- Measure throughput, latency, resource usage
- Not run in regular CI (separate pipeline)
- Use load generation tools

**Example**:
```python
# tests/performance/test_ingestion_throughput.py
def test_ingestion_handles_10k_logs_per_second():
    """Verify platform can ingest 10K logs/sec sustained"""
    # Generate 10K logs/sec for 5 minutes
    # Measure ingestion lag, resource usage
    # Assert lag < 30 seconds
    ...
```

**Run**: `pytest tests/performance/ --performance`

---

## Running Tests

### Quick Start

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=analytics --cov=ingestion --cov-report=html

# Run specific test category
pytest tests/unit/
pytest tests/integration/
pytest tests/regression/
pytest tests/e2e/
```

### Advanced Usage

```bash
# Run tests matching a pattern
pytest -k "test_search"

# Run tests with verbose output
pytest -v

# Run tests and stop on first failure
pytest -x

# Run tests in parallel (faster)
pytest -n auto

# Run only failed tests from last run
pytest --lf

# Generate HTML coverage report
pytest --cov --cov-report=html
open htmlcov/index.html
```

### CI/CD Integration

```bash
# Standard CI pipeline
pytest tests/unit/ tests/integration/ tests/regression/ --cov --cov-fail-under=80

# Full pipeline (includes E2E)
pytest tests/ --cov --cov-fail-under=80

# Performance tests (separate job)
pytest tests/performance/ --performance
```

---

## Test Configuration

### conftest.py

Shared pytest configuration and fixtures are defined in `conftest.py`:

```python
# tests/conftest.py
import pytest
from opensearchpy import OpenSearch

@pytest.fixture
def opensearch_client():
    """Fixture providing OpenSearch test client"""
    client = OpenSearch(
        hosts=[{'host': 'localhost', 'port': 9200}],
        http_auth=('admin', 'admin')
    )
    yield client
    # Cleanup test indices
    client.indices.delete(index="test-*", ignore=[404])

@pytest.fixture
def sample_log_data():
    """Fixture providing sample log data for tests"""
    return [
        {"timestamp": "2026-02-04T10:00:00Z", "level": "INFO", "message": "test1"},
        {"timestamp": "2026-02-04T10:01:00Z", "level": "ERROR", "message": "test2"},
    ]
```

### pytest.ini

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --tb=short
    --cov-report=term-missing
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (require services)
    regression: Regression tests (prevent bugs from returning)
    e2e: End-to-end tests (full workflows)
    performance: Performance/load tests (slow, run separately)
    slow: Tests that take > 5 seconds
```

---

## Test Fixtures

### Shared Fixtures (`tests/fixtures/`)

```
fixtures/
├── sample_logs.json          # Sample log data
├── index_templates/          # Test index templates
├── alert_rules/              # Test alert configurations
└── dashboards/               # Test dashboard exports
```

**Usage**:
```python
import json
from pathlib import Path

def load_fixture(filename):
    fixture_path = Path(__file__).parent / "fixtures" / filename
    with open(fixture_path) as f:
        return json.load(f)

def test_with_fixture():
    data = load_fixture("sample_logs.json")
    assert len(data) > 0
```

---

## Writing Good Tests

### AAA Pattern (Arrange-Act-Assert)

```python
def test_search_logs_by_level():
    # Arrange: Set up test data and conditions
    client = OpenSearchClient()
    test_logs = [
        {"level": "ERROR", "message": "error1"},
        {"level": "INFO", "message": "info1"}
    ]

    # Act: Execute the code under test
    results = client.search(query={"match": {"level": "ERROR"}})

    # Assert: Verify the expected outcome
    assert len(results) == 1
    assert results[0]["level"] == "ERROR"
```

### Test Naming

```python
# Good: Descriptive, specific
def test_search_returns_empty_list_when_no_matches():
    ...

def test_alert_fires_when_threshold_exceeded():
    ...

# Bad: Vague, unclear
def test_search():
    ...

def test_alert():
    ...
```

### Mocking External Dependencies

```python
from unittest.mock import Mock, patch

def test_alert_notification_sends_webhook():
    # Mock the HTTP client to avoid actual network calls
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200

        notifier = WebhookNotifier(url="https://example.com/hook")
        result = notifier.send({"alert": "test"})

        assert result is True
        mock_post.assert_called_once()
```

---

## Test Data Management

### Test Database/Indices

- Use `test-*` prefix for all test indices
- Clean up after each test
- Never use production indices in tests

### Test Environment Variables

```bash
# .env.test
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200
OPENSEARCH_USER=admin
OPENSEARCH_PASSWORD=admin
TEST_MODE=true
LOG_LEVEL=DEBUG
```

Load in conftest.py:
```python
from dotenv import load_dotenv
load_dotenv(".env.test")
```

---

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      opensearch:
        image: opensearchproject/opensearch:2.11.0
        env:
          discovery.type: single-node
        ports:
          - 9200:9200

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt

      - name: Run unit tests
        run: pytest tests/unit/ --cov --cov-report=xml

      - name: Run integration tests
        run: pytest tests/integration/

      - name: Run regression tests
        run: pytest tests/regression/

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Coverage Requirements

| Component | Minimum Coverage | Target Coverage |
|-----------|-----------------|-----------------|
| **Analytics API** | 80% | 90% |
| **Alerting Service** | 80% | 90% |
| **Index Management** | 70% | 85% |
| **Utilities** | 60% | 75% |
| **Overall** | 75% | 85% |

**View Coverage**:
```bash
pytest --cov --cov-report=html
open htmlcov/index.html
```

---

## Troubleshooting Tests

### Common Issues

**Issue**: Tests fail with "Connection refused" to OpenSearch
```bash
# Solution: Start test environment
docker compose -f docker-compose.test.yml up -d
```

**Issue**: Tests fail intermittently
```bash
# Solution: Increase timeouts, ensure proper cleanup
# Add to conftest.py:
@pytest.fixture(autouse=True)
def cleanup_after_test():
    yield
    # Cleanup code here
```

**Issue**: Slow tests
```bash
# Solution: Run in parallel
pytest -n auto

# Or: Mark slow tests and skip them
pytest -m "not slow"
```

---

## Test Metrics

Track these metrics to maintain test quality:

- **Test Count**: Growing with codebase
- **Test Coverage**: Target >80%
- **Test Execution Time**: Should not increase linearly
- **Flaky Test Rate**: Should be <1%
- **Test Failure Rate**: Should trend towards 0%

---

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [Mock Documentation](https://docs.python.org/3/library/unittest.mock.html)

---

## Next Steps

1. Set up test environment: `docker compose -f docker-compose.test.yml up`
2. Install test dependencies: `pip install -r requirements-test.txt`
3. Run tests: `pytest`
4. Write tests for new features following this guide

---

**Questions or Issues?**
- See [Troubleshooting](#troubleshooting-tests)
- Review [Writing Good Tests](#writing-good-tests)
- Check [CI/CD Integration](#continuous-integration)

---

**Last Updated**: 2026-02-04
