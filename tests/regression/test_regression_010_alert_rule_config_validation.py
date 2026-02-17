"""
Regression Test RT-010: Alert Rule Configuration Validation

Original Issue:
    Alert rule JSON files in configs/alert-rules/ must conform to a strict
    schema for the alerting service to load them. Missing required fields,
    invalid operators, malformed intervals, or bad webhook configs cause
    silent rule loading failures - alerts never fire.

Key Requirements:
    - All rule files must be valid JSON
    - Required fields: name, description, enabled, schedule, query, condition,
      actions, throttle, metadata
    - condition.operator must be one of: gt, gte, lt, lte, eq
    - schedule.interval must match pattern: <number><s|m|h|d>
    - actions must have at least one webhook with url and method
    - throttle.unit must be: seconds, minutes, or hours
    - metadata.severity must be: critical, high, medium, or low

Date: 2026-02-10
Severity: High
"""

import json
import re
from pathlib import Path

import pytest


ALERT_RULES_DIR = Path("configs/alert-rules")

REQUIRED_TOP_LEVEL_FIELDS = {
    "name", "description", "enabled", "schedule", "query",
    "condition", "actions", "throttle", "metadata",
}
VALID_OPERATORS = {"gt", "gte", "lt", "lte", "eq"}
VALID_THROTTLE_UNITS = {"seconds", "minutes", "hours"}
VALID_SEVERITIES = {"critical", "high", "medium", "low"}
INTERVAL_PATTERN = re.compile(r"^\d+[smhd]$")


class TestRegressionAlertRuleConfigValidation:
    """Regression tests for alert rule JSON configuration files."""

    @pytest.fixture
    def rule_files(self):
        """Discover all .json rule files in the alert rules directory."""
        assert ALERT_RULES_DIR.exists(), f"Alert rules directory not found: {ALERT_RULES_DIR}"
        files = sorted(ALERT_RULES_DIR.glob("*.json"))
        assert len(files) > 0, "No .json rule files found in alert rules directory"
        return files

    @pytest.fixture
    def loaded_rules(self, rule_files):
        """Load all rule files as parsed JSON."""
        rules = {}
        for file_path in rule_files:
            with open(file_path, "r", encoding="utf-8") as f:
                rules[file_path.name] = json.load(f)
        return rules

    def test_all_rule_files_are_valid_json(self, rule_files):
        """
        Verify every .json file in the alert rules directory is parseable JSON.

        Invalid JSON would cause the rule loader to skip the file silently.
        """
        for file_path in rule_files:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert isinstance(data, dict), f"{file_path.name}: root must be a JSON object"

    def test_required_fields_present(self, loaded_rules):
        """
        Verify every rule file has all required top-level fields.

        Missing fields cause Pydantic validation errors during rule loading.
        """
        for filename, rule in loaded_rules.items():
            present_fields = set(rule.keys())
            missing = REQUIRED_TOP_LEVEL_FIELDS - present_fields
            assert not missing, (
                f"{filename}: missing required fields: {missing}"
            )

    def test_condition_operators_are_valid(self, loaded_rules):
        """
        Verify condition.operator is one of the supported comparison operators.

        An invalid operator causes the condition evaluator to always return False,
        meaning the alert never fires even when the threshold is breached.
        """
        for filename, rule in loaded_rules.items():
            op = rule["condition"]["operator"]
            assert op in VALID_OPERATORS, (
                f"{filename}: invalid operator '{op}', must be one of {VALID_OPERATORS}"
            )

    def test_schedule_intervals_are_valid(self, loaded_rules):
        """
        Verify schedule.interval matches the expected format (e.g., '5m', '1h', '30s').

        An invalid interval format causes a ValueError in the scheduler,
        preventing the rule from being scheduled.
        """
        for filename, rule in loaded_rules.items():
            interval = rule["schedule"]["interval"]
            assert INTERVAL_PATTERN.match(interval), (
                f"{filename}: invalid interval '{interval}', must match pattern '<number><s|m|h|d>'"
            )

    def test_actions_have_valid_webhook_config(self, loaded_rules):
        """
        Verify each rule has at least one action with a valid webhook config.

        Missing webhook url or method means notifications silently fail.
        """
        for filename, rule in loaded_rules.items():
            actions = rule["actions"]
            assert len(actions) > 0, f"{filename}: must have at least one action"
            for i, action in enumerate(actions):
                assert "webhook" in action, (
                    f"{filename}: action[{i}] missing 'webhook' config"
                )
                webhook = action["webhook"]
                assert "url" in webhook, (
                    f"{filename}: action[{i}].webhook missing 'url'"
                )
                assert "method" in webhook, (
                    f"{filename}: action[{i}].webhook missing 'method'"
                )
                assert webhook["method"] in ("POST", "PUT", "PATCH"), (
                    f"{filename}: action[{i}].webhook.method must be POST, PUT, or PATCH"
                )

    def test_throttle_units_are_valid(self, loaded_rules):
        """
        Verify throttle.unit is a recognized time unit.

        An invalid unit defaults to 60s multiplier in the state manager,
        which could cause unexpected notification frequency.
        """
        for filename, rule in loaded_rules.items():
            unit = rule["throttle"]["unit"]
            assert unit in VALID_THROTTLE_UNITS, (
                f"{filename}: invalid throttle unit '{unit}', must be one of {VALID_THROTTLE_UNITS}"
            )
            value = rule["throttle"]["value"]
            assert isinstance(value, (int, float)) and value > 0, (
                f"{filename}: throttle.value must be a positive number"
            )

    def test_severity_values_are_valid(self, loaded_rules):
        """
        Verify metadata.severity is a recognized severity level.

        Invalid severity values break dashboard filtering and alert routing.
        """
        for filename, rule in loaded_rules.items():
            severity = rule["metadata"]["severity"]
            assert severity in VALID_SEVERITIES, (
                f"{filename}: invalid severity '{severity}', must be one of {VALID_SEVERITIES}"
            )

    def test_query_has_required_fields(self, loaded_rules):
        """
        Verify query section has index, time_range, and filter.

        Missing query fields cause OpenSearch query failures.
        """
        for filename, rule in loaded_rules.items():
            query = rule["query"]
            assert "index" in query, f"{filename}: query missing 'index'"
            assert isinstance(query["index"], list), f"{filename}: query.index must be a list"
            assert len(query["index"]) > 0, f"{filename}: query.index must have at least one index"
            assert "time_range" in query, f"{filename}: query missing 'time_range'"
            assert "filter" in query, f"{filename}: query missing 'filter'"
            time_range = query["time_range"]
            assert "from" in time_range, f"{filename}: query.time_range missing 'from'"
            assert "to" in time_range, f"{filename}: query.time_range missing 'to'"

    def test_metadata_has_required_fields(self, loaded_rules):
        """
        Verify metadata section has required fields for categorization.

        Missing metadata fields break alert routing and dashboard display.
        """
        for filename, rule in loaded_rules.items():
            metadata = rule["metadata"]
            assert "severity" in metadata, f"{filename}: metadata missing 'severity'"
            assert "category" in metadata, f"{filename}: metadata missing 'category'"
            assert "owner" in metadata, f"{filename}: metadata missing 'owner'"
