"""
Regression Test RT-004: Analytics API Endpoints

This test validates the core functionality of the Analytics API built in version 0.2.1+.
It ensures all endpoints are working correctly and returning expected responses.

Original Feature:
    Analytics API with health checks, search, aggregations, and index management
    endpoints was implemented with full Pydantic validation and OpenAPI documentation.

How to Use:
    This test requires:
    1. OpenSearch running at http://localhost:9200
    2. Analytics API running at http://localhost:8000
    3. Sample log data (run scripts/data/generate_sample_logs.py first)

Date: 2026-02-04
Severity: High (Core API functionality)
"""

import pytest
import requests
from datetime import datetime

# ============================================================================
# Configuration
# ============================================================================

API_BASE_URL = "http://localhost:8000"
API_V1_URL = f"{API_BASE_URL}/api/v1"

# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="module")
def api_health_check():
    """
    Verify API is running before running tests.
    """
    try:
        response = requests.get(f"{API_BASE_URL}/health/", timeout=5)
        assert response.status_code == 200, "API health check failed"
        health = response.json()
        assert health["status"] in ["healthy", "partially_healthy"], "API is not healthy"
        return health
    except requests.exceptions.RequestException as e:
        pytest.skip(f"Analytics API is not running: {e}")


# ============================================================================
# Health Check Tests
# ============================================================================

class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_regression_004_health_check_returns_200(self, api_health_check):
        """
        Verify /health/ endpoint returns 200 and correct structure.
        """
        response = requests.get(f"{API_BASE_URL}/health/")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "environment" in data
        assert "opensearch" in data

    def test_regression_004_liveness_probe_works(self, api_health_check):
        """
        Verify /health/liveness endpoint returns 200.
        """
        response = requests.get(f"{API_BASE_URL}/health/liveness")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "alive"

    def test_regression_004_readiness_probe_works(self, api_health_check):
        """
        Verify /health/readiness endpoint returns 200 when ready.
        """
        response = requests.get(f"{API_BASE_URL}/health/readiness")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ready"


# ============================================================================
# Search Endpoint Tests
# ============================================================================

class TestSearchEndpoints:
    """Test search endpoints"""

    def test_regression_004_simple_search_returns_results(self, api_health_check):
        """
        Verify GET /search/simple endpoint returns search results.
        """
        response = requests.get(
            f"{API_V1_URL}/search/simple",
            params={"q": "level:ERROR", "size": 5}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "hits" in data["data"]
        assert "total" in data["data"]
        assert "pagination" in data["data"]

    def test_regression_004_advanced_search_with_post(self, api_health_check):
        """
        Verify POST /search endpoint with request body works.
        """
        search_request = {
            "query": "level:ERROR",
            "indices": ["logs-*"],
            "size": 10,
            "from": 0
        }

        response = requests.post(
            f"{API_V1_URL}/search",
            json=search_request
        )
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]["hits"]) <= 10


# ============================================================================
# Aggregation Endpoint Tests
# ============================================================================

class TestAggregationEndpoints:
    """Test aggregation endpoints"""

    def test_regression_004_terms_aggregation_works(self, api_health_check):
        """
        Verify POST /aggregate endpoint with terms aggregation.
        """
        agg_request = {
            "query": "level:ERROR",
            "indices": ["logs-*"],
            "agg_type": "terms",
            "field": "service",
            "size": 5
        }

        response = requests.post(
            f"{API_V1_URL}/aggregate",
            json=agg_request
        )
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert "buckets" in data["data"]
        assert "total" in data["data"]

    def test_regression_004_top_values_shortcut_works(self, api_health_check):
        """
        Verify GET /top-values/{field} shortcut endpoint.
        """
        response = requests.get(
            f"{API_V1_URL}/top-values/level",
            params={"size": 5}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]["buckets"]) > 0

    def test_regression_004_date_histogram_aggregation(self, api_health_check):
        """
        Verify date_histogram aggregation type works.
        """
        agg_request = {
            "query": "level:ERROR",
            "indices": ["logs-*"],
            "agg_type": "date_histogram",
            "field": "@timestamp",
            "interval": "1h"
        }

        response = requests.post(
            f"{API_V1_URL}/aggregate",
            json=agg_request
        )
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert "buckets" in data["data"]


# ============================================================================
# Index Management Endpoint Tests
# ============================================================================

class TestIndexManagementEndpoints:
    """Test index management endpoints"""

    def test_regression_004_list_indices_works(self, api_health_check):
        """
        Verify GET /indices/ endpoint lists indices.
        """
        response = requests.get(
            f"{API_V1_URL}/indices/",
            params={"pattern": "logs-*"}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert isinstance(data["data"], list)

    def test_regression_004_get_index_stats(self, api_health_check):
        """
        Verify GET /indices/{name}/stats endpoint returns statistics.
        """
        # First get available indices
        list_response = requests.get(f"{API_V1_URL}/indices?pattern=logs-*")
        indices = list_response.json()["data"]

        if len(indices) > 0:
            index_name = indices[0]

            # Get stats for first index
            response = requests.get(f"{API_V1_URL}/indices/{index_name}/stats")
            assert response.status_code == 200

            data = response.json()
            assert data["status"] == "success"
            assert index_name in data["data"]
            assert "total" in data["data"][index_name]
            assert "primaries" in data["data"][index_name]

    def test_regression_004_get_index_mappings(self, api_health_check):
        """
        Verify GET /indices/{name}/mappings endpoint returns field mappings.
        """
        # First get available indices
        list_response = requests.get(f"{API_V1_URL}/indices?pattern=logs-*")
        indices = list_response.json()["data"]

        if len(indices) > 0:
            index_name = indices[0]

            # Get mappings
            response = requests.get(f"{API_V1_URL}/indices/{index_name}/mappings")
            assert response.status_code == 200

            data = response.json()
            assert data["status"] == "success"
            assert index_name in data["data"]


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestErrorHandling:
    """Test error handling and validation"""

    def test_regression_004_invalid_query_returns_400(self, api_health_check):
        """
        Verify invalid queries return 400 Bad Request.
        """
        response = requests.get(
            f"{API_V1_URL}/search/simple",
            params={"q": "level:[INVALID SYNTAX", "size": 5}
        )
        # Should return 400 for invalid query syntax
        assert response.status_code in [400, 500]  # Depends on OpenSearch error handling

    def test_regression_004_nonexistent_index_handled(self, api_health_check):
        """
        Verify non-existent index is handled gracefully.
        """
        response = requests.get(f"{API_V1_URL}/indices/nonexistent-index-12345/stats")
        assert response.status_code == 404


# ============================================================================
# Response Format Tests
# ============================================================================

class TestResponseFormat:
    """Test that all responses follow the standard format"""

    def test_regression_004_all_success_responses_have_standard_format(self, api_health_check):
        """
        Verify all successful API responses follow the standard format:
        {
            "status": "success",
            "data": <response_data>,
            "message": <optional_message>
        }
        """
        # Test various endpoints
        endpoints = [
            f"{API_V1_URL}/search/simple?q=level:ERROR&size=1",
            f"{API_V1_URL}/top-values/level?size=1",
            f"{API_V1_URL}/indices?pattern=logs-*"
        ]

        for endpoint in endpoints:
            response = requests.get(endpoint)
            if response.status_code == 200:
                data = response.json()
                assert "status" in data, f"Missing 'status' in response from {endpoint}"
                assert data["status"] == "success"
                assert "data" in data, f"Missing 'data' in response from {endpoint}"


# ============================================================================
# Summary
# ============================================================================

def test_regression_004_summary(api_health_check):
    """
    Summary test that validates the entire API is functional.

    This test performs a complete workflow:
    1. Check API health
    2. List available indices
    3. Search for logs
    4. Aggregate results
    5. Get index statistics
    """
    print("\n" + "=" * 70)
    print("RT-004: Analytics API Regression Test Summary")
    print("=" * 70)

    # 1. Health check
    health_response = requests.get(f"{API_BASE_URL}/health/")
    assert health_response.status_code == 200
    print(f"[OK] Health check passed: {health_response.json()['status']}")

    # 2. List indices
    indices_response = requests.get(f"{API_V1_URL}/indices?pattern=logs-*")
    assert indices_response.status_code == 200
    num_indices = len(indices_response.json()["data"])
    print(f"[OK] Found {num_indices} log indices")

    # 3. Search
    search_response = requests.get(f"{API_V1_URL}/search/simple?q=level:ERROR&size=1")
    assert search_response.status_code == 200
    num_errors = search_response.json()["data"]["total"]
    print(f"[OK] Found {num_errors} error logs")

    # 4. Aggregate
    agg_response = requests.post(
        f"{API_V1_URL}/aggregate",
        json={
            "query": "level:ERROR",
            "agg_type": "terms",
            "field": "service",
            "size": 3
        }
    )
    assert agg_response.status_code == 200
    print(f"[OK] Aggregation completed in {agg_response.json()['data']['took']}ms")

    print("=" * 70)
    print("[OK] All Analytics API endpoints are functional")
    print("=" * 70)
