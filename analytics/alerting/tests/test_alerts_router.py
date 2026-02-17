"""
Tests for routers/alerts.py

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.alert_state import AlertState, AlertStateRecord
from app.models.alert_event import AlertEvent


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_scheduler_with_rules(sample_count_rule, sample_agg_rule):
    """Mock scheduler with loaded rules and state."""
    scheduler = MagicMock()
    scheduler.is_running = True

    # Rule loader
    scheduler.rule_loader.rules = {
        sample_count_rule.name: sample_count_rule,
        sample_agg_rule.name: sample_agg_rule,
    }
    scheduler.rule_loader.get_rule.side_effect = lambda name: {
        sample_count_rule.name: sample_count_rule,
        sample_agg_rule.name: sample_agg_rule,
    }.get(name)
    scheduler.rule_loader.get_enabled_rules.return_value = [sample_count_rule, sample_agg_rule]

    # State manager
    ok_state = AlertStateRecord(rule_name=sample_count_rule.name)
    firing_state = AlertStateRecord(
        rule_name=sample_agg_rule.name,
        state=AlertState.FIRING,
        last_checked=datetime(2026, 2, 10, 12, 0, 0, tzinfo=timezone.utc),
    )
    scheduler.state_manager.get_state.side_effect = lambda name: {
        sample_count_rule.name: ok_state,
        sample_agg_rule.name: firing_state,
    }.get(name, AlertStateRecord(rule_name=name))

    # Manual trigger
    async def mock_trigger(name):
        rule = scheduler.rule_loader.get_rule(name)
        if rule is None:
            return None
        return AlertEvent(
            rule_name=name,
            event_type="manual_trigger",
            timestamp=datetime(2026, 2, 10, 12, 0, 0, tzinfo=timezone.utc),
            value=150.0,
            threshold=100.0,
            condition_met=True,
        )

    scheduler.trigger_manual = AsyncMock(side_effect=mock_trigger)

    # History
    scheduler.history_storage.get_history.return_value = [
        {
            "rule_name": "High Error Rate",
            "event_type": "fired",
            "timestamp": "2026-02-10T12:00:00Z",
        }
    ]

    # Reload
    scheduler.reload_rules.return_value = None

    return scheduler


class TestAlertsRouter:
    """Tests for alert management API endpoints."""

    def test_list_rules(self, client, mock_scheduler_with_rules):
        app.state.scheduler = mock_scheduler_with_rules
        response = client.get("/api/v1/alerts/rules")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) == 2

    def test_list_rules_includes_state(self, client, mock_scheduler_with_rules):
        app.state.scheduler = mock_scheduler_with_rules
        response = client.get("/api/v1/alerts/rules")
        rules = response.json()["data"]
        names_and_states = {r["name"]: r["state"] for r in rules}
        assert names_and_states["High Error Rate"] == "ok"
        assert names_and_states["Slow API Response"] == "firing"

    def test_get_rule_status(self, client, mock_scheduler_with_rules):
        app.state.scheduler = mock_scheduler_with_rules
        response = client.get("/api/v1/alerts/rules/High%20Error%20Rate/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["rule"]["name"] == "High Error Rate"

    def test_get_rule_status_not_found(self, client, mock_scheduler_with_rules):
        app.state.scheduler = mock_scheduler_with_rules
        response = client.get("/api/v1/alerts/rules/Nonexistent/status")
        assert response.status_code == 404

    def test_trigger_rule(self, client, mock_scheduler_with_rules):
        app.state.scheduler = mock_scheduler_with_rules
        response = client.post("/api/v1/alerts/rules/High%20Error%20Rate/trigger")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["event_type"] == "manual_trigger"

    def test_trigger_rule_not_found(self, client, mock_scheduler_with_rules):
        app.state.scheduler = mock_scheduler_with_rules
        response = client.post("/api/v1/alerts/rules/Nonexistent/trigger")
        assert response.status_code == 404

    def test_get_history(self, client, mock_scheduler_with_rules):
        app.state.scheduler = mock_scheduler_with_rules
        response = client.get("/api/v1/alerts/history")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) == 1
        assert data["data"][0]["event_type"] == "fired"

    def test_get_history_with_filter(self, client, mock_scheduler_with_rules):
        app.state.scheduler = mock_scheduler_with_rules
        response = client.get(
            "/api/v1/alerts/history?rule_name=High%20Error%20Rate&limit=50"
        )
        assert response.status_code == 200
        mock_scheduler_with_rules.history_storage.get_history.assert_called_once_with(
            rule_name="High Error Rate", limit=50, time_from="now-24h"
        )

    def test_reload_rules(self, client, mock_scheduler_with_rules):
        app.state.scheduler = mock_scheduler_with_rules
        response = client.post("/api/v1/alerts/rules/reload")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "2" in data["message"]
        mock_scheduler_with_rules.reload_rules.assert_called_once()

    def test_service_unavailable_no_scheduler(self, client):
        # Remove scheduler from app state
        if hasattr(app.state, "scheduler"):
            delattr(app.state, "scheduler")
        response = client.get("/api/v1/alerts/rules")
        assert response.status_code == 503
