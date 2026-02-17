"""
Shared fixtures for alerting service tests.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

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
from app.services.query_executor import QueryResult


# ---------------------------------------------------------------------------
# Sample Alert Rule (count-based, like high-error-rate.json)
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_count_rule():
    """A count-based alert rule (high error rate style)."""
    return AlertRule(
        name="High Error Rate",
        description="Alert when error log count exceeds threshold",
        enabled=True,
        schedule=AlertSchedule(interval="5m"),
        query=AlertQuery(
            index=["logs-*"],
            time_field="@timestamp",
            time_range=AlertQueryTimeRange(**{"from": "now-5m", "to": "now"}),
            filter={"bool": {"must": [{"match": {"level": "ERROR"}}]}},
        ),
        condition=AlertCondition(type="threshold", operator="gt", value=100),
        actions=[
            AlertAction(
                type="webhook",
                name="slack_notification",
                webhook=WebhookConfig(
                    url="http://hooks.example.com/alert",
                    method="POST",
                    headers={"Content-Type": "application/json"},
                    body={
                        "text": "High Error Rate",
                        "count": "{{alert.result_count}}",
                    },
                ),
            )
        ],
        throttle=AlertThrottle(value=15, unit="minutes"),
        metadata=AlertMetadata(
            severity="high",
            category="application",
            owner="platform-team",
            tags=["errors"],
        ),
    )


# ---------------------------------------------------------------------------
# Sample Alert Rule (aggregation-based, like slow-api-response.json)
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_agg_rule():
    """An aggregation-based alert rule (slow API response style)."""
    return AlertRule(
        name="Slow API Response",
        description="Alert when P95 response time exceeds threshold",
        enabled=True,
        schedule=AlertSchedule(interval="5m"),
        query=AlertQuery(
            index=["logs-*"],
            time_field="@timestamp",
            time_range=AlertQueryTimeRange(**{"from": "now-5m", "to": "now"}),
            filter={"bool": {"must": [{"exists": {"field": "http.response_time_ms"}}]}},
            aggregation={"percentiles": {"field": "http.response_time_ms", "percents": [95]}},
        ),
        condition=AlertCondition(
            type="threshold",
            operator="gt",
            value=1000,
            aggregation_field="percentiles.95.0",
        ),
        actions=[
            AlertAction(
                type="webhook",
                name="perf_alert",
                webhook=WebhookConfig(
                    url="http://hooks.example.com/perf",
                    method="POST",
                    body={"text": "Slow API: {{alert.p95_response_time}}ms"},
                ),
            )
        ],
        throttle=AlertThrottle(value=10, unit="minutes"),
        metadata=AlertMetadata(
            severity="medium",
            category="performance",
            owner="api-team",
            tags=["latency"],
        ),
    )


@pytest.fixture
def disabled_rule(sample_count_rule):
    """A disabled alert rule."""
    sample_count_rule.enabled = False
    sample_count_rule.name = "Disabled Rule"
    return sample_count_rule


# ---------------------------------------------------------------------------
# Query results
# ---------------------------------------------------------------------------

@pytest.fixture
def count_query_result():
    """Successful count-based query result."""
    return QueryResult(value=150.0, took_ms=12, raw_response={}, success=True)


@pytest.fixture
def low_count_query_result():
    """Count-based query result below threshold."""
    return QueryResult(value=50.0, took_ms=8, raw_response={}, success=True)


@pytest.fixture
def failed_query_result():
    """Failed query result."""
    return QueryResult(
        value=0.0, took_ms=0, raw_response={}, success=False, error="connection timeout"
    )


# ---------------------------------------------------------------------------
# Mock OpenSearch client
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_opensearch():
    """Mock OpenSearch client with common methods."""
    client = MagicMock()
    client.indices.exists.return_value = True
    client.indices.create.return_value = {"acknowledged": True}
    client.index.return_value = {"result": "created"}
    client.search.return_value = {
        "hits": {"total": {"value": 0, "relation": "eq"}, "hits": []},
        "took": 5,
    }
    client.cluster.health.return_value = {
        "status": "green",
        "number_of_nodes": 3,
    }
    return client


# ---------------------------------------------------------------------------
# Temp rules directory
# ---------------------------------------------------------------------------

@pytest.fixture
def rules_dir_with_files():
    """Temporary directory containing rule JSON files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write count-based rule
        count_data = {
            "name": "High Error Rate",
            "description": "Error count alert",
            "enabled": True,
            "schedule": {"interval": "5m"},
            "query": {
                "index": ["logs-*"],
                "time_field": "@timestamp",
                "time_range": {"from": "now-5m", "to": "now"},
                "filter": {"bool": {"must": [{"match": {"level": "ERROR"}}]}},
            },
            "condition": {"type": "threshold", "operator": "gt", "value": 100},
            "actions": [
                {
                    "type": "webhook",
                    "name": "slack",
                    "webhook": {
                        "url": "http://hooks.example.com/alert",
                        "method": "POST",
                        "body": {"text": "Alert fired"},
                    },
                }
            ],
            "throttle": {"value": 15, "unit": "minutes"},
            "metadata": {
                "severity": "high",
                "category": "application",
                "owner": "platform-team",
                "tags": ["errors"],
            },
        }
        with open(Path(tmpdir) / "high-error-rate.json", "w") as f:
            json.dump(count_data, f)

        # Write agg-based rule
        agg_data = {
            "name": "Slow API Response",
            "description": "P95 latency alert",
            "enabled": True,
            "schedule": {"interval": "5m"},
            "query": {
                "index": ["logs-*"],
                "time_field": "@timestamp",
                "time_range": {"from": "now-5m", "to": "now"},
                "filter": {"bool": {"must": [{"exists": {"field": "http.response_time_ms"}}]}},
                "aggregation": {"percentiles": {"field": "http.response_time_ms", "percents": [95]}},
            },
            "condition": {
                "type": "threshold",
                "operator": "gt",
                "value": 1000,
                "aggregation_field": "percentiles.95.0",
            },
            "actions": [
                {
                    "type": "webhook",
                    "name": "perf_alert",
                    "webhook": {
                        "url": "http://hooks.example.com/perf",
                        "method": "POST",
                        "body": {"text": "Slow response"},
                    },
                }
            ],
            "throttle": {"value": 10, "unit": "minutes"},
            "metadata": {
                "severity": "medium",
                "category": "performance",
                "owner": "api-team",
                "tags": ["latency"],
            },
        }
        with open(Path(tmpdir) / "slow-api-response.json", "w") as f:
            json.dump(agg_data, f)

        # Write a disabled rule
        disabled_data = dict(count_data)
        disabled_data["name"] = "Disabled Rule"
        disabled_data["enabled"] = False
        with open(Path(tmpdir) / "disabled-rule.json", "w") as f:
            json.dump(disabled_data, f)

        yield tmpdir
