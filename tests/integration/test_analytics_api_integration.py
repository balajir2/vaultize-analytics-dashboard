"""
Integration Tests for Analytics API

Tests the Analytics API with actual OpenSearch connectivity.
These tests require OpenSearch and the Analytics API to be running.

Prerequisites:
- OpenSearch running at http://localhost:9200
- Analytics API running at http://localhost:8000
- Sample log data indexed (run scripts/data/generate_sample_logs.py)

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import pytest
import requests
import time
from typing import Dict, Any


# ============================================================================
# Configuration
# ============================================================================

OPENSEARCH_URL = "http://localhost:9200"
API_BASE_URL = "http://localhost:8000"
API_V1_URL = f"{API_BASE_URL}/api/v1"

# Test timeout for API requests
REQUEST_TIMEOUT = 5


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="module")
def opensearch_health():
    """
    Verify OpenSearch is running before tests.
    """
    try:
        response = requests.get(OPENSEARCH_URL, timeout=REQUEST_TIMEOUT)
        assert response.status_code == 200, "OpenSearch is not reachable"
        return response.json()
    except requests.exceptions.RequestException as e:
        pytest.skip(f"OpenSearch is not running: {e}")


@pytest.fixture(scope="module")
def api_health(opensearch_health):
    """
    Verify Analytics API is running and healthy.
    """
    try:
        # Give API time to start if just launched
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(f"{API_BASE_URL}/health/", timeout=REQUEST_TIMEOUT)
                if response.status_code == 200:
                    health = response.json()
                    assert health["status"] in ["healthy", "partially_healthy"]
                    return health
            except requests.exceptions.ConnectionError:
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                raise

        pytest.skip("Analytics API is not responding")
    except requests.exceptions.RequestException as e:
        pytest.skip(f"Analytics API is not running: {e}")


# ============================================================================
# Health Check Integration Tests
# ============================================================================

class TestHealthIntegration:
    """Integration tests for health endpoints"""

    def test_health_endpoint_connectivity(self, api_health):
        """Test that health endpoint is accessible"""
        response = requests.get(f"{API_BASE_URL}/health/")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "environment" in data

    def test_liveness_probe_integration(self, api_health):
        """Test liveness probe is responsive"""
        response = requests.get(f"{API_BASE_URL}/health/liveness")

        assert response.status_code == 200
        assert response.json()["status"] == "alive"

    def test_readiness_probe_with_opensearch(self, api_health, opensearch_health):
        """Test readiness probe reflects OpenSearch connectivity"""
        response = requests.get(f"{API_BASE_URL}/health/readiness")

        # Should be ready since both API and OpenSearch are running
        assert response.status_code == 200
        assert response.json()["status"] == "ready"

    def test_cluster_health_integration(self, api_health, opensearch_health):
        """Test cluster health endpoint returns OpenSearch cluster info"""
        response = requests.get(f"{API_BASE_URL}/health/cluster")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "cluster_name" in data["data"]
        assert "number_of_nodes" in data["data"]


# ============================================================================
# Search Integration Tests
# ============================================================================

class TestSearchIntegration:
    """Integration tests for search endpoints"""

    def test_simple_search_integration(self, api_health):
        """Test simple search against live OpenSearch"""
        response = requests.get(
            f"{API_V1_URL}/search/simple",
            params={"q": "*", "size": 10}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "hits" in data["data"]
        assert "total" in data["data"]
        assert "pagination" in data["data"]

    def test_advanced_search_integration(self, api_health):
        """Test advanced search with POST request"""
        search_request = {
            "query": "level:ERROR",
            "indices": ["logs-*"],
            "size": 20,
            "from": 0
        }

        response = requests.post(
            f"{API_V1_URL}/search",
            json=search_request
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert isinstance(data["data"]["hits"], list)

    def test_search_with_time_range(self, api_health):
        """Test search with time range filter"""
        search_request = {
            "query": "*",
            "time_range": {
                "field": "@timestamp",
                "start": "now-7d",
                "end": "now"
            },
            "size": 50
        }

        response = requests.post(f"{API_V1_URL}/search", json=search_request)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_count_integration(self, api_health):
        """Test document count endpoint"""
        response = requests.get(
            f"{API_V1_URL}/search/count",
            params={"q": "*", "indices": "logs-*"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "count" in data["data"]
        assert isinstance(data["data"]["count"], int)


# ============================================================================
# Aggregation Integration Tests
# ============================================================================

class TestAggregationIntegration:
    """Integration tests for aggregation endpoints"""

    def test_terms_aggregation_integration(self, api_health):
        """Test terms aggregation against live data"""
        agg_request = {
            "query": "*",
            "indices": ["logs-*"],
            "agg_type": "terms",
            "field": "level",
            "size": 5
        }

        response = requests.post(f"{API_V1_URL}/aggregate", json=agg_request)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "buckets" in data["data"]
        assert len(data["data"]["buckets"]) > 0

    def test_date_histogram_integration(self, api_health):
        """Test date histogram aggregation"""
        agg_request = {
            "indices": ["logs-*"],
            "agg_type": "date_histogram",
            "field": "@timestamp",
            "interval": "1h"
        }

        response = requests.post(f"{API_V1_URL}/aggregate", json=agg_request)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "buckets" in data["data"]

    def test_top_values_integration(self, api_health):
        """Test top values convenience endpoint"""
        response = requests.get(
            f"{API_V1_URL}/top-values/service",
            params={"size": 5}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "buckets" in data["data"]


# ============================================================================
# Index Management Integration Tests
# ============================================================================

class TestIndexManagementIntegration:
    """Integration tests for index management endpoints"""

    def test_list_indices_integration(self, api_health):
        """Test listing indices from live OpenSearch"""
        response = requests.get(
            f"{API_V1_URL}/indices/",
            params={"pattern": "logs-*"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert isinstance(data["data"], list)

    def test_get_index_stats_integration(self, api_health):
        """Test getting index statistics"""
        # First get available indices
        list_response = requests.get(f"{API_V1_URL}/indices/", params={"pattern": "logs-*"})
        indices = list_response.json()["data"]

        if len(indices) > 0:
            index_name = indices[0]["index"]

            # Get stats for first index
            response = requests.get(f"{API_V1_URL}/indices/{index_name}/stats")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert index_name in data["data"]

    def test_get_index_mappings_integration(self, api_health):
        """Test getting index mappings"""
        # Get first available index
        list_response = requests.get(f"{API_V1_URL}/indices/", params={"pattern": "logs-*"})
        indices = list_response.json()["data"]

        if len(indices) > 0:
            index_name = indices[0]["index"]

            response = requests.get(f"{API_V1_URL}/indices/{index_name}/mappings")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert index_name in data["data"]

    def test_get_index_settings_integration(self, api_health):
        """Test getting index settings"""
        # Get first available index
        list_response = requests.get(f"{API_V1_URL}/indices/", params={"pattern": "logs-*"})
        indices = list_response.json()["data"]

        if len(indices) > 0:
            index_name = indices[0]["index"]

            response = requests.get(f"{API_V1_URL}/indices/{index_name}/settings")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert index_name in data["data"]


# ============================================================================
# End-to-End Workflow Tests
# ============================================================================

class TestEndToEndWorkflows:
    """Integration tests for complete workflows"""

    def test_search_to_aggregation_workflow(self, api_health):
        """Test complete workflow: search -> analyze results -> aggregate"""
        # Step 1: Search for errors
        search_response = requests.get(
            f"{API_V1_URL}/search/simple",
            params={"q": "level:ERROR", "size": 10}
        )
        assert search_response.status_code == 200

        # Step 2: Aggregate errors by service
        agg_response = requests.post(
            f"{API_V1_URL}/aggregate",
            json={
                "query": "level:ERROR",
                "agg_type": "terms",
                "field": "service",
                "size": 5
            }
        )
        assert agg_response.status_code == 200

        # Step 3: Verify data consistency
        search_data = search_response.json()["data"]
        agg_data = agg_response.json()["data"]

        assert search_data["total"] >= 0
        assert len(agg_data["buckets"]) >= 0

    def test_index_discovery_to_stats_workflow(self, api_health):
        """Test workflow: discover indices -> get stats -> analyze"""
        # Step 1: List all log indices
        list_response = requests.get(
            f"{API_V1_URL}/indices/",
            params={"pattern": "logs-*"}
        )
        assert list_response.status_code == 200
        indices = list_response.json()["data"]

        # Step 2: Get stats for each index
        total_docs = 0
        for index in indices[:3]:  # Limit to first 3 indices
            stats_response = requests.get(
                f"{API_V1_URL}/indices/{index['index']}/stats"
            )
            assert stats_response.status_code == 200

            index_stats = stats_response.json()["data"][index["index"]]
            total_docs += index_stats["total"]["docs"]["count"]

        assert total_docs >= 0


# ============================================================================
# Performance and Reliability Tests
# ============================================================================

class TestPerformanceAndReliability:
    """Integration tests for performance and reliability"""

    def test_api_response_time(self, api_health):
        """Test that API responses are reasonably fast"""
        start_time = time.time()

        response = requests.get(
            f"{API_V1_URL}/search/simple",
            params={"q": "*", "size": 10}
        )

        elapsed_time = (time.time() - start_time) * 1000  # Convert to ms

        assert response.status_code == 200
        assert elapsed_time < 1000  # Should respond within 1 second

    def test_concurrent_requests(self, api_health):
        """Test API handles concurrent requests"""
        import concurrent.futures

        def make_request():
            return requests.get(f"{API_V1_URL}/search/simple", params={"q": "*", "size": 5})

        # Make 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All requests should succeed
        assert all(r.status_code == 200 for r in results)

    def test_large_result_set_handling(self, api_health):
        """Test API handles large result sets"""
        response = requests.get(
            f"{API_V1_URL}/search/simple",
            params={"q": "*", "size": 1000}  # Large page size
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
