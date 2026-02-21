"""
Regression Test RT-025: Notification Result Aggregation

Validates that the alert scheduler collects per-action notification
results instead of overwriting with the last action's result.
Tests the notification_results list field in AlertEvent and the
aggregate status logic (success/partial/failed).

Date: 2026-02-21
Severity: Medium
Category: Bug Fix - Alerting
Authors: Balaji Rajan and Claude (Anthropic)
"""

import ast
from pathlib import Path

import pytest

# ============================================================================
# Constants
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SCHEDULER = PROJECT_ROOT / "analytics" / "alerting" / "app" / "services" / "scheduler.py"
ALERT_EVENT = PROJECT_ROOT / "analytics" / "alerting" / "app" / "models" / "alert_event.py"


# ============================================================================
# Tests: AlertEvent Model Has notification_results
# ============================================================================

class TestAlertEventModel:
    """Validate AlertEvent model changes."""

    def test_regression_025_01_has_notification_results_field(self):
        """RT-025-01: AlertEvent must have notification_results field."""
        source = ALERT_EVENT.read_text(encoding="utf-8")
        assert "notification_results" in source, \
            "AlertEvent must have notification_results field"

    def test_regression_025_02_notification_results_is_list(self):
        """RT-025-02: notification_results must be typed as List."""
        source = ALERT_EVENT.read_text(encoding="utf-8")
        assert "List" in source, \
            "AlertEvent must import List for notification_results type"

    def test_regression_025_03_to_dict_includes_notification_results(self):
        """RT-025-03: to_dict() must include notification_results."""
        source = ALERT_EVENT.read_text(encoding="utf-8")
        # Find to_dict method and verify notification_results is in it
        in_to_dict = False
        found = False
        for line in source.splitlines():
            if "def to_dict" in line:
                in_to_dict = True
            if in_to_dict and "notification_results" in line:
                found = True
                break
        assert found, "to_dict() must include notification_results in output"

    def test_regression_025_04_notification_status_includes_partial(self):
        """RT-025-04: notification_status comment must mention 'partial'."""
        source = ALERT_EVENT.read_text(encoding="utf-8")
        assert "partial" in source, \
            "AlertEvent notification_status should document 'partial' as a valid value"


# ============================================================================
# Tests: Scheduler Collects Per-Action Results
# ============================================================================

class TestSchedulerResultCollection:
    """Validate scheduler collects results per action."""

    def test_regression_025_05_notification_results_list_initialized(self):
        """RT-025-05: Scheduler must initialize notification_results as empty list."""
        source = SCHEDULER.read_text(encoding="utf-8")
        assert "notification_results = []" in source, \
            "Scheduler must initialize notification_results as empty list"

    def test_regression_025_06_results_appended_not_overwritten(self):
        """RT-025-06: Scheduler must append to notification_results, not overwrite."""
        source = SCHEDULER.read_text(encoding="utf-8")
        assert "notification_results.append" in source, \
            "Scheduler must append each action result to notification_results list"

    def test_regression_025_07_no_direct_overwrite_in_loop(self):
        """RT-025-07: Loop must not directly assign notification_sent = result.success."""
        source = SCHEDULER.read_text(encoding="utf-8")
        lines = source.splitlines()
        in_action_loop = False
        has_overwrite = False
        for line in lines:
            stripped = line.strip()
            if "for action in rule.actions:" in stripped:
                in_action_loop = True
                continue
            if in_action_loop:
                # Check for the old overwrite pattern
                if stripped == "notification_sent = result.success":
                    has_overwrite = True
                # End of loop body (dedented)
                if stripped and not line.startswith(" " * 16) and not stripped.startswith("#"):
                    if "notification_results" not in stripped:
                        break
        assert not has_overwrite, \
            "Scheduler must NOT overwrite notification_sent = result.success in loop"

    def test_regression_025_08_aggregate_status_computed(self):
        """RT-025-08: Scheduler must compute aggregate status (success/partial/failed)."""
        source = SCHEDULER.read_text(encoding="utf-8")
        assert '"partial"' in source, \
            "Scheduler must compute 'partial' aggregate status"
        assert '"success"' in source and '"failed"' in source, \
            "Scheduler must compute 'success' and 'failed' aggregate statuses"

    def test_regression_025_09_notification_results_passed_to_event(self):
        """RT-025-09: AlertEvent construction must include notification_results."""
        source = SCHEDULER.read_text(encoding="utf-8")
        # Find the AlertEvent() constructor call and check for notification_results
        in_alert_event = False
        found = False
        for line in source.splitlines():
            if "AlertEvent(" in line:
                in_alert_event = True
            if in_alert_event and "notification_results=" in line:
                found = True
                break
            if in_alert_event and line.strip().startswith("))"):
                in_alert_event = False
        assert found, \
            "AlertEvent construction must include notification_results=notification_results"
