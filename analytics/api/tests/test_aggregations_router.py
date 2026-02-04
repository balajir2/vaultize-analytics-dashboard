"""
Unit Tests for Aggregations Router

Tests aggregation endpoints including terms, date_histogram,
stats, and cardinality aggregations.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import status
from opensearchpy import exceptions as os_exceptions


class TestAggregateEndpoint:
    """Test /aggregate endpoint"""

    @patch('app.routers.aggregations.get_opensearch')
    def test_terms_aggregation(self, mock_get_os, test_client, sample_aggregation_response):
        """Test terms aggregation for top values"""
        mock_client = MagicMock()
        mock_client.search.return_value = sample_aggregation_response
        mock_get_os.return_value = mock_client

        agg_request = {
            "query": "level:ERROR",
            "indices": ["logs-*"],
            "agg_type": "terms",
            "field": "service",
            "size": 5
        }

        response = test_client.post("/api/v1/aggregate", json=agg_request)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert "buckets" in data["data"]
        assert len(data["data"]["buckets"]) > 0
        assert data["data"]["buckets"][0]["key"] == "api-service"

    @patch('app.routers.aggregations.get_opensearch')
    def test_date_histogram_aggregation(self, mock_get_os, test_client):
        """Test date_histogram aggregation for time series"""
        mock_client = MagicMock()
        mock_client.search.return_value = {
            "took": 15,
            "hits": {"total": {"value": 500}},
            "aggregations": {
                "results": {
                    "buckets": [
                        {"key": 1707062400000, "key_as_string": "2026-02-04T10:00:00Z", "doc_count": 100},
                        {"key": 1707066000000, "key_as_string": "2026-02-04T11:00:00Z", "doc_count": 150}
                    ]
                }
            }
        }
        mock_get_os.return_value = mock_client

        agg_request = {
            "query": "level:ERROR",
            "indices": ["logs-*"],
            "agg_type": "date_histogram",
            "field": "@timestamp",
            "interval": "1h"
        }

        response = test_client.post("/api/v1/aggregate", json=agg_request)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]["buckets"]) == 2

    @patch('app.routers.aggregations.get_opensearch')
    def test_stats_aggregation(self, mock_get_os, test_client):
        """Test stats aggregation for numeric analysis"""
        mock_client = MagicMock()
        mock_client.search.return_value = {
            "took": 8,
            "hits": {"total": {"value": 1000}},
            "aggregations": {
                "results": {
                    "count": 1000,
                    "min": 10.0,
                    "max": 5000.0,
                    "avg": 250.5,
                    "sum": 250500.0
                }
            }
        }
        mock_get_os.return_value = mock_client

        agg_request = {
            "indices": ["logs-*"],
            "agg_type": "stats",
            "field": "duration_ms"
        }

        response = test_client.post("/api/v1/aggregate", json=agg_request)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["buckets"][0]["data"]["avg"] == 250.5

    @patch('app.routers.aggregations.get_opensearch')
    def test_cardinality_aggregation(self, mock_get_os, test_client):
        """Test cardinality aggregation for unique count"""
        mock_client = MagicMock()
        mock_client.search.return_value = {
            "took": 5,
            "hits": {"total": {"value": 1000}},
            "aggregations": {
                "results": {
                    "value": 42  # 42 unique users
                }
            }
        }
        mock_get_os.return_value = mock_client

        agg_request = {
            "indices": ["logs-*"],
            "agg_type": "cardinality",
            "field": "user"
        }

        response = test_client.post("/api/v1/aggregate", json=agg_request)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["buckets"][0]["doc_count"] == 42

    @patch('app.routers.aggregations.get_opensearch')
    def test_aggregation_with_time_range(self, mock_get_os, test_client, sample_aggregation_response):
        """Test aggregation with time range filter"""
        mock_client = MagicMock()
        mock_client.search.return_value = sample_aggregation_response
        mock_get_os.return_value = mock_client

        agg_request = {
            "query": "level:ERROR",
            "indices": ["logs-*"],
            "agg_type": "terms",
            "field": "service",
            "time_range": {
                "field": "@timestamp",
                "start": "now-24h",
                "end": "now"
            },
            "size": 10
        }

        response = test_client.post("/api/v1/aggregate", json=agg_request)

        assert response.status_code == status.HTTP_200_OK

    @patch('app.routers.aggregations.get_opensearch')
    def test_aggregation_without_query(self, mock_get_os, test_client, sample_aggregation_response):
        """Test aggregation without filter query (match_all)"""
        mock_client = MagicMock()
        mock_client.search.return_value = sample_aggregation_response
        mock_get_os.return_value = mock_client

        agg_request = {
            "indices": ["logs-*"],
            "agg_type": "terms",
            "field": "level"
        }

        response = test_client.post("/api/v1/aggregate", json=agg_request)

        assert response.status_code == status.HTTP_200_OK


class TestTopValuesEndpoint:
    """Test /top-values/{field} convenience endpoint"""

    @patch('app.routers.aggregations.get_opensearch')
    def test_top_values_get_request(self, mock_get_os, test_client, sample_aggregation_response):
        """Test GET /top-values/{field} shortcut"""
        mock_client = MagicMock()
        mock_client.search.return_value = sample_aggregation_response
        mock_get_os.return_value = mock_client

        response = test_client.get("/api/v1/top-values/level", params={"size": 5})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert "buckets" in data["data"]

    @patch('app.routers.aggregations.get_opensearch')
    def test_top_values_with_query_filter(self, mock_get_os, test_client, sample_aggregation_response):
        """Test top values with query filter"""
        mock_client = MagicMock()
        mock_client.search.return_value = sample_aggregation_response
        mock_get_os.return_value = mock_client

        response = test_client.get(
            "/api/v1/top-values/service",
            params={"query": "level:ERROR", "size": 10}
        )

        assert response.status_code == status.HTTP_200_OK

    @patch('app.routers.aggregations.get_opensearch')
    def test_top_values_multiple_indices(self, mock_get_os, test_client, sample_aggregation_response):
        """Test top values across multiple indices"""
        mock_client = MagicMock()
        mock_client.search.return_value = sample_aggregation_response
        mock_get_os.return_value = mock_client

        response = test_client.get(
            "/api/v1/top-values/host",
            params={"indices": "logs-2026-02-04,logs-2026-02-03", "size": 5}
        )

        assert response.status_code == status.HTTP_200_OK


class TestAggregationValidation:
    """Test aggregation request validation"""

    def test_date_histogram_requires_interval(self, test_client):
        """Test date_histogram validation requires interval"""
        agg_request = {
            "indices": ["logs-*"],
            "agg_type": "date_histogram",
            "field": "@timestamp"
            # Missing interval
        }

        response = test_client.post("/api/v1/aggregate", json=agg_request)

        # Should fail validation or return error
        assert response.status_code in [400, 422]

    @patch('app.routers.aggregations.get_opensearch')
    def test_unsupported_aggregation_type(self, mock_get_os, test_client):
        """Test unsupported aggregation type returns error"""
        mock_client = MagicMock()
        mock_get_os.return_value = mock_client

        agg_request = {
            "indices": ["logs-*"],
            "agg_type": "unsupported_type",
            "field": "service"
        }

        response = test_client.post("/api/v1/aggregate", json=agg_request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestAggregationErrorHandling:
    """Test error handling in aggregation endpoints"""

    @patch('app.routers.aggregations.get_opensearch')
    def test_invalid_field_error(self, mock_get_os, test_client):
        """Test handling of invalid field for aggregation"""
        mock_client = MagicMock()
        mock_client.search.side_effect = os_exceptions.RequestError(
            400, "illegal_argument_exception", {"error": "Field not found"}
        )
        mock_get_os.return_value = mock_client

        agg_request = {
            "indices": ["logs-*"],
            "agg_type": "terms",
            "field": "nonexistent_field"
        }

        response = test_client.post("/api/v1/aggregate", json=agg_request)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch('app.routers.aggregations.get_opensearch')
    def test_index_not_found(self, mock_get_os, test_client):
        """Test handling of non-existent index"""
        mock_client = MagicMock()
        mock_client.search.side_effect = os_exceptions.NotFoundError(
            404, "index_not_found_exception", {}
        )
        mock_get_os.return_value = mock_client

        agg_request = {
            "indices": ["nonexistent-*"],
            "agg_type": "terms",
            "field": "service"
        }

        response = test_client.post("/api/v1/aggregate", json=agg_request)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch('app.routers.aggregations.get_opensearch')
    def test_opensearch_connection_error(self, mock_get_os, test_client):
        """Test handling of OpenSearch connection errors"""
        mock_client = MagicMock()
        mock_client.search.side_effect = os_exceptions.ConnectionError(
            "N/A", "Connection refused", None
        )
        mock_get_os.return_value = mock_client

        agg_request = {
            "indices": ["logs-*"],
            "agg_type": "terms",
            "field": "service"
        }

        response = test_client.post("/api/v1/aggregate", json=agg_request)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
