"""
Pytest configuration and shared fixtures for all tests.

This file contains global pytest configuration and fixtures that are
available to all tests across the test suite.
"""

import os
import pytest
from pathlib import Path
from typing import Generator


# ============================================================================
# Test Configuration
# ============================================================================

def pytest_configure(config):
    """
    Pytest hook for initial configuration.

    Sets up test markers and environment variables.
    """
    # Register custom markers
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (require services)"
    )
    config.addinivalue_line(
        "markers", "regression: Regression tests (prevent bugs from returning)"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests (full workflows)"
    )
    config.addinivalue_line(
        "markers", "performance: Performance/load tests (slow, run separately)"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take > 5 seconds"
    )

    # Set test environment variables
    os.environ["TEST_MODE"] = "true"
    os.environ["LOG_LEVEL"] = "DEBUG"


# ============================================================================
# Path Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def project_root() -> Path:
    """
    Fixture providing path to project root directory.

    Returns:
        Path object pointing to project root
    """
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """
    Fixture providing path to test fixtures directory.

    Returns:
        Path object pointing to tests/fixtures/
    """
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def config_dir(project_root: Path) -> Path:
    """
    Fixture providing path to configs directory.

    Returns:
        Path object pointing to configs/
    """
    return project_root / "configs"


# ============================================================================
# OpenSearch Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def opensearch_host() -> str:
    """
    Fixture providing OpenSearch host.

    Returns:
        OpenSearch host (from env or default)
    """
    return os.getenv("OPENSEARCH_HOST", "localhost")


@pytest.fixture(scope="session")
def opensearch_port() -> int:
    """
    Fixture providing OpenSearch port.

    Returns:
        OpenSearch port (from env or default)
    """
    return int(os.getenv("OPENSEARCH_PORT", "9200"))


@pytest.fixture(scope="session")
def opensearch_credentials() -> tuple[str, str]:
    """
    Fixture providing OpenSearch authentication credentials.

    Returns:
        Tuple of (username, password)
    """
    username = os.getenv("OPENSEARCH_USER", "admin")
    password = os.getenv("OPENSEARCH_PASSWORD", "admin")
    return (username, password)


@pytest.fixture
def opensearch_client(
    opensearch_host: str,
    opensearch_port: int,
    opensearch_credentials: tuple[str, str]
):
    """
    Fixture providing OpenSearch client for testing.

    Automatically cleans up test indices after each test.

    Yields:
        OpenSearch client instance
    """
    # Import here to avoid requiring opensearch-py for all tests
    from opensearchpy import OpenSearch

    username, password = opensearch_credentials

    client = OpenSearch(
        hosts=[{"host": opensearch_host, "port": opensearch_port}],
        http_auth=(username, password),
        use_ssl=False,
        verify_certs=False,
        ssl_show_warn=False,
    )

    yield client

    # Cleanup: Delete all test indices (prefix: test-*)
    try:
        client.indices.delete(index="test-*", ignore=[404])
    except Exception as e:
        print(f"Warning: Failed to cleanup test indices: {e}")


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def sample_log_entry() -> dict:
    """
    Fixture providing a single sample log entry.

    Returns:
        Dictionary representing a log entry
    """
    return {
        "timestamp": "2026-02-04T10:00:00Z",
        "level": "INFO",
        "message": "Sample log message",
        "service": "test-service",
        "host": "test-host",
        "environment": "test"
    }


@pytest.fixture
def sample_log_batch() -> list[dict]:
    """
    Fixture providing a batch of sample log entries.

    Returns:
        List of log entry dictionaries
    """
    return [
        {
            "timestamp": "2026-02-04T10:00:00Z",
            "level": "INFO",
            "message": "Application started",
            "service": "api",
            "host": "host-1"
        },
        {
            "timestamp": "2026-02-04T10:01:00Z",
            "level": "ERROR",
            "message": "Connection timeout",
            "service": "api",
            "host": "host-1"
        },
        {
            "timestamp": "2026-02-04T10:02:00Z",
            "level": "WARN",
            "message": "High memory usage",
            "service": "worker",
            "host": "host-2"
        },
        {
            "timestamp": "2026-02-04T10:03:00Z",
            "level": "INFO",
            "message": "Request processed",
            "service": "api",
            "host": "host-1"
        },
    ]


@pytest.fixture
def sample_alert_rule() -> dict:
    """
    Fixture providing a sample alert rule configuration.

    Returns:
        Dictionary representing an alert rule
    """
    return {
        "name": "High Error Rate",
        "description": "Alert when error rate exceeds threshold",
        "query": {
            "match": {"level": "ERROR"}
        },
        "condition": {
            "type": "threshold",
            "operator": "gt",
            "value": 100
        },
        "interval": "5m",
        "actions": [
            {
                "type": "webhook",
                "url": "https://example.com/webhook"
            }
        ]
    }


# ============================================================================
# File Loading Fixtures
# ============================================================================

@pytest.fixture
def load_fixture():
    """
    Fixture providing a function to load JSON fixture files.

    Returns:
        Function that loads JSON files from fixtures directory

    Usage:
        def test_something(load_fixture):
            data = load_fixture("sample_logs.json")
    """
    import json

    fixtures_path = Path(__file__).parent / "fixtures"

    def _load_fixture(filename: str):
        """Load a fixture file by name."""
        file_path = fixtures_path / filename

        if not file_path.exists():
            raise FileNotFoundError(f"Fixture not found: {filename}")

        with open(file_path, "r") as f:
            if filename.endswith(".json"):
                return json.load(f)
            elif filename.endswith(".yaml") or filename.endswith(".yml"):
                import yaml
                return yaml.safe_load(f)
            else:
                return f.read()

    return _load_fixture


# ============================================================================
# Temporary Directory Fixtures
# ============================================================================

@pytest.fixture
def temp_log_file(tmp_path: Path) -> Generator[Path, None, None]:
    """
    Fixture providing a temporary log file.

    Args:
        tmp_path: pytest's built-in temporary directory fixture

    Yields:
        Path to temporary log file
    """
    log_file = tmp_path / "test.log"
    log_file.touch()

    yield log_file

    # Cleanup happens automatically with tmp_path


# ============================================================================
# Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_webhook_server():
    """
    Fixture providing a mock webhook server for testing notifications.

    Yields:
        Mock server with tracking of received requests
    """
    from unittest.mock import Mock

    mock_server = Mock()
    mock_server.received_requests = []

    def record_request(method, url, **kwargs):
        mock_server.received_requests.append({
            "method": method,
            "url": url,
            "kwargs": kwargs
        })
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"status": "ok"}
        return response

    mock_server.post = Mock(side_effect=lambda url, **kwargs: record_request("POST", url, **kwargs))
    mock_server.get = Mock(side_effect=lambda url, **kwargs: record_request("GET", url, **kwargs))

    yield mock_server


# ============================================================================
# Test Isolation
# ============================================================================

@pytest.fixture(autouse=True)
def isolate_tests():
    """
    Auto-use fixture to ensure test isolation.

    Runs before and after each test to ensure clean state.
    """
    # Setup: Run before each test
    # (Add any global setup here)

    yield

    # Teardown: Run after each test
    # (Add any global cleanup here)


# ============================================================================
# Skip Conditions
# ============================================================================

def pytest_collection_modifyitems(config, items):
    """
    Pytest hook to modify test collection.

    Adds skip markers based on environment or conditions.
    """
    # Skip integration tests if SKIP_INTEGRATION env var is set
    if os.getenv("SKIP_INTEGRATION"):
        skip_integration = pytest.mark.skip(reason="SKIP_INTEGRATION is set")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)

    # Skip performance tests unless explicitly requested
    if not config.getoption("--performance", default=False):
        skip_performance = pytest.mark.skip(reason="Performance tests not requested")
        for item in items:
            if "performance" in item.keywords:
                item.add_marker(skip_performance)


def pytest_addoption(parser):
    """
    Pytest hook to add custom command line options.
    """
    parser.addoption(
        "--performance",
        action="store_true",
        default=False,
        help="Run performance tests"
    )


# ============================================================================
# Reporting Hooks
# ============================================================================

def pytest_report_header(config):
    """
    Pytest hook to add custom header to test report.

    Returns:
        List of strings to add to report header
    """
    return [
        "Vaultize Analytics Platform - Test Suite",
        f"Test Mode: {os.getenv('TEST_MODE', 'false')}",
        f"OpenSearch: {os.getenv('OPENSEARCH_HOST', 'localhost')}:{os.getenv('OPENSEARCH_PORT', '9200')}"
    ]
