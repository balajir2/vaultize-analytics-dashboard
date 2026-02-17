"""
Tests for routers/health.py

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_scheduler():
    scheduler = MagicMock()
    scheduler.is_running = True
    scheduler.rule_loader.rules = {"rule1": MagicMock(), "rule2": MagicMock()}
    return scheduler


class TestHealthRouter:
    """Tests for health check endpoints."""

    @patch("app.routers.health.get_opensearch")
    def test_health_healthy(self, mock_get_os, client, mock_scheduler):
        mock_client = MagicMock()
        mock_client.cluster.health.return_value = {
            "status": "green",
            "number_of_nodes": 3,
        }
        mock_get_os.return_value = mock_client
        app.state.scheduler = mock_scheduler

        response = client.get("/health/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["opensearch"]["status"] == "green"
        assert data["scheduler"] == "running"
        assert data["rules_loaded"] == 2

    @patch("app.routers.health.get_opensearch")
    def test_health_degraded_no_opensearch(self, mock_get_os, client, mock_scheduler):
        mock_get_os.side_effect = Exception("connection refused")
        app.state.scheduler = mock_scheduler

        response = client.get("/health/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["opensearch"] is None

    @patch("app.routers.health.get_opensearch")
    def test_health_degraded_scheduler_stopped(self, mock_get_os, client):
        mock_client = MagicMock()
        mock_client.cluster.health.return_value = {
            "status": "green",
            "number_of_nodes": 3,
        }
        mock_get_os.return_value = mock_client
        scheduler = MagicMock()
        scheduler.is_running = False
        scheduler.rule_loader.rules = {}
        app.state.scheduler = scheduler

        response = client.get("/health/")
        data = response.json()
        assert data["status"] == "degraded"
        assert data["scheduler"] == "stopped"

    def test_liveness(self, client):
        response = client.get("/health/liveness")
        assert response.status_code == 200
        assert response.json() == {"status": "alive"}

    @patch("app.routers.health.get_opensearch")
    def test_readiness_ready(self, mock_get_os, client, mock_scheduler):
        mock_client = MagicMock()
        mock_client.cluster.health.return_value = {"status": "green"}
        mock_get_os.return_value = mock_client
        app.state.scheduler = mock_scheduler

        response = client.get("/health/readiness")
        assert response.status_code == 200
        assert response.json() == {"status": "ready"}

    @patch("app.routers.health.get_opensearch")
    def test_readiness_opensearch_down(self, mock_get_os, client, mock_scheduler):
        mock_get_os.side_effect = Exception("connection refused")
        app.state.scheduler = mock_scheduler

        response = client.get("/health/readiness")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "not_ready"
        assert "OpenSearch" in data["reason"]

    @patch("app.routers.health.get_opensearch")
    def test_readiness_scheduler_not_running(self, mock_get_os, client):
        mock_client = MagicMock()
        mock_client.cluster.health.return_value = {"status": "green"}
        mock_get_os.return_value = mock_client
        scheduler = MagicMock()
        scheduler.is_running = False
        app.state.scheduler = scheduler

        response = client.get("/health/readiness")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "not_ready"
        assert "Scheduler" in data["reason"]
