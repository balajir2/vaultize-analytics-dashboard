"""
E2E Test: Log Ingestion Flow

Tests the complete log ingestion pipeline:
  Generate log data -> Fluent Bit -> OpenSearch -> API search

Requires: All core services running (docker compose up -d)

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import uuid

import pytest
import requests

pytestmark = pytest.mark.e2e


# ============================================================================
# Tests: Log Ingestion Pipeline
# ============================================================================

class TestLogIngestionFlow:
    """End-to-end log ingestion: forward -> OpenSearch -> API."""

    def test_opensearch_cluster_healthy(self, opensearch_available):
        """Cluster must be green or yellow."""
        resp = requests.get(f"{opensearch_available}/_cluster/health", timeout=10)
        assert resp.status_code == 200
        assert resp.json()["status"] in ("green", "yellow")

    def test_log_indices_exist(self, opensearch_available):
        """Log indices should exist after ingestion."""
        resp = requests.get(
            f"{opensearch_available}/_cat/indices/logs-*?format=json",
            timeout=10,
        )
        assert resp.status_code == 200
        indices = resp.json()
        assert len(indices) > 0, "No log indices found — has data been ingested?"

    def test_api_search_returns_logs(self, api_available, opensearch_available):
        """API search endpoint returns log data."""
        resp = requests.get(
            f"{api_available}/api/v1/search",
            params={"q": "*", "index": "logs-*", "size": 5},
            timeout=10,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("total", 0) > 0 or len(data.get("hits", [])) > 0

    def test_api_aggregation_returns_results(self, api_available):
        """API aggregation endpoint works."""
        resp = requests.post(
            f"{api_available}/api/v1/aggregations",
            json={
                "index": "logs-*",
                "aggs": {
                    "levels": {
                        "terms": {"field": "level.keyword", "size": 10}
                    }
                }
            },
            timeout=10,
        )
        assert resp.status_code == 200

    def test_direct_index_and_search(self, opensearch_available, cleanup_test_indices):
        """Index a document directly and search for it."""
        test_index = cleanup_test_indices(f"test-e2e-{uuid.uuid4().hex[:8]}")
        test_id = uuid.uuid4().hex

        # Index a document
        doc = {
            "@timestamp": "2026-02-17T12:00:00Z",
            "message": f"E2E test log entry {test_id}",
            "level": "INFO",
            "service": "e2e-test",
        }
        resp = requests.post(
            f"{opensearch_available}/{test_index}/_doc?refresh=true",
            json=doc,
            timeout=10,
        )
        assert resp.status_code == 201

        # Search for it
        resp = requests.get(
            f"{opensearch_available}/{test_index}/_search",
            json={"query": {"match": {"message": test_id}}},
            timeout=10,
        )
        assert resp.status_code == 200
        hits = resp.json()["hits"]["total"]["value"]
        assert hits == 1
