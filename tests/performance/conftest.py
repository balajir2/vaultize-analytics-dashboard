"""
Performance Test Configuration and Utilities

Provides fixtures and timing utilities for performance benchmarks.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import time
import uuid
from contextlib import contextmanager

import pytest
import requests

# ============================================================================
# Configuration
# ============================================================================

OPENSEARCH_URL = "http://localhost:9200"
API_URL = "http://localhost:8000"


def is_service_up(url: str) -> bool:
    try:
        return requests.get(url, timeout=5).status_code < 500
    except Exception:
        return False


# ============================================================================
# Timer Utility
# ============================================================================

@contextmanager
def timer(label: str = ""):
    """Context manager that measures wall-clock time."""
    start = time.perf_counter()
    result = {"elapsed": 0.0}
    yield result
    result["elapsed"] = time.perf_counter() - start
    if label:
        print(f"  {label}: {result['elapsed']:.3f}s")


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def require_opensearch():
    if not is_service_up(f"{OPENSEARCH_URL}/_cluster/health"):
        pytest.skip("OpenSearch is not running")
    return OPENSEARCH_URL


@pytest.fixture(scope="session")
def require_api():
    if not is_service_up(f"{API_URL}/health/liveness"):
        pytest.skip("Analytics API is not running")
    return API_URL


@pytest.fixture
def perf_index(require_opensearch):
    """Create a temporary performance test index."""
    index_name = f"perf-test-{uuid.uuid4().hex[:8]}"
    yield index_name
    requests.delete(f"{require_opensearch}/{index_name}", timeout=10)
