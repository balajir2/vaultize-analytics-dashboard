"""
E2E Test Configuration and Fixtures

Provides fixtures for E2E tests that require running services.
Tests are skipped if services are not available.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import time

import pytest
import requests

# ============================================================================
# Service URLs
# ============================================================================

OPENSEARCH_URL = "http://localhost:9200"
DASHBOARDS_URL = "http://localhost:5601"
API_URL = "http://localhost:8000"
ALERTING_URL = "http://localhost:8001"


# ============================================================================
# Service Availability Check
# ============================================================================

def is_service_up(url: str, timeout: int = 5) -> bool:
    """Check if a service is reachable."""
    try:
        resp = requests.get(url, timeout=timeout)
        return resp.status_code < 500
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return False


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def opensearch_available():
    """Skip tests if OpenSearch is not running."""
    if not is_service_up(f"{OPENSEARCH_URL}/_cluster/health"):
        pytest.skip("OpenSearch is not running")
    return OPENSEARCH_URL


@pytest.fixture(scope="session")
def dashboards_available():
    """Skip tests if OpenSearch Dashboards is not running."""
    if not is_service_up(f"{DASHBOARDS_URL}/api/status"):
        pytest.skip("OpenSearch Dashboards is not running")
    return DASHBOARDS_URL


@pytest.fixture(scope="session")
def api_available():
    """Skip tests if Analytics API is not running."""
    if not is_service_up(f"{API_URL}/health/liveness"):
        pytest.skip("Analytics API is not running")
    return API_URL


@pytest.fixture(scope="session")
def alerting_available():
    """Skip tests if Alerting Service is not running."""
    if not is_service_up(f"{ALERTING_URL}/health/liveness"):
        pytest.skip("Alerting Service is not running")
    return ALERTING_URL


@pytest.fixture
def cleanup_test_indices(opensearch_available):
    """Delete test indices after the test completes."""
    created_indices = []

    def register(index_name):
        created_indices.append(index_name)
        return index_name

    yield register

    for idx in created_indices:
        try:
            requests.delete(f"{opensearch_available}/{idx}", timeout=10)
        except Exception:
            pass


def wait_for_index(opensearch_url: str, index_pattern: str, timeout: int = 30) -> bool:
    """Wait for an index matching the pattern to appear."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            resp = requests.get(
                f"{opensearch_url}/_cat/indices/{index_pattern}?format=json",
                timeout=5,
            )
            if resp.status_code == 200 and resp.json():
                return True
        except Exception:
            pass
        time.sleep(2)
    return False


def wait_for_doc_count(opensearch_url: str, index: str, min_count: int, timeout: int = 30) -> int:
    """Wait until an index has at least min_count documents."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            resp = requests.get(f"{opensearch_url}/{index}/_count", timeout=5)
            if resp.status_code == 200:
                count = resp.json().get("count", 0)
                if count >= min_count:
                    return count
        except Exception:
            pass
        time.sleep(2)
    return 0
