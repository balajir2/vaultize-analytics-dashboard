"""
Query Executor Service

Executes OpenSearch queries defined in alert rules.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import logging
from dataclasses import dataclass
from typing import Optional

from opensearchpy import OpenSearch

from app.models.alert_rule import AlertRule

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Result of executing an alert query."""
    value: float
    took_ms: int
    raw_response: dict
    success: bool
    error: Optional[str] = None


class QueryExecutor:
    """Executes OpenSearch queries for alert rules."""

    def __init__(self, client: OpenSearch):
        self.client = client

    def execute(self, rule: AlertRule) -> QueryResult:
        """
        Execute the query for a rule and return the numeric result.

        For count-based rules (no aggregation): returns hits.total.value
        For aggregation-based rules: extracts value at condition.aggregation_field
        """
        try:
            body = self._build_query_body(rule)
            response = self.client.search(
                index=",".join(rule.query.index),
                body=body,
                size=0,
            )
            took_ms = response.get("took", 0)

            if rule.query.aggregation and rule.condition.aggregation_field:
                value = self._extract_aggregation_result(
                    response, rule.condition.aggregation_field
                )
            else:
                value = self._extract_count_result(response)

            return QueryResult(
                value=value,
                took_ms=took_ms,
                raw_response=response,
                success=True,
            )
        except Exception as e:
            logger.error(f"Query execution failed for rule '{rule.name}': {e}")
            return QueryResult(
                value=0.0,
                took_ms=0,
                raw_response={},
                success=False,
                error=str(e),
            )

    def _build_query_body(self, rule: AlertRule) -> dict:
        """Build the OpenSearch query body from the rule."""
        time_range_filter = {
            "range": {
                rule.query.time_field: {
                    "gte": rule.query.time_range.from_,
                    "lte": rule.query.time_range.to,
                }
            }
        }

        # Combine rule filter with time range
        query_body: dict = {
            "query": {
                "bool": {
                    "must": [
                        rule.query.filter,
                        time_range_filter,
                    ]
                }
            }
        }

        # Add aggregation if present
        if rule.query.aggregation:
            query_body["aggs"] = {"alert_agg": rule.query.aggregation}

        return query_body

    def _extract_count_result(self, response: dict) -> float:
        """Extract hit count from search response."""
        total = response.get("hits", {}).get("total", {})
        if isinstance(total, dict):
            return float(total.get("value", 0))
        return float(total)

    def _extract_aggregation_result(self, response: dict, agg_field: str) -> float:
        """
        Extract aggregation value using dot-notation path.

        Example: "percentiles.95.0" navigates response["aggregations"]["alert_agg"]["values"]["95.0"]
        """
        aggs = response.get("aggregations", {}).get("alert_agg", {})

        # Handle percentiles specifically
        if "values" in aggs:
            parts = agg_field.split(".")
            # For "percentiles.95.0", extract from values["95.0"]
            if len(parts) >= 2:
                key = ".".join(parts[1:])
                return float(aggs["values"].get(key, 0))

        # Handle simple aggregations (avg, sum, min, max)
        if "value" in aggs:
            return float(aggs["value"])

        logger.warning(f"Could not extract aggregation value for field '{agg_field}'")
        return 0.0
