# Analytics API Tests

**Authors**: Balaji Rajan and Claude (Anthropic)
**License**: Apache 2.0

Comprehensive test suite for the Analytics API including unit tests and integration tests.

## Test Structure

```
tests/
├── conftest.py                        # Shared fixtures and configuration
├── test_models.py                     # Pydantic model tests
├── test_health_router.py              # Health endpoint tests
├── test_search_router.py              # Search endpoint tests
├── test_aggregations_router.py        # Aggregation endpoint tests
└── test_indices_router.py             # Index management tests
```

## Prerequisites

### Install Test Dependencies

```bash
cd analytics/api
pip install -r requirements-test.txt
```

### Running Services (for integration tests)

Integration tests require running services:
- OpenSearch at http://localhost:9200
- Analytics API at http://localhost:8000

Start services with Docker Compose:
```bash
docker compose up -d
```

## Running Tests

### All Tests

```bash
cd analytics/api
pytest
```

### Unit Tests Only

Unit tests use mocked dependencies and don't require running services:

```bash
pytest -m unit
```

### With Coverage Report

```bash
pytest --cov=app --cov-report=html --cov-report=term
```

This generates:
- Terminal coverage summary
- HTML report in `htmlcov/index.html`

### Specific Test File

```bash
pytest tests/test_models.py
pytest tests/test_health_router.py -v
```

### Specific Test Function

```bash
pytest tests/test_models.py::TestAPIResponse::test_api_response_success
```

## Test Coverage Requirements

Per CLAUDE.md requirements, all code must have **>80% test coverage**.

Check current coverage:
```bash
pytest --cov=app --cov-report=term-missing
```

## Writing New Tests

### Unit Test Template

```python
import pytest
from unittest.mock import patch, MagicMock

class TestMyFeature:
    """Test my feature"""

    @patch('app.module.dependency')
    def test_my_function(self, mock_dep, test_client):
        """Test description"""
        # Arrange
        mock_dep.return_value = expected_value

        # Act
        response = test_client.get("/endpoint")

        # Assert
        assert response.status_code == 200
```

### Using Fixtures

Common fixtures available in `conftest.py`:
- `test_client` - FastAPI TestClient
- `mock_opensearch_client` - Mocked OpenSearch client
- `sample_log_data` - Sample log entry
- `sample_search_response` - Sample search response
- `sample_aggregation_response` - Sample aggregation response

## Test Markers

Tests can be marked for selective execution:

```python
@pytest.mark.unit
def test_something_fast():
    pass

@pytest.mark.integration
def test_with_real_services():
    pass

@pytest.mark.slow
def test_long_running():
    pass
```

Run specific markers:
```bash
pytest -m unit          # Only unit tests
pytest -m integration   # Only integration tests
pytest -m "not slow"    # Skip slow tests
```

## Continuous Integration

Tests run automatically on:
- Pre-commit hooks
- Pull requests
- Main branch commits

## Troubleshooting

### Import Errors

If you see import errors, ensure you're in the correct directory:
```bash
cd analytics/api
export PYTHONPATH=.
pytest
```

### Test Database

Unit tests use mocked data and don't touch real databases.
Integration tests use the live OpenSearch instance.

### Slow Tests

Some integration tests may be slow due to network latency. Use:
```bash
pytest -m "not slow"
```

## Coverage Goals

| Module | Target | Current |
|--------|--------|---------|
| app/models/* | >90% | TBD |
| app/routers/* | >85% | TBD |
| app/config.py | >80% | TBD |
| app/opensearch_client.py | >80% | TBD |

Update coverage after running:
```bash
pytest --cov=app --cov-report=term
```

## References

- [pytest documentation](https://docs.pytest.org/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [CLAUDE.md Testing Requirements](../../CLAUDE.md#testing-requirements)
