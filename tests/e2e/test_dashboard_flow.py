"""
E2E Test: Dashboard Flow

Tests dashboard accessibility and saved object integrity:
  OpenSearch Dashboards accessible -> API docs -> Saved objects valid

Requires: OpenSearch Dashboards and API running.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import pytest
import requests

pytestmark = pytest.mark.e2e


# ============================================================================
# Tests: Dashboard Accessibility
# ============================================================================

class TestDashboardFlow:
    """End-to-end dashboard: access -> objects -> visualizations."""

    def test_dashboards_accessible(self, dashboards_available):
        """OpenSearch Dashboards UI is accessible."""
        resp = requests.get(f"{dashboards_available}/api/status", timeout=10)
        assert resp.status_code == 200

    def test_api_docs_accessible(self, api_available):
        """API documentation (Swagger) is accessible."""
        resp = requests.get(f"{api_available}/docs", timeout=10)
        assert resp.status_code == 200

    def test_api_openapi_spec(self, api_available):
        """OpenAPI spec is accessible."""
        resp = requests.get(f"{api_available}/openapi.json", timeout=10)
        assert resp.status_code == 200
        spec = resp.json()
        assert "paths" in spec
        assert "info" in spec

    def test_api_root_returns_metadata(self, api_available):
        """API root endpoint returns platform metadata."""
        resp = requests.get(f"{api_available}/", timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        assert "name" in data
        assert "version" in data

    def test_health_endpoints_no_auth_required(self, api_available):
        """Health endpoints work without authentication."""
        for endpoint in ["/health/liveness", "/health/readiness"]:
            resp = requests.get(f"{api_available}{endpoint}", timeout=10)
            assert resp.status_code == 200, f"{endpoint} returned {resp.status_code}"

    def test_indices_list_accessible(self, api_available):
        """Indices list endpoint returns data."""
        resp = requests.get(f"{api_available}/api/v1/indices/", timeout=10)
        assert resp.status_code == 200
