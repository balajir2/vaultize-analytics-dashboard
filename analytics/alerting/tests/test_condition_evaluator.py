"""
Tests for condition_evaluator.py

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import pytest

from app.models.alert_rule import AlertCondition, AlertRule
from app.services.condition_evaluator import ConditionEvaluator
from app.services.query_executor import QueryResult


class TestConditionEvaluator:
    """Tests for the ConditionEvaluator class."""

    def setup_method(self):
        self.evaluator = ConditionEvaluator()

    def _make_rule_with_condition(self, operator: str, value: float, sample_count_rule) -> AlertRule:
        """Helper to create a rule with a specific condition."""
        sample_count_rule.condition = AlertCondition(
            type="threshold", operator=operator, value=value
        )
        return sample_count_rule

    def _make_query_result(self, value: float) -> QueryResult:
        return QueryResult(value=value, took_ms=5, raw_response={}, success=True)

    # --- gt operator ---

    def test_gt_true(self, sample_count_rule):
        rule = self._make_rule_with_condition("gt", 100, sample_count_rule)
        result = self.evaluator.evaluate(rule, self._make_query_result(150))
        assert result.condition_met is True
        assert result.operator == "gt"

    def test_gt_false_equal(self, sample_count_rule):
        rule = self._make_rule_with_condition("gt", 100, sample_count_rule)
        result = self.evaluator.evaluate(rule, self._make_query_result(100))
        assert result.condition_met is False

    def test_gt_false_below(self, sample_count_rule):
        rule = self._make_rule_with_condition("gt", 100, sample_count_rule)
        result = self.evaluator.evaluate(rule, self._make_query_result(50))
        assert result.condition_met is False

    # --- gte operator ---

    def test_gte_true_above(self, sample_count_rule):
        rule = self._make_rule_with_condition("gte", 100, sample_count_rule)
        result = self.evaluator.evaluate(rule, self._make_query_result(150))
        assert result.condition_met is True

    def test_gte_true_equal(self, sample_count_rule):
        rule = self._make_rule_with_condition("gte", 100, sample_count_rule)
        result = self.evaluator.evaluate(rule, self._make_query_result(100))
        assert result.condition_met is True

    def test_gte_false(self, sample_count_rule):
        rule = self._make_rule_with_condition("gte", 100, sample_count_rule)
        result = self.evaluator.evaluate(rule, self._make_query_result(99))
        assert result.condition_met is False

    # --- lt operator ---

    def test_lt_true(self, sample_count_rule):
        rule = self._make_rule_with_condition("lt", 100, sample_count_rule)
        result = self.evaluator.evaluate(rule, self._make_query_result(50))
        assert result.condition_met is True

    def test_lt_false_equal(self, sample_count_rule):
        rule = self._make_rule_with_condition("lt", 100, sample_count_rule)
        result = self.evaluator.evaluate(rule, self._make_query_result(100))
        assert result.condition_met is False

    # --- lte operator ---

    def test_lte_true_below(self, sample_count_rule):
        rule = self._make_rule_with_condition("lte", 100, sample_count_rule)
        result = self.evaluator.evaluate(rule, self._make_query_result(50))
        assert result.condition_met is True

    def test_lte_true_equal(self, sample_count_rule):
        rule = self._make_rule_with_condition("lte", 100, sample_count_rule)
        result = self.evaluator.evaluate(rule, self._make_query_result(100))
        assert result.condition_met is True

    def test_lte_false(self, sample_count_rule):
        rule = self._make_rule_with_condition("lte", 100, sample_count_rule)
        result = self.evaluator.evaluate(rule, self._make_query_result(101))
        assert result.condition_met is False

    # --- eq operator ---

    def test_eq_true(self, sample_count_rule):
        rule = self._make_rule_with_condition("eq", 100, sample_count_rule)
        result = self.evaluator.evaluate(rule, self._make_query_result(100))
        assert result.condition_met is True

    def test_eq_false(self, sample_count_rule):
        rule = self._make_rule_with_condition("eq", 100, sample_count_rule)
        result = self.evaluator.evaluate(rule, self._make_query_result(101))
        assert result.condition_met is False

    # --- Edge cases ---

    def test_zero_value(self, sample_count_rule):
        rule = self._make_rule_with_condition("gt", 0, sample_count_rule)
        result = self.evaluator.evaluate(rule, self._make_query_result(0))
        assert result.condition_met is False

    def test_negative_value(self, sample_count_rule):
        rule = self._make_rule_with_condition("lt", 0, sample_count_rule)
        result = self.evaluator.evaluate(rule, self._make_query_result(-5))
        assert result.condition_met is True

    def test_unknown_operator(self, sample_count_rule):
        rule = self._make_rule_with_condition("invalid_op", 100, sample_count_rule)
        result = self.evaluator.evaluate(rule, self._make_query_result(150))
        assert result.condition_met is False
        assert "Unknown operator" in result.message

    def test_result_values_propagated(self, sample_count_rule):
        rule = self._make_rule_with_condition("gt", 100, sample_count_rule)
        result = self.evaluator.evaluate(rule, self._make_query_result(150))
        assert result.actual_value == 150.0
        assert result.threshold == 100.0
        assert result.operator == "gt"

    def test_message_contains_rule_name(self, sample_count_rule):
        rule = self._make_rule_with_condition("gt", 100, sample_count_rule)
        result = self.evaluator.evaluate(rule, self._make_query_result(150))
        assert sample_count_rule.name in result.message
