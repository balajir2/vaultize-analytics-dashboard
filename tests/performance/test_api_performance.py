"""
Performance Test: API Throughput

Benchmarks Analytics API under concurrent load.

Requires: Analytics API running.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest
import requests

from conftest import timer

pytestmark = pytest.mark.performance


class TestAPIPerformance:
    """Benchmark API throughput under load."""

    def _make_request(self, url: str) -> tuple:
        """Make a request and return (status_code, latency_ms)."""
        with timer() as t:
            resp = requests.get(url, timeout=10)
        return resp.status_code, t["elapsed"] * 1000

    def test_health_endpoint_throughput(self, require_api):
        """Benchmark: Health endpoint throughput (100 sequential requests)."""
        url = f"{require_api}/health/liveness"
        latencies = []

        with timer("100 health requests") as total:
            for _ in range(100):
                status, latency = self._make_request(url)
                assert status == 200
                latencies.append(latency)

        p50 = statistics.median(latencies)
        p95 = sorted(latencies)[int(len(latencies) * 0.95)]
        rps = 100 / total["elapsed"]
        print(f"    Health: p50={p50:.1f}ms, p95={p95:.1f}ms, rps={rps:.0f}")

    def test_concurrent_requests(self, require_api):
        """Benchmark: Concurrent API requests (10 threads, 50 requests each)."""
        url = f"{require_api}/health/liveness"
        total_requests = 50
        max_workers = 10

        results = []
        with timer(f"{total_requests} concurrent requests") as total:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [
                    executor.submit(self._make_request, url)
                    for _ in range(total_requests)
                ]
                for future in as_completed(futures):
                    status, latency = future.result()
                    results.append((status, latency))

        statuses = [r[0] for r in results]
        latencies = [r[1] for r in results]
        success_rate = statuses.count(200) / len(statuses) * 100
        p50 = statistics.median(latencies)
        p95 = sorted(latencies)[int(len(latencies) * 0.95)]
        rps = total_requests / total["elapsed"]

        print(f"    Concurrent: success={success_rate:.0f}%, p50={p50:.1f}ms, p95={p95:.1f}ms, rps={rps:.0f}")
        assert success_rate >= 95, f"Success rate too low: {success_rate}%"

    def test_root_endpoint_throughput(self, require_api):
        """Benchmark: Root endpoint throughput."""
        url = f"{require_api}/"
        latencies = []

        with timer("50 root requests") as total:
            for _ in range(50):
                status, latency = self._make_request(url)
                assert status == 200
                latencies.append(latency)

        p50 = statistics.median(latencies)
        rps = 50 / total["elapsed"]
        print(f"    Root: p50={p50:.1f}ms, rps={rps:.0f}")
