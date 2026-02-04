"""
Unit Tests for Pydantic Models

Tests all Pydantic models used in the Analytics API for validation,
serialization, and edge cases.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from app.models.common import APIResponse, PaginationParams, PaginationMeta, TimeRange
from app.models.health import HealthResponse, OpenSearchHealthResponse
from app.models.search import (
    SearchRequest,
    SearchHit,
    SearchResponse,
    AggregationRequest,
    AggregationBucket,
    AggregationResponse
)


# ============================================================================
# Common Models Tests
# ============================================================================

class TestAPIResponse:
    """Test APIResponse model"""

    def test_api_response_success(self):
        """Test successful API response creation"""
        response = APIResponse(
            status="success",
            data={"key": "value"},
            message="Operation completed"
        )
        assert response.status == "success"
        assert response.data == {"key": "value"}
        assert response.message == "Operation completed"

    def test_api_response_minimal(self):
        """Test API response with minimal fields"""
        response = APIResponse[dict](status="success", data={})
        assert response.status == "success"
        assert response.data == {}
        assert response.message is None

    def test_api_response_serialization(self):
        """Test API response JSON serialization"""
        response = APIResponse(status="success", data={"count": 42})
        json_data = response.model_dump()
        assert json_data["status"] == "success"
        assert json_data["data"]["count"] == 42


class TestPaginationParams:
    """Test PaginationParams model"""

    def test_pagination_defaults(self):
        """Test default pagination values"""
        params = PaginationParams()
        assert params.page == 1
        assert params.size == 100
        assert params.offset == 0

    def test_pagination_offset_calculation(self):
        """Test offset calculation from page and size"""
        params = PaginationParams(page=3, size=50)
        assert params.offset == 100  # (3-1) * 50

    def test_pagination_validation_page_minimum(self):
        """Test page number must be >= 1"""
        with pytest.raises(ValidationError):
            PaginationParams(page=0)

    def test_pagination_validation_size_minimum(self):
        """Test size must be >= 1"""
        with pytest.raises(ValidationError):
            PaginationParams(size=0)

    def test_pagination_validation_size_maximum(self):
        """Test size must be <= 10000"""
        with pytest.raises(ValidationError):
            PaginationParams(size=10001)


class TestPaginationMeta:
    """Test PaginationMeta model"""

    def test_pagination_metadata_creation(self):
        """Test pagination metadata creation"""
        meta = PaginationMeta(
            page=2,
            size=50,
            total=150,
            total_pages=3
        )
        assert meta.page == 2
        assert meta.size == 50
        assert meta.total == 150
        assert meta.total_pages == 3


# ============================================================================
# Health Models Tests
# ============================================================================

class TestOpenSearchHealthResponse:
    """Test OpenSearchHealthResponse model"""

    def test_opensearch_health_creation(self):
        """Test OpenSearch health response creation"""
        health = OpenSearchHealthResponse(
            status="green",
            cluster_name="test-cluster",
            timed_out=False,
            number_of_nodes=3,
            number_of_data_nodes=3,
            active_primary_shards=15,
            active_shards=30,
            relocating_shards=0,
            initializing_shards=0,
            unassigned_shards=0
        )
        assert health.status == "green"
        assert health.cluster_name == "test-cluster"
        assert health.number_of_nodes == 3


class TestHealthResponse:
    """Test HealthResponse model"""

    def test_health_response_full(self):
        """Test full health response"""
        health = HealthResponse(
            status="healthy",
            version="0.2.1",
            environment="test",
            opensearch=OpenSearchHealthResponse(
                status="green",
                cluster_name="test",
                timed_out=False,
                number_of_nodes=3,
                number_of_data_nodes=3,
                active_primary_shards=10,
                active_shards=20,
                relocating_shards=0,
                initializing_shards=0,
                unassigned_shards=0
            )
        )
        assert health.status == "healthy"
        assert health.opensearch.status == "green"

    def test_health_response_without_opensearch(self):
        """Test health response without OpenSearch"""
        health = HealthResponse(
            status="degraded",
            version="0.2.1",
            environment="test"
        )
        assert health.status == "degraded"
        assert health.opensearch is None


# ============================================================================
# Search Models Tests
# ============================================================================

class TestTimeRange:
    """Test TimeRange model"""

    def test_time_range_both_bounds(self):
        """Test time range with start and end"""
        time_range = TimeRange(
            field="@timestamp",
            start="2026-02-04T00:00:00Z",
            end="2026-02-04T23:59:59Z"
        )
        assert time_range.field == "@timestamp"
        assert time_range.start == "2026-02-04T00:00:00Z"
        assert time_range.end == "2026-02-04T23:59:59Z"

    def test_time_range_start_only(self):
        """Test time range with only start"""
        time_range = TimeRange(field="@timestamp", start="now-24h")
        assert time_range.start == "now-24h"
        assert time_range.end is None

    def test_time_range_relative_dates(self):
        """Test time range with relative dates"""
        time_range = TimeRange(
            field="@timestamp",
            start="now-7d",
            end="now"
        )
        assert time_range.start == "now-7d"
        assert time_range.end == "now"


class TestSearchRequest:
    """Test SearchRequest model"""

    def test_search_request_defaults(self):
        """Test search request with default values"""
        request = SearchRequest()
        assert request.query is None
        assert request.indices == ["logs-*"]
        assert request.size == 100
        assert request.from_ == 0

    def test_search_request_full(self):
        """Test search request with all fields"""
        request = SearchRequest(
            query="level:ERROR",
            indices=["logs-2026-02-04"],
            time_range=TimeRange(field="@timestamp", start="now-1h"),
            fields=["message", "service"],
            sort=[{"@timestamp": "desc"}],
            size=50,
            **{"from": 10}  # Using from as keyword arg
        )
        assert request.query == "level:ERROR"
        assert request.size == 50
        assert request.from_ == 10

    def test_search_request_validation_size(self):
        """Test search request size validation"""
        with pytest.raises(ValidationError):
            SearchRequest(size=20000)  # Exceeds max 10000


class TestSearchHit:
    """Test SearchHit model"""

    def test_search_hit_creation(self):
        """Test search hit creation"""
        hit = SearchHit(
            index="logs-2026-02-04",
            id="abc123",
            score=1.5,
            source={
                "@timestamp": "2026-02-04T10:00:00Z",
                "level": "ERROR",
                "message": "Test error"
            }
        )
        assert hit.index == "logs-2026-02-04"
        assert hit.id == "abc123"
        assert hit.score == 1.5
        assert hit.source["level"] == "ERROR"


class TestSearchResponse:
    """Test SearchResponse model"""

    def test_search_response_creation(self):
        """Test search response creation"""
        response = SearchResponse(
            hits=[
                SearchHit(
                    index="logs-2026-02-04",
                    id="1",
                    score=1.0,
                    source={"message": "test"}
                )
            ],
            total=100,
            took=5,
            pagination=PaginationMeta(page=1, size=100, total=100, total_pages=1)
        )
        assert len(response.hits) == 1
        assert response.total == 100
        assert response.took == 5


# ============================================================================
# Aggregation Models Tests
# ============================================================================

class TestAggregationRequest:
    """Test AggregationRequest model"""

    def test_aggregation_request_terms(self):
        """Test terms aggregation request"""
        request = AggregationRequest(
            query="level:ERROR",
            indices=["logs-*"],
            agg_type="terms",
            field="service",
            size=10
        )
        assert request.agg_type == "terms"
        assert request.field == "service"
        assert request.size == 10

    def test_aggregation_request_date_histogram(self):
        """Test date_histogram aggregation request"""
        request = AggregationRequest(
            indices=["logs-*"],
            agg_type="date_histogram",
            field="@timestamp",
            interval="1h"
        )
        assert request.agg_type == "date_histogram"
        assert request.interval == "1h"

    def test_aggregation_request_with_time_range(self):
        """Test aggregation request with time range"""
        request = AggregationRequest(
            indices=["logs-*"],
            agg_type="stats",
            field="duration_ms",
            time_range=TimeRange(field="@timestamp", start="now-1d")
        )
        assert request.time_range.start == "now-1d"


class TestAggregationBucket:
    """Test AggregationBucket model"""

    def test_aggregation_bucket_simple(self):
        """Test simple aggregation bucket"""
        bucket = AggregationBucket(
            key="api-service",
            doc_count=150
        )
        assert bucket.key == "api-service"
        assert bucket.doc_count == 150
        assert bucket.data is None

    def test_aggregation_bucket_with_data(self):
        """Test aggregation bucket with additional data"""
        bucket = AggregationBucket(
            key="stats",
            doc_count=1000,
            data={"min": 10, "max": 5000, "avg": 250.5}
        )
        assert bucket.data["avg"] == 250.5


class TestAggregationResponse:
    """Test AggregationResponse model"""

    def test_aggregation_response_creation(self):
        """Test aggregation response creation"""
        response = AggregationResponse(
            buckets=[
                AggregationBucket(key="service1", doc_count=100),
                AggregationBucket(key="service2", doc_count=50)
            ],
            total=500,
            took=10
        )
        assert len(response.buckets) == 2
        assert response.total == 500
        assert response.took == 10

    def test_aggregation_response_empty_buckets(self):
        """Test aggregation response with no buckets"""
        response = AggregationResponse(
            buckets=[],
            total=0,
            took=2
        )
        assert len(response.buckets) == 0
        assert response.total == 0
