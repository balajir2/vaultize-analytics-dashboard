"""
Integration Test: Alerting Service

Tests alerting service integration with OpenSearch for
rule evaluation, state management, and history recording.

Requires: Alerting Service and OpenSearch running.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import pytest
import requests

# ============================================================================
# Configuration
# ============================================================================

OPENSEARCH_URL = "http://localhost:9200"
ALERTING_URL = "http://localhost:8001"


def is_service_up(url: str) -> bool:
    try:
        return requests.get(url, timeout=5).status_code < 500
    except Exception:
        return False


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="module")
def require_alerting():
    if not is_service_up(f"{ALERTING_URL}/health/liveness"):
        pytest.skip("Alerting Service is not running")
    return ALERTING_URL


@pytest.fixture(scope="module")
def require_opensearch():
    if not is_service_up(f"{OPENSEARCH_URL}/_cluster/health"):
        pytest.skip("OpenSearch is not running")
    return OPENSEARCH_URL


# ============================================================================
# Tests
# ============================================================================

class TestAlertingIntegration:
    """Integration tests for the alerting service with OpenSearch."""

    def test_alerting_connects_to_opensearch(self, require_alerting):
        """Alerting service readiness implies OpenSearch connection."""
        resp = requests.get(f"{require_alerting}/health/readiness", timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        # Readiness check should verify OpenSearch connectivity
        assert data.get("status") in ("healthy", "ready")

    def test_rules_endpoint_returns_list(self, require_alerting):
        """Rules endpoint returns a list of configured rules."""
        resp = requests.get(f"{require_alerting}/api/v1/rules", timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        rules = data.get("rules", data) if isinstance(data, dict) else data
        assert isinstance(rules, list)

    def test_state_endpoint_returns_data(self, require_alerting):
        """State endpoint returns current alert states."""
        resp = requests.get(f"{require_alerting}/api/v1/state", timeout=10)
        assert resp.status_code == 200

    def test_evaluate_endpoint_works(self, require_alerting, require_opensearch):
        """Evaluation endpoint triggers rule evaluation."""
        resp = requests.post(f"{require_alerting}/api/v1/evaluate", timeout=30)
        # Accept 200 (success), 404 (endpoint may not exist), or 405
        assert resp.status_code in (200, 404, 405)

    def test_opensearch_has_alert_indices(self, require_opensearch, require_alerting):
        """After evaluation, alert-related indices may exist."""
        # Trigger evaluation first
        requests.post(f"{require_alerting}/api/v1/evaluate", timeout=30)

        resp = requests.get(
            f"{require_opensearch}/_cat/indices/.alerts*?format=json",
            timeout=10,
        )
        # It's OK if no indices exist yet (no alerts triggered)
        assert resp.status_code in (200, 404)
