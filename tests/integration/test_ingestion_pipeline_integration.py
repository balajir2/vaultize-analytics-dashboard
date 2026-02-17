"""
Integration Test: Ingestion Pipeline

Tests the full ingestion pipeline from data generation through
OpenSearch indexing to API retrieval.

Requires: OpenSearch and Analytics API running.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import uuid

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
# Fixtures
# ============================================================================

@pytest.fixture(scope="module")
def require_opensearch():
    if not is_service_up(f"{OPENSEARCH_URL}/_cluster/health"):
        pytest.skip("OpenSearch is not running")
    return OPENSEARCH_URL


@pytest.fixture(scope="module")
def require_api():
    if not is_service_up(f"{API_URL}/health/liveness"):
        pytest.skip("Analytics API is not running")
    return API_URL


@pytest.fixture
def test_index(require_opensearch):
    """Create a temporary test index and clean up after."""
    index_name = f"test-integration-{uuid.uuid4().hex[:8]}"
    yield index_name
    requests.delete(f"{require_opensearch}/{index_name}", timeout=10)


# ============================================================================
# Tests
# ============================================================================

class TestIngestionPipeline:
    """Integration: index documents -> search via API."""

    def test_index_single_document(self, require_opensearch, test_index):
        """Index a single document and retrieve it."""
        doc = {
            "@timestamp": "2026-02-17T12:00:00Z",
            "message": "Pipeline integration test",
            "level": "INFO",
            "service": "integration-test",
        }
        resp = requests.post(
            f"{require_opensearch}/{test_index}/_doc?refresh=true",
            json=doc,
            timeout=10,
        )
        assert resp.status_code == 201

        # Verify document exists
        resp = requests.get(f"{require_opensearch}/{test_index}/_count", timeout=10)
        assert resp.json()["count"] == 1

    def test_bulk_index_documents(self, require_opensearch, test_index):
        """Bulk index multiple documents."""
        bulk_body = ""
        for i in range(10):
            bulk_body += f'{{"index": {{"_index": "{test_index}"}}}}\n'
            bulk_body += f'{{"@timestamp": "2026-02-17T12:00:{i:02d}Z", "message": "Bulk doc {i}", "level": "INFO"}}\n'

        resp = requests.post(
            f"{require_opensearch}/_bulk?refresh=true",
            data=bulk_body,
            headers={"Content-Type": "application/x-ndjson"},
            timeout=30,
        )
        assert resp.status_code == 200
        assert not resp.json().get("errors", False)

        # Verify count
        resp = requests.get(f"{require_opensearch}/{test_index}/_count", timeout=10)
        assert resp.json()["count"] == 10

    def test_search_via_api(self, require_opensearch, require_api, test_index):
        """Index documents and search via the Analytics API."""
        test_id = uuid.uuid4().hex

        # Index a document
        doc = {
            "@timestamp": "2026-02-17T12:00:00Z",
            "message": f"API search test {test_id}",
            "level": "WARNING",
            "service": "integration-test",
        }
        requests.post(
            f"{require_opensearch}/{test_index}/_doc?refresh=true",
            json=doc,
            timeout=10,
        )

        # Search via API
        resp = requests.get(
            f"{require_api}/api/v1/search",
            params={"q": test_id, "index": test_index, "size": 10},
            timeout=10,
        )
        assert resp.status_code == 200

    def test_aggregation_via_api(self, require_opensearch, require_api, test_index):
        """Index documents and aggregate via the Analytics API."""
        # Index some documents with different levels
        for level in ["INFO", "WARNING", "ERROR", "INFO", "INFO"]:
            doc = {
                "@timestamp": "2026-02-17T12:00:00Z",
                "message": "Agg test",
                "level": level,
            }
            requests.post(
                f"{require_opensearch}/{test_index}/_doc",
                json=doc,
                timeout=10,
            )

        requests.post(f"{require_opensearch}/{test_index}/_refresh", timeout=10)

        # Aggregate via API
        resp = requests.post(
            f"{require_api}/api/v1/aggregations",
            json={
                "index": test_index,
                "aggs": {
                    "by_level": {"terms": {"field": "level.keyword", "size": 10}}
                },
            },
            timeout=10,
        )
        assert resp.status_code == 200
