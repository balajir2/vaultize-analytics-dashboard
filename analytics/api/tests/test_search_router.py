"""
Unit Tests for Search Router

Tests search endpoints including simple search, advanced search,
and count operations.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import status
from opensearchpy import exceptions as os_exceptions


class TestSimpleSearch:
    """Test simple search endpoint"""

    @patch('app.routers.search.get_opensearch')
    def test_simple_search_success(self, mock_get_os, test_client, sample_search_response):
        """Test GET /search/simple with valid query"""
        mock_client = MagicMock()
        mock_client.search.return_value = sample_search_response
        mock_get_os.return_value = mock_client

        response = test_client.get(
            "/api/v1/search/simple",
            params={"q": "level:ERROR", "size": 10}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "hits" in data["data"]
        assert "total" in data["data"]
        assert data["data"]["total"] == 100

    @patch('app.routers.search.get_opensearch')
    def test_simple_search_default_params(self, mock_get_os, test_client, sample_search_response):
        """Test simple search with default parameters"""
        mock_client = MagicMock()
        mock_client.search.return_value = sample_search_response
        mock_get_os.return_value = mock_client

        response = test_client.get("/api/v1/search/simple", params={"q": "*"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"

    @patch('app.routers.search.get_opensearch')
    def test_simple_search_invalid_query(self, mock_get_os, test_client):
        """Test simple search with invalid query syntax"""
        mock_client = MagicMock()
        mock_client.search.side_effect = os_exceptions.RequestError(
            400, "parsing_exception", {"error": "Invalid query"}
        )
        mock_get_os.return_value = mock_client

        response = test_client.get(
            "/api/v1/search/simple",
            params={"q": "level:[INVALID"}
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch('app.routers.search.get_opensearch')
    def test_simple_search_multiple_indices(self, mock_get_os, test_client, sample_search_response):
        """Test simple search across multiple indices"""
        mock_client = MagicMock()
        mock_client.search.return_value = sample_search_response
        mock_get_os.return_value = mock_client

        response = test_client.get(
            "/api/v1/search/simple",
            params={"q": "level:ERROR", "indices": "logs-2026-02-04,logs-2026-02-03"}
        )

        assert response.status_code == status.HTTP_200_OK


class TestAdvancedSearch:
    """Test advanced search endpoint"""

    @patch('app.routers.search.get_opensearch')
    def test_advanced_search_post(self, mock_get_os, test_client, sample_search_response):
        """Test POST /search with request body"""
        mock_client = MagicMock()
        mock_client.search.return_value = sample_search_response
        mock_get_os.return_value = mock_client

        search_request = {
            "query": "level:ERROR",
            "indices": ["logs-*"],
            "size": 50,
            "from": 0
        }

        response = test_client.post("/api/v1/search", json=search_request)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]["hits"]) > 0

    @patch('app.routers.search.get_opensearch')
    def test_advanced_search_with_time_range(self, mock_get_os, test_client, sample_search_response):
        """Test advanced search with time range filter"""
        mock_client = MagicMock()
        mock_client.search.return_value = sample_search_response
        mock_get_os.return_value = mock_client

        search_request = {
            "query": "level:ERROR",
            "time_range": {
                "field": "@timestamp",
                "start": "now-24h",
                "end": "now"
            },
            "size": 100
        }

        response = test_client.post("/api/v1/search", json=search_request)

        assert response.status_code == status.HTTP_200_OK
        # Verify the search was called with time range in query
        mock_client.search.assert_called_once()

    @patch('app.routers.search.get_opensearch')
    def test_advanced_search_with_fields(self, mock_get_os, test_client, sample_search_response):
        """Test advanced search with specific fields"""
        mock_client = MagicMock()
        mock_client.search.return_value = sample_search_response
        mock_get_os.return_value = mock_client

        search_request = {
            "query": "*",
            "fields": ["@timestamp", "level", "message"],
            "size": 10
        }

        response = test_client.post("/api/v1/search", json=search_request)

        assert response.status_code == status.HTTP_200_OK

    @patch('app.routers.search.get_opensearch')
    def test_advanced_search_with_sort(self, mock_get_os, test_client, sample_search_response):
        """Test advanced search with custom sorting"""
        mock_client = MagicMock()
        mock_client.search.return_value = sample_search_response
        mock_get_os.return_value = mock_client

        search_request = {
            "query": "level:ERROR",
            "sort": [{"@timestamp": "asc"}, {"_score": "desc"}],
            "size": 20
        }

        response = test_client.post("/api/v1/search", json=search_request)

        assert response.status_code == status.HTTP_200_OK

    @patch('app.routers.search.get_opensearch')
    def test_advanced_search_pagination(self, mock_get_os, test_client, sample_search_response):
        """Test advanced search with pagination"""
        mock_client = MagicMock()
        mock_client.search.return_value = sample_search_response
        mock_get_os.return_value = mock_client

        search_request = {
            "query": "*",
            "size": 25,
            "from": 50  # Page 3 with size 25
        }

        response = test_client.post("/api/v1/search", json=search_request)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "pagination" in data["data"]


class TestCountEndpoint:
    """Test count endpoint"""

    @patch('app.routers.search.get_opensearch')
    def test_count_documents(self, mock_get_os, test_client):
        """Test GET /search/count returns document count"""
        mock_client = MagicMock()
        mock_client.count.return_value = {"count": 1500}
        mock_get_os.return_value = mock_client

        response = test_client.get(
            "/api/v1/search/count",
            params={"q": "level:ERROR"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["count"] == 1500

    @patch('app.routers.search.get_opensearch')
    def test_count_with_index_pattern(self, mock_get_os, test_client):
        """Test count with specific index pattern"""
        mock_client = MagicMock()
        mock_client.count.return_value = {"count": 750}
        mock_get_os.return_value = mock_client

        response = test_client.get(
            "/api/v1/search/count",
            params={"q": "*", "indices": "logs-2026-02-04"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["count"] == 750


class TestSearchQueryBuilder:
    """Test search query building logic"""

    @patch('app.routers.search.get_opensearch')
    def test_query_builder_match_all(self, mock_get_os, test_client, sample_search_response):
        """Test query builder with match_all for empty query"""
        mock_client = MagicMock()
        mock_client.search.return_value = sample_search_response
        mock_get_os.return_value = mock_client

        search_request = {"query": None, "size": 10}

        response = test_client.post("/api/v1/search", json=search_request)

        assert response.status_code == status.HTTP_200_OK

    @patch('app.routers.search.get_opensearch')
    def test_query_builder_with_query_string(self, mock_get_os, test_client, sample_search_response):
        """Test query builder with query_string"""
        mock_client = MagicMock()
        mock_client.search.return_value = sample_search_response
        mock_get_os.return_value = mock_client

        search_request = {
            "query": "service:api-service AND level:ERROR",
            "size": 10
        }

        response = test_client.post("/api/v1/search", json=search_request)

        assert response.status_code == status.HTTP_200_OK


class TestErrorHandling:
    """Test error handling in search endpoints"""

    @patch('app.routers.search.get_opensearch')
    def test_index_not_found(self, mock_get_os, test_client):
        """Test handling of non-existent index"""
        mock_client = MagicMock()
        mock_client.search.side_effect = os_exceptions.NotFoundError(
            404, "index_not_found_exception", {"error": "no such index"}
        )
        mock_get_os.return_value = mock_client

        response = test_client.get(
            "/api/v1/search/simple",
            params={"q": "*", "indices": "nonexistent-index"}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch('app.routers.search.get_opensearch')
    def test_opensearch_connection_error(self, mock_get_os, test_client):
        """Test handling of OpenSearch connection errors"""
        mock_client = MagicMock()
        mock_client.search.side_effect = os_exceptions.ConnectionError(
            "N/A", "Connection refused", None
        )
        mock_get_os.return_value = mock_client

        response = test_client.get("/api/v1/search/simple", params={"q": "*"})

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
