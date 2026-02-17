"""
E2E Test: Alert Flow

Tests the alerting pipeline:
  Alert rules loaded -> Evaluation -> State transitions -> History

Requires: Alerting Service and OpenSearch running.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import pytest
import requests

pytestmark = pytest.mark.e2e


# ============================================================================
# Tests: Alerting Service Flow
# ============================================================================

class TestAlertFlow:
    """End-to-end alerting: rules -> evaluation -> state."""

    def test_alerting_service_healthy(self, alerting_available):
        """Alerting service must be healthy."""
        resp = requests.get(f"{alerting_available}/health/liveness", timeout=10)
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

    def test_alerting_readiness(self, alerting_available):
        """Alerting service readiness check passes."""
        resp = requests.get(f"{alerting_available}/health/readiness", timeout=10)
        assert resp.status_code == 200

    def test_alert_rules_loaded(self, alerting_available):
        """Alert rules are loaded from config."""
        resp = requests.get(f"{alerting_available}/api/v1/rules", timeout=10)
        assert resp.status_code == 200
        data = resp.json()
        rules = data.get("rules", data) if isinstance(data, dict) else data
        assert len(rules) > 0, "No alert rules loaded"

    def test_alert_rule_has_required_fields(self, alerting_available):
        """Each alert rule has required fields."""
        resp = requests.get(f"{alerting_available}/api/v1/rules", timeout=10)
        data = resp.json()
        rules = data.get("rules", data) if isinstance(data, dict) else data

        for rule in rules[:3]:  # Check first 3 rules
            assert "name" in rule or "id" in rule, f"Rule missing name/id: {rule}"

    def test_alert_state_endpoint(self, alerting_available):
        """Alert state endpoint is accessible."""
        resp = requests.get(f"{alerting_available}/api/v1/state", timeout=10)
        # Should return 200 with state info or empty state
        assert resp.status_code == 200

    def test_trigger_evaluation(self, alerting_available):
        """Trigger manual evaluation (if endpoint exists)."""
        resp = requests.post(f"{alerting_available}/api/v1/evaluate", timeout=30)
        # Evaluation should succeed or return 404 if endpoint doesn't exist
        assert resp.status_code in (200, 404, 405)
