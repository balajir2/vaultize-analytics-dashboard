"""
Pytest Configuration and Fixtures for Analytics API Tests

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import pytest
from typing import Generator, Dict, Any
from unittest.mock import Mock, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.config import Settings


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """
    Create test settings with safe defaults.

    Returns:
        Settings: Test configuration
    """
    return Settings(
        environment="test",
        opensearch_host="localhost",
        opensearch_port=9200,
        opensearch_use_ssl=False,
        api_port=8000,
        log_level="INFO"
    )


@pytest.fixture(scope="function")
def mock_opensearch_client() -> Mock:
    """
    Create a mock OpenSearch client for unit tests.

    Returns:
        Mock: Mocked OpenSearch client
    """
    mock_client = MagicMock()

    # Mock cluster health
    mock_client.cluster.health.return_value = {
        "cluster_name": "test-cluster",
        "status": "green",
        "number_of_nodes": 3,
        "active_shards": 10
    }

    # Mock search response
    mock_client.search.return_value = {
        "took": 5,
        "hits": {
            "total": {"value": 100, "relation": "eq"},
            "hits": [
                {
                    "_index": "logs-2026-02-04",
                    "_id": "1",
                    "_source": {
                        "@timestamp": "2026-02-04T10:00:00Z",
                        "level": "ERROR",
                        "service": "api-service",
                        "message": "Connection timeout"
                    }
                }
            ]
        }
    }

    # Mock indices stats
    mock_client.indices.stats.return_value = {
        "indices": {
            "logs-2026-02-04": {
                "total": {
                    "docs": {"count": 1000, "deleted": 0},
                    "store": {"size_in_bytes": 1048576}
                },
                "primaries": {
                    "docs": {"count": 1000},
                    "store": {"size_in_bytes": 524288}
                }
            }
        }
    }

    # Mock indices list
    mock_client.cat.indices.return_value = [
        {
            "index": "logs-2026-02-04",
            "health": "green",
            "status": "open",
            "docs.count": "1000",
            "store.size": "1mb"
        }
    ]

    # Mock index mappings
    mock_client.indices.get_mapping.return_value = {
        "logs-2026-02-04": {
            "mappings": {
                "properties": {
                    "@timestamp": {"type": "date"},
                    "level": {"type": "keyword"},
                    "service": {"type": "keyword"}
                }
            }
        }
    }

    # Mock index deletion
    mock_client.indices.delete.return_value = {"acknowledged": True}

    return mock_client


@pytest.fixture(scope="function")
def test_client() -> Generator[TestClient, None, None]:
    """
    Create FastAPI test client.

    Yields:
        TestClient: FastAPI test client
    """
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def sample_log_data() -> Dict[str, Any]:
    """
    Sample log data for testing.

    Returns:
        dict: Sample log entry
    """
    return {
        "@timestamp": "2026-02-04T10:00:00Z",
        "level": "ERROR",
        "service": "api-service",
        "message": "Connection timeout after 30s",
        "host": "server-01",
        "environment": "production",
        "request_id": "req-123456",
        "user": "user1",
        "duration_ms": 30000,
        "status_code": 500,
        "stack_trace": "Error at api-service.handler.process()",
        "error_code": "ERR_5001"
    }


@pytest.fixture(scope="function")
def sample_search_response() -> Dict[str, Any]:
    """
    Sample OpenSearch search response.

    Returns:
        dict: Sample search response
    """
    return {
        "took": 5,
        "timed_out": False,
        "hits": {
            "total": {"value": 100, "relation": "eq"},
            "max_score": 1.0,
            "hits": [
                {
                    "_index": "logs-2026-02-04",
                    "_id": "1",
                    "_score": 1.0,
                    "_source": {
                        "@timestamp": "2026-02-04T10:00:00Z",
                        "level": "ERROR",
                        "service": "api-service",
                        "message": "Connection timeout"
                    }
                }
            ]
        }
    }


@pytest.fixture(scope="function")
def sample_aggregation_response() -> Dict[str, Any]:
    """
    Sample OpenSearch aggregation response.

    Returns:
        dict: Sample aggregation response
    """
    return {
        "took": 10,
        "hits": {"total": {"value": 500}},
        "aggregations": {
            "results": {
                "buckets": [
                    {"key": "api-service", "doc_count": 200},
                    {"key": "web-service", "doc_count": 150},
                    {"key": "db-service", "doc_count": 100}
                ]
            }
        }
    }
