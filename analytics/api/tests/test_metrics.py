"""
Unit Tests for Prometheus Metrics Endpoint

Validates that the /metrics endpoint returns Prometheus text format
with expected metrics from prometheus-fastapi-instrumentator.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="function")
def client():
    """Create FastAPI test client."""
    with TestClient(app) as c:
        yield c


class TestMetricsEndpoint:
    """Tests for the /metrics Prometheus endpoint."""

    def test_metrics_returns_200(self, client):
        """GET /metrics returns 200 OK."""
        response = client.get("/metrics")
        assert response.status_code == 200

    def test_metrics_returns_prometheus_format(self, client):
        """GET /metrics returns Prometheus text format content type."""
        response = client.get("/metrics")
        content_type = response.headers.get("content-type", "")
        assert "text/plain" in content_type or "text/openmetrics" in content_type

    def test_metrics_contains_http_request_metrics(self, client):
        """Metrics include HTTP request metrics after making a request."""
        # Generate some metrics by hitting an endpoint
        client.get("/health/liveness")
        response = client.get("/metrics")
        assert "http_request" in response.text

    def test_metrics_not_in_openapi_schema(self, client):
        """The /metrics endpoint should not appear in OpenAPI schema."""
        response = client.get("/openapi.json")
        schema = response.json()
        assert "/metrics" not in schema.get("paths", {})

    def test_metrics_not_rate_limited(self, client):
        """The /metrics endpoint should not be rate limited."""
        for _ in range(50):
            response = client.get("/metrics")
            assert response.status_code == 200
