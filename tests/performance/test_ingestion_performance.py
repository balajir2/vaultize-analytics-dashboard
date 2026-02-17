"""
Performance Test: Ingestion Throughput

Benchmarks bulk indexing performance at various document counts.

Requires: OpenSearch running.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import uuid
from datetime import datetime, timezone

import pytest
import requests

from conftest import timer

pytestmark = pytest.mark.performance


class TestIngestionPerformance:
    """Benchmark bulk document indexing."""

    def _generate_bulk_body(self, index: str, count: int) -> str:
        """Generate NDJSON bulk body."""
        lines = []
        base_time = datetime(2026, 2, 17, 12, 0, 0, tzinfo=timezone.utc)
        for i in range(count):
            lines.append(f'{{"index": {{"_index": "{index}"}}}}')
            lines.append(
                f'{{"@timestamp": "{base_time.isoformat()}", '
                f'"message": "Performance test document {i}", '
                f'"level": "INFO", "service": "perf-test", '
                f'"request_id": "{uuid.uuid4().hex}"}}'
            )
        return "\n".join(lines) + "\n"

    def test_bulk_index_1k_documents(self, require_opensearch, perf_index):
        """Benchmark: Index 1,000 documents."""
        body = self._generate_bulk_body(perf_index, 1000)

        with timer("1K docs bulk index") as t:
            resp = requests.post(
                f"{require_opensearch}/_bulk?refresh=true",
                data=body,
                headers={"Content-Type": "application/x-ndjson"},
                timeout=60,
            )

        assert resp.status_code == 200
        assert not resp.json().get("errors", False)
        print(f"    Throughput: {1000 / t['elapsed']:.0f} docs/sec")

    def test_bulk_index_10k_documents(self, require_opensearch, perf_index):
        """Benchmark: Index 10,000 documents."""
        body = self._generate_bulk_body(perf_index, 10000)

        with timer("10K docs bulk index") as t:
            resp = requests.post(
                f"{require_opensearch}/_bulk?refresh=true",
                data=body,
                headers={"Content-Type": "application/x-ndjson"},
                timeout=120,
            )

        assert resp.status_code == 200
        assert not resp.json().get("errors", False)
        print(f"    Throughput: {10000 / t['elapsed']:.0f} docs/sec")

    def test_bulk_index_100k_documents(self, require_opensearch, perf_index):
        """Benchmark: Index 100,000 documents in batches of 10K."""
        total = 100000
        batch_size = 10000
        batches = total // batch_size

        with timer(f"100K docs bulk index ({batches} batches)") as t:
            for _ in range(batches):
                body = self._generate_bulk_body(perf_index, batch_size)
                resp = requests.post(
                    f"{require_opensearch}/_bulk",
                    data=body,
                    headers={"Content-Type": "application/x-ndjson"},
                    timeout=120,
                )
                assert resp.status_code == 200

            # Final refresh
            requests.post(f"{require_opensearch}/{perf_index}/_refresh", timeout=30)

        print(f"    Throughput: {total / t['elapsed']:.0f} docs/sec")

        # Verify count
        resp = requests.get(f"{require_opensearch}/{perf_index}/_count", timeout=10)
        assert resp.json()["count"] == total
