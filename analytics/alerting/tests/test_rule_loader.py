"""
Tests for rule_loader.py

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import json
import os
import tempfile
from pathlib import Path

import pytest

from app.services.rule_loader import RuleLoader


class TestRuleLoader:
    """Tests for the RuleLoader class."""

    def test_load_all_rules(self, rules_dir_with_files):
        loader = RuleLoader(rules_dir_with_files)
        rules = loader.load_all_rules()
        assert len(rules) == 3  # 2 enabled + 1 disabled

    def test_get_enabled_rules(self, rules_dir_with_files):
        loader = RuleLoader(rules_dir_with_files)
        loader.load_all_rules()
        enabled = loader.get_enabled_rules()
        assert len(enabled) == 2
        names = [r.name for r in enabled]
        assert "High Error Rate" in names
        assert "Slow API Response" in names

    def test_get_rule_by_name(self, rules_dir_with_files):
        loader = RuleLoader(rules_dir_with_files)
        loader.load_all_rules()
        rule = loader.get_rule("High Error Rate")
        assert rule is not None
        assert rule.name == "High Error Rate"
        assert rule.condition.operator == "gt"
        assert rule.condition.value == 100

    def test_get_rule_not_found(self, rules_dir_with_files):
        loader = RuleLoader(rules_dir_with_files)
        loader.load_all_rules()
        assert loader.get_rule("nonexistent") is None

    def test_reload_rules(self, rules_dir_with_files):
        loader = RuleLoader(rules_dir_with_files)
        loader.load_all_rules()
        assert len(loader.rules) == 3

        # Remove a file and reload
        (Path(rules_dir_with_files) / "disabled-rule.json").unlink()
        loader.reload_rules()
        assert len(loader.rules) == 2

    def test_missing_directory(self):
        loader = RuleLoader("/nonexistent/path")
        rules = loader.load_all_rules()
        assert rules == {}

    def test_invalid_json_skipped(self, rules_dir_with_files):
        # Write an invalid JSON file
        with open(Path(rules_dir_with_files) / "bad.json", "w") as f:
            f.write("not valid json{{{")

        loader = RuleLoader(rules_dir_with_files)
        rules = loader.load_all_rules()
        # Should load 3 valid rules, skip the bad one
        assert len(rules) == 3

    def test_invalid_schema_skipped(self, rules_dir_with_files):
        # Write a valid JSON file but invalid rule schema
        with open(Path(rules_dir_with_files) / "bad-schema.json", "w") as f:
            json.dump({"name": "missing fields"}, f)

        loader = RuleLoader(rules_dir_with_files)
        rules = loader.load_all_rules()
        # Should load 3 valid rules, skip the bad one
        assert len(rules) == 3

    def test_env_var_substitution(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            rule_data = {
                "name": "Env Test",
                "description": "Tests env var substitution",
                "enabled": True,
                "schedule": {"interval": "5m"},
                "query": {
                    "index": ["logs-*"],
                    "time_field": "@timestamp",
                    "time_range": {"from": "now-5m", "to": "now"},
                    "filter": {"match_all": {}},
                },
                "condition": {"type": "threshold", "operator": "gt", "value": 100},
                "actions": [
                    {
                        "type": "webhook",
                        "name": "test",
                        "webhook": {
                            "url": "${TEST_WEBHOOK_URL}",
                            "method": "POST",
                            "body": {"text": "alert"},
                        },
                    }
                ],
                "throttle": {"value": 15, "unit": "minutes"},
                "metadata": {
                    "severity": "high",
                    "category": "test",
                    "owner": "test-team",
                    "tags": [],
                },
            }
            with open(Path(tmpdir) / "env-test.json", "w") as f:
                json.dump(rule_data, f)

            os.environ["TEST_WEBHOOK_URL"] = "http://resolved.example.com/hook"
            try:
                loader = RuleLoader(tmpdir)
                loader.load_all_rules()
                rule = loader.get_rule("Env Test")
                assert rule is not None
                assert rule.actions[0].webhook.url == "http://resolved.example.com/hook"
            finally:
                del os.environ["TEST_WEBHOOK_URL"]

    def test_unresolved_env_var_preserved(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            rule_data = {
                "name": "Unresolved Env",
                "description": "Unresolved env var",
                "enabled": True,
                "schedule": {"interval": "5m"},
                "query": {
                    "index": ["logs-*"],
                    "time_field": "@timestamp",
                    "time_range": {"from": "now-5m", "to": "now"},
                    "filter": {"match_all": {}},
                },
                "condition": {"type": "threshold", "operator": "gt", "value": 100},
                "actions": [
                    {
                        "type": "webhook",
                        "name": "test",
                        "webhook": {
                            "url": "${NONEXISTENT_VAR_XYZ}",
                            "method": "POST",
                            "body": {"text": "alert"},
                        },
                    }
                ],
                "throttle": {"value": 15, "unit": "minutes"},
                "metadata": {
                    "severity": "high",
                    "category": "test",
                    "owner": "test-team",
                    "tags": [],
                },
            }
            with open(Path(tmpdir) / "unresolved.json", "w") as f:
                json.dump(rule_data, f)

            loader = RuleLoader(tmpdir)
            loader.load_all_rules()
            rule = loader.get_rule("Unresolved Env")
            assert rule is not None
            # Unresolved vars are preserved as-is
            assert rule.actions[0].webhook.url == "${NONEXISTENT_VAR_XYZ}"

    def test_rules_property(self, rules_dir_with_files):
        loader = RuleLoader(rules_dir_with_files)
        loader.load_all_rules()
        assert isinstance(loader.rules, dict)
        assert len(loader.rules) == 3

    def test_file_path_set_on_rule(self, rules_dir_with_files):
        loader = RuleLoader(rules_dir_with_files)
        loader.load_all_rules()
        rule = loader.get_rule("High Error Rate")
        assert rule is not None
        assert rule.file_path is not None
        assert "high-error-rate.json" in rule.file_path
