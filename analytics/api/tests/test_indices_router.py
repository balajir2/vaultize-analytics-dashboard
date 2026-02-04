"""
Unit Tests for Indices Router

Tests index management endpoints including stats, mappings,
settings, and deletion operations.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import status
from opensearchpy import exceptions as os_exceptions


class TestIndexStats:
    """Test index statistics endpoint"""

    @patch('app.routers.indices.get_opensearch')
    def test_get_index_stats_single_index(self, mock_get_os, test_client, mock_opensearch_client):
        """Test GET /indices/{name}/stats for single index"""
        mock_get_os.return_value = mock_opensearch_client

        response = test_client.get("/api/v1/indices/logs-2026-02-04/stats")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert "logs-2026-02-04" in data["data"]
        assert "total" in data["data"]["logs-2026-02-04"]
        assert "primaries" in data["data"]["logs-2026-02-04"]

    @patch('app.routers.indices.get_opensearch')
    def test_get_index_stats_pattern(self, mock_get_os, test_client):
        """Test index stats with wildcard pattern"""
        mock_client = MagicMock()
        mock_client.indices.stats.return_value = {
            "indices": {
                "logs-2026-02-04": {
                    "total": {"docs": {"count": 1000, "deleted": 0}, "store": {"size_in_bytes": 1048576}},
                    "primaries": {"docs": {"count": 1000}, "store": {"size_in_bytes": 524288}}
                },
                "logs-2026-02-03": {
                    "total": {"docs": {"count": 800, "deleted": 0}, "store": {"size_in_bytes": 838860}},
                    "primaries": {"docs": {"count": 800}, "store": {"size_in_bytes": 419430}}
                }
            }
        }
        mock_get_os.return_value = mock_client

        response = test_client.get("/api/v1/indices/logs-*/stats")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 2

    @patch('app.routers.indices.get_opensearch')
    def test_get_index_stats_not_found(self, mock_get_os, test_client):
        """Test index stats for non-existent index"""
        mock_client = MagicMock()
        mock_client.indices.stats.side_effect = os_exceptions.NotFoundError(
            404, "index_not_found_exception", {}
        )
        mock_get_os.return_value = mock_client

        response = test_client.get("/api/v1/indices/nonexistent-index/stats")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestIndexMappings:
    """Test index mappings endpoint"""

    @patch('app.routers.indices.get_opensearch')
    def test_get_index_mappings(self, mock_get_os, test_client, mock_opensearch_client):
        """Test GET /indices/{name}/mappings"""
        mock_get_os.return_value = mock_opensearch_client

        response = test_client.get("/api/v1/indices/logs-2026-02-04/mappings")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert "logs-2026-02-04" in data["data"]

    @patch('app.routers.indices.get_opensearch')
    def test_get_index_mappings_not_found(self, mock_get_os, test_client):
        """Test mappings for non-existent index"""
        mock_client = MagicMock()
        mock_client.indices.get_mapping.side_effect = os_exceptions.NotFoundError(
            404, "index_not_found_exception", {}
        )
        mock_get_os.return_value = mock_client

        response = test_client.get("/api/v1/indices/nonexistent/mappings")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestIndexSettings:
    """Test index settings endpoint"""

    @patch('app.routers.indices.get_opensearch')
    def test_get_index_settings(self, mock_get_os, test_client):
        """Test GET /indices/{name}/settings"""
        mock_client = MagicMock()
        mock_client.indices.get_settings.return_value = {
            "logs-2026-02-04": {
                "settings": {
                    "index": {
                        "number_of_shards": "3",
                        "number_of_replicas": "1",
                        "refresh_interval": "1s"
                    }
                }
            }
        }
        mock_get_os.return_value = mock_client

        response = test_client.get("/api/v1/indices/logs-2026-02-04/settings")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert "logs-2026-02-04" in data["data"]

    @patch('app.routers.indices.get_opensearch')
    def test_get_index_settings_not_found(self, mock_get_os, test_client):
        """Test settings for non-existent index"""
        mock_client = MagicMock()
        mock_client.indices.get_settings.side_effect = os_exceptions.NotFoundError(
            404, "index_not_found_exception", {}
        )
        mock_get_os.return_value = mock_client

        response = test_client.get("/api/v1/indices/nonexistent/settings")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteIndex:
    """Test index deletion endpoint"""

    @patch('app.routers.indices.get_opensearch')
    def test_delete_index_success(self, mock_get_os, test_client):
        """Test DELETE /indices/{name} successful deletion"""
        mock_client = MagicMock()
        mock_client.indices.delete.return_value = {"acknowledged": True}
        mock_get_os.return_value = mock_client

        response = test_client.delete("/api/v1/indices/test-index-to-delete")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert "deleted successfully" in data["message"]

    @patch('app.routers.indices.get_opensearch')
    def test_delete_index_wildcards_rejected(self, mock_get_os, test_client):
        """Test deletion rejects wildcard patterns for safety"""
        mock_client = MagicMock()
        mock_get_os.return_value = mock_client

        # Test with asterisk
        response = test_client.delete("/api/v1/indices/logs-*")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Wildcards not allowed" in response.json()["detail"]

        # Test with question mark
        response = test_client.delete("/api/v1/indices/logs-?")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Ensure delete was never called
        mock_client.indices.delete.assert_not_called()

    @patch('app.routers.indices.get_opensearch')
    def test_delete_index_not_found(self, mock_get_os, test_client):
        """Test deletion of non-existent index"""
        mock_client = MagicMock()
        mock_client.indices.delete.side_effect = os_exceptions.NotFoundError(
            404, "index_not_found_exception", {}
        )
        mock_get_os.return_value = mock_client

        response = test_client.delete("/api/v1/indices/nonexistent-index")

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestListIndices:
    """Test list indices endpoint"""

    @patch('app.routers.indices.get_opensearch')
    def test_list_all_indices(self, mock_get_os, test_client, mock_opensearch_client):
        """Test GET /indices/ lists all indices"""
        mock_get_os.return_value = mock_opensearch_client

        response = test_client.get("/api/v1/indices/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0

    @patch('app.routers.indices.get_opensearch')
    def test_list_indices_with_pattern(self, mock_get_os, test_client):
        """Test listing indices with pattern filter"""
        mock_client = MagicMock()
        mock_client.cat.indices.return_value = [
            {"index": "logs-2026-02-04", "health": "green", "status": "open", "docs.count": "1000"},
            {"index": "logs-2026-02-03", "health": "green", "status": "open", "docs.count": "800"}
        ]
        mock_get_os.return_value = mock_client

        response = test_client.get("/api/v1/indices/", params={"pattern": "logs-*"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["data"]) == 2
        assert all("logs-" in idx["index"] for idx in data["data"])

    @patch('app.routers.indices.get_opensearch')
    def test_list_indices_filter_by_health(self, mock_get_os, test_client):
        """Test listing indices filtered by health status"""
        mock_client = MagicMock()
        mock_client.cat.indices.return_value = [
            {"index": "logs-2026-02-04", "health": "green", "status": "open"},
            {"index": "logs-2026-02-03", "health": "yellow", "status": "open"},
            {"index": "logs-2026-02-02", "health": "green", "status": "open"}
        ]
        mock_get_os.return_value = mock_client

        response = test_client.get("/api/v1/indices/", params={"health": "green"})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should only return green indices (filtering happens in endpoint)
        assert all(idx["health"] == "green" for idx in data["data"])

    @patch('app.routers.indices.get_opensearch')
    def test_list_indices_sorted_by_name(self, mock_get_os, test_client):
        """Test indices are sorted by name"""
        mock_client = MagicMock()
        mock_client.cat.indices.return_value = [
            {"index": "logs-2026-02-03", "health": "green"},
            {"index": "logs-2026-02-04", "health": "green"},
            {"index": "logs-2026-02-02", "health": "green"}
        ]
        mock_get_os.return_value = mock_client

        response = test_client.get("/api/v1/indices/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Verify sorting
        indices = [idx["index"] for idx in data["data"]]
        assert indices == sorted(indices)


class TestIndexEndpointsErrorHandling:
    """Test error handling across index endpoints"""

    @patch('app.routers.indices.get_opensearch')
    def test_opensearch_connection_error(self, mock_get_os, test_client):
        """Test handling of OpenSearch connection errors"""
        mock_client = MagicMock()
        mock_client.indices.stats.side_effect = os_exceptions.ConnectionError(
            "N/A", "Connection refused", None
        )
        mock_get_os.return_value = mock_client

        response = test_client.get("/api/v1/indices/logs-*/stats")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    @patch('app.routers.indices.get_opensearch')
    def test_generic_exception_handling(self, mock_get_os, test_client):
        """Test handling of unexpected exceptions"""
        mock_client = MagicMock()
        mock_client.indices.stats.side_effect = Exception("Unexpected error")
        mock_get_os.return_value = mock_client

        response = test_client.get("/api/v1/indices/logs-2026-02-04/stats")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
