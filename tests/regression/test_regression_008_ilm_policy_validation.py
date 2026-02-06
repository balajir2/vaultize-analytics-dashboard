"""
Regression Test RT-008: ILM Policy Validation

Original Issue:
    Index Lifecycle Management (ILM) policy must define all four phases
    (hot, warm, cold, delete) with correct min_age progression and required
    actions. A misconfigured ILM policy causes indices to accumulate without
    cleanup, leading to disk exhaustion, or premature deletion of logs.

Key Requirements:
    - Must have all 4 phases: hot, warm, cold, delete
    - min_age must increase monotonically across phases
    - Hot phase must have rollover action with max_age and max_primary_shard_size
    - Delete phase must have a delete action
    - Warm phase should include forcemerge and shrink for storage optimization
    - Cold phase should reduce replicas to 0

Date: 2026-02-06
Severity: High
"""

import json
import pytest
from pathlib import Path


class TestRegressionILMPolicyValidation:
    """Regression tests for ILM policy configuration"""

    @pytest.fixture
    def policy_path(self):
        """Path to ILM policy file"""
        return Path("configs/ilm-policies/logs-lifecycle-policy.json")

    @pytest.fixture
    def policy(self, policy_path):
        """Load and parse ILM policy"""
        with open(policy_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data["policy"]

    @pytest.fixture
    def phases(self, policy):
        """Extract phases from policy"""
        return policy["phases"]

    def test_regression_008_has_all_four_phases(self, phases):
        """
        Verify ILM policy defines all four lifecycle phases.
        Missing phases cause indices to skip lifecycle stages.
        """
        required_phases = {"hot", "warm", "cold", "delete"}
        actual_phases = set(phases.keys())

        for phase in required_phases:
            assert phase in actual_phases, (
                f"ILM policy missing '{phase}' phase. "
                f"Found: {actual_phases}"
            )

    def test_regression_008_min_age_increases_monotonically(self, phases):
        """
        Verify min_age values increase from hot → warm → cold → delete.
        Non-monotonic ages cause phases to overlap or execute out of order.
        """
        def parse_min_age_days(min_age_str):
            """Convert min_age string to days for comparison"""
            if min_age_str.endswith("ms"):
                return 0
            elif min_age_str.endswith("d"):
                return int(min_age_str[:-1])
            elif min_age_str.endswith("h"):
                return int(min_age_str[:-1]) / 24
            return 0

        phase_order = ["hot", "warm", "cold", "delete"]
        ages = []
        for phase_name in phase_order:
            min_age = phases[phase_name].get("min_age", "0ms")
            ages.append((phase_name, parse_min_age_days(min_age)))

        for i in range(len(ages) - 1):
            current_phase, current_age = ages[i]
            next_phase, next_age = ages[i + 1]
            assert next_age > current_age, (
                f"min_age must increase: '{next_phase}' ({next_age}d) "
                f"must be greater than '{current_phase}' ({current_age}d)"
            )

    def test_regression_008_hot_phase_has_rollover(self, phases):
        """
        Verify hot phase has rollover action with size and age limits.
        Without rollover, a single index grows unbounded.
        """
        hot_actions = phases["hot"]["actions"]
        assert "rollover" in hot_actions, (
            "Hot phase must have rollover action to limit index size"
        )

        rollover = hot_actions["rollover"]
        assert "max_age" in rollover, (
            "Rollover must define max_age for time-based rotation"
        )
        assert "max_primary_shard_size" in rollover, (
            "Rollover must define max_primary_shard_size for size-based rotation"
        )

    def test_regression_008_delete_phase_has_delete_action(self, phases):
        """
        Verify delete phase actually deletes indices.
        A delete phase without a delete action means indices are never cleaned up.
        """
        delete_actions = phases["delete"]["actions"]
        assert "delete" in delete_actions, (
            "Delete phase must have a delete action to remove old indices"
        )

    def test_regression_008_warm_phase_has_optimization_actions(self, phases):
        """
        Verify warm phase includes forcemerge and shrink for storage optimization.
        Without these, warm indices consume excessive disk space.
        """
        warm_actions = phases["warm"]["actions"]
        assert "forcemerge" in warm_actions, (
            "Warm phase should have forcemerge to reduce segment count"
        )
        assert "shrink" in warm_actions, (
            "Warm phase should have shrink to reduce shard count"
        )

    def test_regression_008_cold_phase_reduces_replicas(self, phases):
        """
        Verify cold phase reduces replicas to minimize storage.
        Cold data is rarely accessed and doesn't need replica overhead.
        """
        cold_actions = phases["cold"]["actions"]
        assert "allocate" in cold_actions, (
            "Cold phase must have allocate action to adjust replicas"
        )
        assert cold_actions["allocate"]["number_of_replicas"] == 0, (
            "Cold phase should set replicas to 0 to save disk space"
        )

    def test_regression_008_policy_is_valid_json(self, policy_path):
        """
        Verify the ILM policy file is valid JSON.
        Invalid JSON causes OpenSearch API calls to fail during bootstrap.
        """
        with open(policy_path, 'r', encoding='utf-8') as f:
            content = f.read()

        parsed = json.loads(content)
        assert "policy" in parsed, "ILM policy file must have a 'policy' root key"

    def test_regression_008_delete_min_age_at_least_30_days(self, phases):
        """
        Verify delete phase waits at least 30 days before removing data.
        Premature deletion loses log data needed for compliance and forensics.
        """
        min_age = phases["delete"]["min_age"]
        assert min_age.endswith("d"), (
            f"Delete min_age should be in days, got: {min_age}"
        )
        days = int(min_age[:-1])
        assert days >= 30, (
            f"Delete phase min_age is {days}d, should be at least 30d "
            f"for compliance retention requirements"
        )
