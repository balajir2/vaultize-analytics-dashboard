"""
Tests for query_executor.py

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

from unittest.mock import MagicMock

from app.services.query_executor import QueryExecutor


class TestQueryExecutor:
    """Tests for the QueryExecutor class."""

    def test_count_query_success(self, mock_opensearch, sample_count_rule):
        mock_opensearch.search.return_value = {
            "took": 12,
            "hits": {"total": {"value": 150, "relation": "eq"}, "hits": []},
        }
        executor = QueryExecutor(mock_opensearch)
        result = executor.execute(sample_count_rule)

        assert result.success is True
        assert result.value == 150.0
        assert result.took_ms == 12

    def test_count_query_zero_hits(self, mock_opensearch, sample_count_rule):
        mock_opensearch.search.return_value = {
            "took": 3,
            "hits": {"total": {"value": 0, "relation": "eq"}, "hits": []},
        }
        executor = QueryExecutor(mock_opensearch)
        result = executor.execute(sample_count_rule)

        assert result.success is True
        assert result.value == 0.0

    def test_aggregation_percentiles_query(self, mock_opensearch, sample_agg_rule):
        mock_opensearch.search.return_value = {
            "took": 20,
            "hits": {"total": {"value": 500, "relation": "eq"}, "hits": []},
            "aggregations": {
                "alert_agg": {
                    "values": {"95.0": 1250.5}
                }
            },
        }
        executor = QueryExecutor(mock_opensearch)
        result = executor.execute(sample_agg_rule)

        assert result.success is True
        assert result.value == 1250.5

    def test_aggregation_simple_value(self, mock_opensearch, sample_agg_rule):
        """Test simple aggregation (avg/sum/min/max) with value field."""
        sample_agg_rule.condition.aggregation_field = "avg"
        sample_agg_rule.query.aggregation = {"avg": {"field": "response_time"}}
        mock_opensearch.search.return_value = {
            "took": 15,
            "hits": {"total": {"value": 100, "relation": "eq"}, "hits": []},
            "aggregations": {
                "alert_agg": {"value": 456.7}
            },
        }
        executor = QueryExecutor(mock_opensearch)
        result = executor.execute(sample_agg_rule)

        assert result.success is True
        assert result.value == 456.7

    def test_query_failure(self, mock_opensearch, sample_count_rule):
        mock_opensearch.search.side_effect = Exception("connection timeout")
        executor = QueryExecutor(mock_opensearch)
        result = executor.execute(sample_count_rule)

        assert result.success is False
        assert result.error == "connection timeout"
        assert result.value == 0.0

    def test_query_body_includes_time_range(self, mock_opensearch, sample_count_rule):
        mock_opensearch.search.return_value = {
            "took": 5,
            "hits": {"total": {"value": 0, "relation": "eq"}, "hits": []},
        }
        executor = QueryExecutor(mock_opensearch)
        executor.execute(sample_count_rule)

        call_args = mock_opensearch.search.call_args
        body = call_args[1]["body"] if "body" in call_args[1] else call_args[0][0]
        query_must = body["query"]["bool"]["must"]
        # Should have both the rule filter and the time range filter
        assert len(query_must) == 2
        # Second element should be the time range
        range_filter = query_must[1]
        assert "range" in range_filter
        assert "@timestamp" in range_filter["range"]

    def test_query_body_includes_aggregation(self, mock_opensearch, sample_agg_rule):
        mock_opensearch.search.return_value = {
            "took": 5,
            "hits": {"total": {"value": 0, "relation": "eq"}, "hits": []},
            "aggregations": {"alert_agg": {"values": {"95.0": 0}}},
        }
        executor = QueryExecutor(mock_opensearch)
        executor.execute(sample_agg_rule)

        call_args = mock_opensearch.search.call_args
        body = call_args[1]["body"] if "body" in call_args[1] else call_args[0][0]
        assert "aggs" in body
        assert "alert_agg" in body["aggs"]

    def test_query_uses_correct_index(self, mock_opensearch, sample_count_rule):
        mock_opensearch.search.return_value = {
            "took": 5,
            "hits": {"total": {"value": 0, "relation": "eq"}, "hits": []},
        }
        executor = QueryExecutor(mock_opensearch)
        executor.execute(sample_count_rule)

        call_args = mock_opensearch.search.call_args
        assert call_args[1]["index"] == "logs-*"

    def test_query_uses_size_zero(self, mock_opensearch, sample_count_rule):
        mock_opensearch.search.return_value = {
            "took": 5,
            "hits": {"total": {"value": 0, "relation": "eq"}, "hits": []},
        }
        executor = QueryExecutor(mock_opensearch)
        executor.execute(sample_count_rule)

        call_args = mock_opensearch.search.call_args
        assert call_args[1]["size"] == 0

    def test_count_result_integer_total(self, mock_opensearch, sample_count_rule):
        """Handle OpenSearch returning total as integer instead of dict."""
        mock_opensearch.search.return_value = {
            "took": 5,
            "hits": {"total": 42, "hits": []},
        }
        executor = QueryExecutor(mock_opensearch)
        result = executor.execute(sample_count_rule)
        assert result.value == 42.0
