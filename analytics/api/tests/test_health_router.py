"""
Unit Tests for Health Router

Tests all health check endpoints including liveness, readiness,
and cluster health monitoring.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import status
from opensearchpy import exceptions as os_exceptions


class TestHealthEndpoints:
    """Test health check endpoints"""

    @patch('app.routers.health.get_opensearch')
    def test_health_check_healthy(self, mock_get_os, test_client, mock_opensearch_client):
        """Test /health/ returns healthy status when OpenSearch is up"""
        mock_get_os.return_value = mock_opensearch_client

        response = test_client.get("/health/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] in ["healthy", "partially_healthy"]
        assert "version" in data
        assert "environment" in data
        assert "opensearch" in data
        assert data["opensearch"]["status"] == "green"

    @patch('app.routers.health.get_opensearch')
    def test_health_check_opensearch_down(self, mock_get_os, test_client):
        """Test /health/ returns degraded when OpenSearch is down"""
        mock_client = MagicMock()
        mock_client.cluster.health.side_effect = Exception("Connection refused")
        mock_get_os.return_value = mock_client

        response = test_client.get("/health/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "degraded"
        assert data["opensearch"] is None

    @patch('app.routers.health.get_opensearch')
    def test_health_check_yellow_cluster(self, mock_get_os, test_client):
        """Test /health/ returns partially_healthy for yellow cluster"""
        mock_client = MagicMock()
        mock_client.cluster.health.return_value = {
            "cluster_name": "test",
            "status": "yellow",
            "number_of_nodes": 1
        }
        mock_get_os.return_value = mock_client

        response = test_client.get("/health/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "partially_healthy"
        assert data["opensearch"]["status"] == "yellow"


class TestLivenessProbe:
    """Test liveness probe endpoint"""

    def test_liveness_check_always_alive(self, test_client):
        """Test /health/liveness always returns alive"""
        response = test_client.get("/health/liveness")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "alive"

    def test_liveness_check_no_dependencies(self, test_client):
        """Test liveness check doesn't depend on external services"""
        # This should succeed even if OpenSearch is down
        response = test_client.get("/health/liveness")

        assert response.status_code == status.HTTP_200_OK


class TestReadinessProbe:
    """Test readiness probe endpoint"""

    @patch('app.routers.health.get_opensearch')
    def test_readiness_check_ready(self, mock_get_os, test_client, mock_opensearch_client):
        """Test /health/readiness returns ready when OpenSearch is up"""
        mock_get_os.return_value = mock_opensearch_client

        response = test_client.get("/health/readiness")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "ready"

    @patch('app.routers.health.get_opensearch')
    def test_readiness_check_not_ready(self, mock_get_os, test_client):
        """Test /health/readiness returns not ready when OpenSearch is down"""
        mock_client = MagicMock()
        mock_client.cluster.health.side_effect = Exception("Connection refused")
        mock_get_os.return_value = mock_client

        response = test_client.get("/health/readiness")

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        data = response.json()
        assert data["status"] == "not_ready"


class TestClusterHealthEndpoint:
    """Test cluster health endpoint"""

    @patch('app.routers.health.get_opensearch')
    def test_cluster_health_detailed(self, mock_get_os, test_client, mock_opensearch_client):
        """Test /health/cluster returns detailed cluster info"""
        mock_opensearch_client.cluster.health.return_value = {
            "cluster_name": "test-cluster",
            "status": "green",
            "number_of_nodes": 3,
            "active_primary_shards": 10,
            "active_shards": 20,
            "relocating_shards": 0,
            "initializing_shards": 0,
            "unassigned_shards": 0
        }
        mock_get_os.return_value = mock_opensearch_client

        response = test_client.get("/health/cluster")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["cluster_name"] == "test-cluster"
        assert data["data"]["number_of_nodes"] == 3

    @patch('app.routers.health.get_opensearch')
    def test_cluster_health_connection_error(self, mock_get_os, test_client):
        """Test /health/cluster handles connection errors"""
        mock_client = MagicMock()
        mock_client.cluster.health.side_effect = os_exceptions.ConnectionError(
            "N/A", "Connection refused", None
        )
        mock_get_os.return_value = mock_client

        response = test_client.get("/health/cluster")

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
