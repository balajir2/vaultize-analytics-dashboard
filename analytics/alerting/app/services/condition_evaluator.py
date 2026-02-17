"""
Condition Evaluator Service

Compares query results against threshold conditions.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import operator
from dataclasses import dataclass

from app.models.alert_rule import AlertRule
from app.services.query_executor import QueryResult


@dataclass
class EvaluationResult:
    """Result of evaluating a condition."""
    condition_met: bool
    actual_value: float
    threshold: float
    operator: str
    message: str


OPERATORS = {
    "gt": operator.gt,
    "gte": operator.ge,
    "lt": operator.lt,
    "lte": operator.le,
    "eq": operator.eq,
}


class ConditionEvaluator:
    """Evaluates threshold conditions against query results."""

    def evaluate(self, rule: AlertRule, query_result: QueryResult) -> EvaluationResult:
        """Compare query_result.value against rule.condition using the configured operator."""
        op_func = OPERATORS.get(rule.condition.operator)
        if op_func is None:
            return EvaluationResult(
                condition_met=False,
                actual_value=query_result.value,
                threshold=rule.condition.value,
                operator=rule.condition.operator,
                message=f"Unknown operator: {rule.condition.operator}",
            )

        condition_met = op_func(query_result.value, rule.condition.value)

        if condition_met:
            message = (
                f"Alert '{rule.name}': {query_result.value} "
                f"{rule.condition.operator} {rule.condition.value} = True"
            )
        else:
            message = (
                f"Alert '{rule.name}': {query_result.value} "
                f"{rule.condition.operator} {rule.condition.value} = False"
            )

        return EvaluationResult(
            condition_met=condition_met,
            actual_value=query_result.value,
            threshold=rule.condition.value,
            operator=rule.condition.operator,
            message=message,
        )
