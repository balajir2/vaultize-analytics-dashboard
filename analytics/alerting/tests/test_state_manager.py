"""
Tests for state_manager.py

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch

import pytest

from app.models.alert_rule import AlertThrottle
from app.models.alert_state import AlertState, AlertStateRecord
from app.services.state_manager import StateManager


class TestStateManager:
    """Tests for the StateManager class."""

    def setup_method(self):
        self.mock_client = MagicMock()
        self.mock_client.indices.exists.return_value = False
        self.mock_client.indices.create.return_value = {"acknowledged": True}
        self.mock_client.search.return_value = {
            "hits": {"total": {"value": 0, "relation": "eq"}, "hits": []}
        }
        self.mock_client.index.return_value = {"result": "created"}
        self.manager = StateManager(self.mock_client, ".alerts-state")

    # --- Initialization ---

    def test_initialize_creates_index_if_missing(self):
        self.manager.initialize()
        self.mock_client.indices.create.assert_called_once()

    def test_initialize_skips_creation_if_exists(self):
        self.mock_client.indices.exists.return_value = True
        self.manager.initialize()
        self.mock_client.indices.create.assert_not_called()

    def test_initialize_loads_existing_states(self):
        self.mock_client.indices.exists.return_value = True
        self.mock_client.search.return_value = {
            "hits": {
                "total": {"value": 1, "relation": "eq"},
                "hits": [
                    {
                        "_source": {
                            "rule_name": "Test Rule",
                            "state": "firing",
                            "consecutive_fires": 3,
                            "threshold": 100.0,
                        }
                    }
                ],
            }
        }
        self.manager.initialize()
        state = self.manager.get_state("Test Rule")
        assert state.state == AlertState.FIRING
        assert state.consecutive_fires == 3

    # --- get_state ---

    def test_get_state_default_ok(self):
        state = self.manager.get_state("New Rule")
        assert state.state == AlertState.OK
        assert state.rule_name == "New Rule"

    # --- State transitions ---

    def test_ok_to_firing(self, sample_count_rule):
        """OK + condition_met = FIRING (should notify)."""
        transition = self.manager.update_state(sample_count_rule, True, 150.0)
        assert transition.previous_state == AlertState.OK
        assert transition.new_state == AlertState.FIRING
        assert transition.changed is True
        assert transition.should_notify is True

    def test_firing_still_firing(self, sample_count_rule):
        """FIRING + condition_met = still FIRING (check throttle)."""
        # First: go to FIRING
        self.manager.update_state(sample_count_rule, True, 150.0)

        # Second: still met - should check throttle
        # Since last_notified was just set, throttle window not passed
        transition = self.manager.update_state(sample_count_rule, True, 200.0)
        assert transition.previous_state == AlertState.FIRING
        assert transition.new_state == AlertState.FIRING
        assert transition.changed is False
        # Throttle prevents notification (just notified)
        assert transition.should_notify is False

    def test_firing_to_resolved(self, sample_count_rule):
        """FIRING + condition_not_met = RESOLVED (should notify)."""
        # Go to FIRING first
        self.manager.update_state(sample_count_rule, True, 150.0)

        # Condition no longer met
        transition = self.manager.update_state(sample_count_rule, False, 50.0)
        assert transition.previous_state == AlertState.FIRING
        assert transition.new_state == AlertState.RESOLVED
        assert transition.changed is True
        assert transition.should_notify is True

    def test_resolved_to_ok(self, sample_count_rule):
        """RESOLVED + condition_not_met = OK (silent)."""
        # Go to FIRING then RESOLVED
        self.manager.update_state(sample_count_rule, True, 150.0)
        self.manager.update_state(sample_count_rule, False, 50.0)

        # Still not met -> back to OK
        transition = self.manager.update_state(sample_count_rule, False, 30.0)
        assert transition.previous_state == AlertState.RESOLVED
        assert transition.new_state == AlertState.OK
        assert transition.changed is True
        assert transition.should_notify is False

    def test_resolved_to_firing(self, sample_count_rule):
        """RESOLVED + condition_met = FIRING (should notify)."""
        # Go to FIRING then RESOLVED
        self.manager.update_state(sample_count_rule, True, 150.0)
        self.manager.update_state(sample_count_rule, False, 50.0)

        # Condition met again
        transition = self.manager.update_state(sample_count_rule, True, 200.0)
        assert transition.previous_state == AlertState.RESOLVED
        assert transition.new_state == AlertState.FIRING
        assert transition.changed is True
        assert transition.should_notify is True

    def test_ok_stays_ok(self, sample_count_rule):
        """OK + condition_not_met = still OK (silent)."""
        transition = self.manager.update_state(sample_count_rule, False, 50.0)
        assert transition.previous_state == AlertState.OK
        assert transition.new_state == AlertState.OK
        assert transition.changed is False
        assert transition.should_notify is False

    # --- Throttle ---

    def test_throttle_allows_after_window(self, sample_count_rule):
        """Notification allowed when throttle window has passed."""
        # Go to FIRING
        self.manager.update_state(sample_count_rule, True, 150.0)

        # Set last_notified to far in the past
        state = self.manager.get_state(sample_count_rule.name)
        state.last_notified = datetime.now(timezone.utc) - timedelta(hours=1)

        # Should now be allowed to notify again
        transition = self.manager.update_state(sample_count_rule, True, 200.0)
        assert transition.should_notify is True

    def test_throttle_prevents_within_window(self, sample_count_rule):
        """Notification blocked when within throttle window."""
        # Go to FIRING (sets last_notified to now)
        self.manager.update_state(sample_count_rule, True, 150.0)

        # Immediately check again - within 15-minute throttle
        transition = self.manager.update_state(sample_count_rule, True, 200.0)
        assert transition.should_notify is False

    # --- Consecutive fires ---

    def test_consecutive_fires_increment(self, sample_count_rule):
        """Consecutive fire counter increments while FIRING."""
        self.manager.update_state(sample_count_rule, True, 150.0)
        state = self.manager.get_state(sample_count_rule.name)
        assert state.consecutive_fires == 1

        self.manager.update_state(sample_count_rule, True, 200.0)
        assert state.consecutive_fires == 2

    def test_consecutive_fires_reset_on_resolve(self, sample_count_rule):
        """Consecutive fire counter resets on RESOLVED."""
        self.manager.update_state(sample_count_rule, True, 150.0)
        self.manager.update_state(sample_count_rule, True, 200.0)
        state = self.manager.get_state(sample_count_rule.name)
        assert state.consecutive_fires == 2

        self.manager.update_state(sample_count_rule, False, 50.0)
        assert state.consecutive_fires == 0

    # --- Persistence ---

    def test_state_persisted_on_update(self, sample_count_rule):
        self.manager.update_state(sample_count_rule, True, 150.0)
        self.mock_client.index.assert_called()
        call_args = self.mock_client.index.call_args
        assert call_args[1]["index"] == ".alerts-state"
        assert call_args[1]["id"] == sample_count_rule.name

    # --- Throttle parsing ---

    def test_parse_throttle_seconds(self):
        assert StateManager._parse_throttle_seconds(
            AlertThrottle(value=15, unit="minutes")
        ) == 900

    def test_parse_throttle_hours(self):
        assert StateManager._parse_throttle_seconds(
            AlertThrottle(value=2, unit="hours")
        ) == 7200

    def test_parse_throttle_seconds_unit(self):
        assert StateManager._parse_throttle_seconds(
            AlertThrottle(value=30, unit="seconds")
        ) == 30
