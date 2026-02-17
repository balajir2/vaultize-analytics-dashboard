"""
Performance Test: Query Latency

Benchmarks search and aggregation query performance.

Requires: OpenSearch running with indexed data.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import statistics
import uuid

import pytest
import requests

from conftest import timer

pytestmark = pytest.mark.performance


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="class")
def indexed_data(require_opensearch):
    """Create an index with 10K documents for query testing."""
    index_name = f"perf-query-{uuid.uuid4().hex[:8]}"
    levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    services = ["api", "auth", "worker", "scheduler", "gateway"]

    # Bulk index 10K documents
    batch_size = 5000
    for batch_start in range(0, 10000, batch_size):
        lines = []
        for i in range(batch_start, batch_start + batch_size):
            lines.append(f'{{"index": {{"_index": "{index_name}"}}}}')
            lines.append(
                f'{{"@timestamp": "2026-02-17T{(i // 3600) % 24:02d}:{(i // 60) % 60:02d}:{i % 60:02d}Z", '
                f'"message": "Query perf test doc {i}", '
                f'"level": "{levels[i % len(levels)]}", '
                f'"service": "{services[i % len(services)]}", '
                f'"response_time_ms": {50 + (i % 500)}}}'
            )
        body = "\n".join(lines) + "\n"
        requests.post(
            f"{require_opensearch}/_bulk",
            data=body,
            headers={"Content-Type": "application/x-ndjson"},
            timeout=120,
        )

    requests.post(f"{require_opensearch}/{index_name}/_refresh", timeout=30)

    yield index_name

    requests.delete(f"{require_opensearch}/{index_name}", timeout=10)


# ============================================================================
# Tests
# ============================================================================

class TestQueryPerformance:
    """Benchmark search and aggregation queries."""

    def _run_query_n_times(self, url: str, body: dict, n: int = 10) -> list:
        """Run a query N times and return latency list."""
        latencies = []
        for _ in range(n):
            with timer() as t:
                resp = requests.post(url, json=body, timeout=30)
            assert resp.status_code == 200
            latencies.append(t["elapsed"] * 1000)  # Convert to ms
        return latencies

    def test_match_all_query_latency(self, require_opensearch, indexed_data):
        """Benchmark: match_all query latency."""
        url = f"{require_opensearch}/{indexed_data}/_search"
        body = {"query": {"match_all": {}}, "size": 100}

        latencies = self._run_query_n_times(url, body)
        p50 = statistics.median(latencies)
        p95 = sorted(latencies)[int(len(latencies) * 0.95)]
        print(f"    match_all: p50={p50:.1f}ms, p95={p95:.1f}ms")

    def test_term_query_latency(self, require_opensearch, indexed_data):
        """Benchmark: term query latency."""
        url = f"{require_opensearch}/{indexed_data}/_search"
        body = {"query": {"term": {"level.keyword": "ERROR"}}, "size": 100}

        latencies = self._run_query_n_times(url, body)
        p50 = statistics.median(latencies)
        p95 = sorted(latencies)[int(len(latencies) * 0.95)]
        print(f"    term query: p50={p50:.1f}ms, p95={p95:.1f}ms")

    def test_aggregation_latency(self, require_opensearch, indexed_data):
        """Benchmark: terms aggregation latency."""
        url = f"{require_opensearch}/{indexed_data}/_search"
        body = {
            "size": 0,
            "aggs": {
                "by_level": {"terms": {"field": "level.keyword", "size": 10}},
                "by_service": {"terms": {"field": "service.keyword", "size": 10}},
            },
        }

        latencies = self._run_query_n_times(url, body)
        p50 = statistics.median(latencies)
        p95 = sorted(latencies)[int(len(latencies) * 0.95)]
        print(f"    aggregation: p50={p50:.1f}ms, p95={p95:.1f}ms")

    def test_date_range_query_latency(self, require_opensearch, indexed_data):
        """Benchmark: date range query latency."""
        url = f"{require_opensearch}/{indexed_data}/_search"
        body = {
            "query": {
                "range": {
                    "@timestamp": {
                        "gte": "2026-02-17T00:00:00Z",
                        "lte": "2026-02-17T12:00:00Z",
                    }
                }
            },
            "size": 100,
        }

        latencies = self._run_query_n_times(url, body)
        p50 = statistics.median(latencies)
        p95 = sorted(latencies)[int(len(latencies) * 0.95)]
        print(f"    date_range: p50={p50:.1f}ms, p95={p95:.1f}ms")
