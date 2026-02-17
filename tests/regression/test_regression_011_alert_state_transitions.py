"""
Regression Test RT-011: Alert State Machine Transitions

Original Issue:
    The alerting service state machine must correctly transition between
    OK, FIRING, and RESOLVED states. Incorrect transitions cause:
    - Missed alerts (condition met but no notification)
    - Alert storms (repeated notifications without throttle)
    - Stuck states (alert never resolves)

State Machine:
    OK + condition_met      -> FIRING   (notify)
    FIRING + condition_met  -> FIRING   (throttle check)
    FIRING + not_met        -> RESOLVED (notify)
    RESOLVED + not_met      -> OK       (silent)
    RESOLVED + condition_met -> FIRING  (notify)
    OK + not_met            -> OK       (silent)

Key Requirements:
    - All 5 operators (gt, gte, lt, lte, eq) must evaluate correctly
    - State transitions follow the defined state machine
    - Throttle prevents repeat notifications within window
    - Throttle allows notifications after window expires

Date: 2026-02-10
Severity: Critical
"""

import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Add alerting app to path for imports
ALERTING_APP_DIR = Path(__file__).resolve().parents[2] / "analytics" / "alerting"
sys.path.insert(0, str(ALERTING_APP_DIR))

from app.models.alert_rule import (
    AlertAction,
    AlertCondition,
    AlertMetadata,
    AlertQuery,
    AlertQueryTimeRange,
    AlertRule,
    AlertSchedule,
    AlertThrottle,
    WebhookConfig,
)
from app.models.alert_state import AlertState, AlertStateRecord
from app.services.condition_evaluator import ConditionEvaluator, OPERATORS
from app.services.query_executor import QueryResult
from app.services.state_manager import StateManager


@pytest.fixture
def mock_opensearch():
    """Mock OpenSearch client for state manager."""
    client = MagicMock()
    client.indices.exists.return_value = True
    client.search.return_value = {
        "hits": {"total": {"value": 0, "relation": "eq"}, "hits": []}
    }
    client.index.return_value = {"result": "created"}
    return client


@pytest.fixture
def state_manager(mock_opensearch):
    """Initialized state manager with mock OpenSearch."""
    sm = StateManager(mock_opensearch, ".alerts-state-test")
    sm.initialize()
    return sm


@pytest.fixture
def sample_rule():
    """A sample alert rule for state transition testing."""
    return AlertRule(
        name="Test State Rule",
        description="Rule for testing state transitions",
        enabled=True,
        schedule=AlertSchedule(interval="5m"),
        query=AlertQuery(
            index=["logs-*"],
            time_field="@timestamp",
            time_range=AlertQueryTimeRange(**{"from": "now-5m", "to": "now"}),
            filter={"match_all": {}},
        ),
        condition=AlertCondition(type="threshold", operator="gt", value=100),
        actions=[
            AlertAction(
                type="webhook",
                name="test",
                webhook=WebhookConfig(
                    url="http://example.com/hook",
                    method="POST",
                    body={"text": "test"},
                ),
            )
        ],
        throttle=AlertThrottle(value=15, unit="minutes"),
        metadata=AlertMetadata(
            severity="high", category="test", owner="test-team", tags=[]
        ),
    )


class TestRegressionAlertStateTransitions:
    """Regression tests for the alert state machine."""

    # -----------------------------------------------------------------------
    # State Transition Tests
    # -----------------------------------------------------------------------

    def test_ok_to_firing_on_condition_met(self, state_manager, sample_rule):
        """
        Verify OK -> FIRING when condition is met.

        This is the primary alert firing path. A failure here means alerts
        never fire regardless of threshold violations.
        """
        transition = state_manager.update_state(sample_rule, True, 150.0)
        assert transition.previous_state == AlertState.OK
        assert transition.new_state == AlertState.FIRING
        assert transition.changed is True
        assert transition.should_notify is True

    def test_firing_to_resolved_on_condition_cleared(self, state_manager, sample_rule):
        """
        Verify FIRING -> RESOLVED when condition clears.

        This is the alert resolution path. A failure means alerts stay stuck
        in FIRING state forever even after the problem is fixed.
        """
        state_manager.update_state(sample_rule, True, 150.0)
        transition = state_manager.update_state(sample_rule, False, 50.0)
        assert transition.previous_state == AlertState.FIRING
        assert transition.new_state == AlertState.RESOLVED
        assert transition.changed is True
        assert transition.should_notify is True

    def test_resolved_to_ok_on_continued_clear(self, state_manager, sample_rule):
        """
        Verify RESOLVED -> OK when condition remains clear.

        This completes the lifecycle. A failure means rules stay in RESOLVED
        state permanently instead of returning to OK.
        """
        state_manager.update_state(sample_rule, True, 150.0)
        state_manager.update_state(sample_rule, False, 50.0)
        transition = state_manager.update_state(sample_rule, False, 30.0)
        assert transition.previous_state == AlertState.RESOLVED
        assert transition.new_state == AlertState.OK
        assert transition.changed is True
        assert transition.should_notify is False

    def test_resolved_to_firing_on_re_trigger(self, state_manager, sample_rule):
        """
        Verify RESOLVED -> FIRING when condition triggers again.

        This tests re-firing after resolution. A failure means alerts that
        resolve and re-fire would be silently missed.
        """
        state_manager.update_state(sample_rule, True, 150.0)
        state_manager.update_state(sample_rule, False, 50.0)
        transition = state_manager.update_state(sample_rule, True, 200.0)
        assert transition.previous_state == AlertState.RESOLVED
        assert transition.new_state == AlertState.FIRING
        assert transition.changed is True
        assert transition.should_notify is True

    def test_ok_stays_ok_when_condition_not_met(self, state_manager, sample_rule):
        """
        Verify OK -> OK when condition is not met (no spurious transitions).
        """
        transition = state_manager.update_state(sample_rule, False, 50.0)
        assert transition.previous_state == AlertState.OK
        assert transition.new_state == AlertState.OK
        assert transition.changed is False
        assert transition.should_notify is False

    def test_full_lifecycle(self, state_manager, sample_rule):
        """
        Verify the complete lifecycle: OK -> FIRING -> RESOLVED -> OK.

        This end-to-end test catches any corruption in state tracking
        across multiple transitions.
        """
        # OK -> FIRING
        t1 = state_manager.update_state(sample_rule, True, 150.0)
        assert t1.new_state == AlertState.FIRING

        # FIRING -> RESOLVED
        t2 = state_manager.update_state(sample_rule, False, 50.0)
        assert t2.new_state == AlertState.RESOLVED

        # RESOLVED -> OK
        t3 = state_manager.update_state(sample_rule, False, 30.0)
        assert t3.new_state == AlertState.OK

        # Final state check
        state = state_manager.get_state(sample_rule.name)
        assert state.state == AlertState.OK
        assert state.consecutive_fires == 0

    # -----------------------------------------------------------------------
    # Throttle Tests
    # -----------------------------------------------------------------------

    def test_throttle_prevents_repeat_notification(self, state_manager, sample_rule):
        """
        Verify throttle prevents repeated notifications while FIRING.

        Without throttle enforcement, each check cycle would send a
        notification, causing alert storms.
        """
        # First fire - should notify
        t1 = state_manager.update_state(sample_rule, True, 150.0)
        assert t1.should_notify is True

        # Still firing - throttle should prevent notification
        t2 = state_manager.update_state(sample_rule, True, 200.0)
        assert t2.should_notify is False

    def test_throttle_allows_after_window_expires(self, state_manager, sample_rule):
        """
        Verify notifications are allowed after the throttle window expires.

        A broken throttle that never expires means only one notification
        ever gets sent, even for ongoing incidents.
        """
        # First fire
        state_manager.update_state(sample_rule, True, 150.0)

        # Set last_notified to 1 hour ago (beyond 15-minute throttle)
        state = state_manager.get_state(sample_rule.name)
        state.last_notified = datetime.now(timezone.utc) - timedelta(hours=1)

        # Should now be allowed
        t2 = state_manager.update_state(sample_rule, True, 200.0)
        assert t2.should_notify is True

    # -----------------------------------------------------------------------
    # Operator Tests
    # -----------------------------------------------------------------------

    def test_all_operators_registered(self):
        """
        Verify all 5 comparison operators are available.

        A missing operator means rules using it silently fail to evaluate,
        returning condition_met=False always.
        """
        expected = {"gt", "gte", "lt", "lte", "eq"}
        assert set(OPERATORS.keys()) == expected

    def test_gt_operator_evaluates_correctly(self):
        """Verify gt (greater than) operator boundary behavior."""
        evaluator = ConditionEvaluator()
        rule = _make_rule("gt", 100)

        assert evaluator.evaluate(rule, _make_qr(101)).condition_met is True
        assert evaluator.evaluate(rule, _make_qr(100)).condition_met is False
        assert evaluator.evaluate(rule, _make_qr(99)).condition_met is False

    def test_gte_operator_evaluates_correctly(self):
        """Verify gte (greater than or equal) operator boundary behavior."""
        evaluator = ConditionEvaluator()
        rule = _make_rule("gte", 100)

        assert evaluator.evaluate(rule, _make_qr(101)).condition_met is True
        assert evaluator.evaluate(rule, _make_qr(100)).condition_met is True
        assert evaluator.evaluate(rule, _make_qr(99)).condition_met is False

    def test_lt_operator_evaluates_correctly(self):
        """Verify lt (less than) operator boundary behavior."""
        evaluator = ConditionEvaluator()
        rule = _make_rule("lt", 100)

        assert evaluator.evaluate(rule, _make_qr(99)).condition_met is True
        assert evaluator.evaluate(rule, _make_qr(100)).condition_met is False
        assert evaluator.evaluate(rule, _make_qr(101)).condition_met is False

    def test_lte_operator_evaluates_correctly(self):
        """Verify lte (less than or equal) operator boundary behavior."""
        evaluator = ConditionEvaluator()
        rule = _make_rule("lte", 100)

        assert evaluator.evaluate(rule, _make_qr(99)).condition_met is True
        assert evaluator.evaluate(rule, _make_qr(100)).condition_met is True
        assert evaluator.evaluate(rule, _make_qr(101)).condition_met is False

    def test_eq_operator_evaluates_correctly(self):
        """Verify eq (equal) operator boundary behavior."""
        evaluator = ConditionEvaluator()
        rule = _make_rule("eq", 100)

        assert evaluator.evaluate(rule, _make_qr(100)).condition_met is True
        assert evaluator.evaluate(rule, _make_qr(99)).condition_met is False
        assert evaluator.evaluate(rule, _make_qr(101)).condition_met is False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_rule(operator: str, value: float) -> AlertRule:
    """Create a minimal rule with a specific condition."""
    return AlertRule(
        name=f"Test {operator} {value}",
        description="Test rule",
        enabled=True,
        schedule=AlertSchedule(interval="5m"),
        query=AlertQuery(
            index=["logs-*"],
            time_field="@timestamp",
            time_range=AlertQueryTimeRange(**{"from": "now-5m", "to": "now"}),
            filter={"match_all": {}},
        ),
        condition=AlertCondition(type="threshold", operator=operator, value=value),
        actions=[
            AlertAction(
                type="webhook",
                name="test",
                webhook=WebhookConfig(
                    url="http://example.com/hook",
                    method="POST",
                    body={"text": "test"},
                ),
            )
        ],
        throttle=AlertThrottle(value=15, unit="minutes"),
        metadata=AlertMetadata(
            severity="high", category="test", owner="test-team", tags=[]
        ),
    )


def _make_qr(value: float) -> QueryResult:
    """Create a simple query result with the given value."""
    return QueryResult(value=value, took_ms=5, raw_response={}, success=True)
