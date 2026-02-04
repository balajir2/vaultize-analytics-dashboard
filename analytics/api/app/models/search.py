"""
Search Models

Pydantic models for search and aggregation endpoints.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.models.common import PaginationMeta, TimeRange


class SearchRequest(BaseModel):
    """
    Log search request parameters.
    """
    query: Optional[str] = Field(
        default=None,
        description="Lucene query string (e.g., 'level:ERROR AND message:timeout')"
    )
    indices: List[str] = Field(
        default=["logs-*"],
        description="List of index patterns to search"
    )
    time_range: Optional[TimeRange] = Field(
        default=None,
        description="Time range filter"
    )
    fields: Optional[List[str]] = Field(
        default=None,
        description="Specific fields to return (default: all)"
    )
    sort: Optional[List[Dict[str, str]]] = Field(
        default=[{"@timestamp": "desc"}],
        description="Sort order (e.g., [{'@timestamp': 'desc'}])"
    )
    size: int = Field(default=100, ge=1, le=10000, description="Number of results to return")
    from_: int = Field(default=0, ge=0, alias="from", description="Offset for pagination")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "query": "level:ERROR AND service:api",
                "indices": ["logs-2026-02-*"],
                "time_range": {
                    "start": "now-1h",
                    "end": "now",
                    "field": "@timestamp"
                },
                "fields": ["@timestamp", "level", "message", "service"],
                "sort": [{"@timestamp": "desc"}],
                "size": 100,
                "from": 0
            }
        }


class SearchHit(BaseModel):
    """
    Individual search result hit.
    """
    index: str = Field(..., description="Index name")
    id: str = Field(..., description="Document ID")
    score: Optional[float] = Field(default=None, description="Relevance score")
    source: Dict[str, Any] = Field(..., description="Document source data")

    class Config:
        json_schema_extra = {
            "example": {
                "index": "logs-2026-02-04",
                "id": "abc123",
                "score": 1.0,
                "source": {
                    "@timestamp": "2026-02-04T10:30:00Z",
                    "level": "ERROR",
                    "message": "Connection timeout",
                    "service": "api",
                    "host": "server-01"
                }
            }
        }


class SearchResponse(BaseModel):
    """
    Search results response.
    """
    hits: List[SearchHit] = Field(..., description="Search result hits")
    total: int = Field(..., description="Total number of matching documents")
    took: int = Field(..., description="Query execution time in milliseconds")
    pagination: Optional[PaginationMeta] = Field(default=None, description="Pagination metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "hits": [
                    {
                        "index": "logs-2026-02-04",
                        "id": "abc123",
                        "score": 1.0,
                        "source": {
                            "@timestamp": "2026-02-04T10:30:00Z",
                            "level": "ERROR",
                            "message": "Connection timeout",
                            "service": "api"
                        }
                    }
                ],
                "total": 1523,
                "took": 45,
                "pagination": {
                    "page": 1,
                    "size": 100,
                    "total": 1523,
                    "total_pages": 16
                }
            }
        }


class AggregationRequest(BaseModel):
    """
    Aggregation request parameters.
    """
    query: Optional[str] = Field(
        default=None,
        description="Filter query for aggregation"
    )
    indices: List[str] = Field(
        default=["logs-*"],
        description="Index patterns to aggregate"
    )
    time_range: Optional[TimeRange] = Field(
        default=None,
        description="Time range filter"
    )
    agg_type: str = Field(
        ...,
        description="Aggregation type: terms, date_histogram, stats, etc."
    )
    field: str = Field(..., description="Field to aggregate on")
    size: Optional[int] = Field(
        default=10,
        description="Number of buckets/results"
    )
    interval: Optional[str] = Field(
        default=None,
        description="Interval for date_histogram (e.g., '1h', '1d')"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "level:ERROR",
                "indices": ["logs-*"],
                "time_range": {
                    "start": "now-24h",
                    "end": "now",
                    "field": "@timestamp"
                },
                "agg_type": "terms",
                "field": "service.keyword",
                "size": 10
            }
        }


class AggregationBucket(BaseModel):
    """
    Single aggregation bucket result.
    """
    key: Any = Field(..., description="Bucket key")
    doc_count: int = Field(..., description="Number of documents in bucket")
    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional aggregation data (e.g., stats)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "key": "api-service",
                "doc_count": 523,
                "data": None
            }
        }


class AggregationResponse(BaseModel):
    """
    Aggregation results response.
    """
    buckets: List[AggregationBucket] = Field(..., description="Aggregation buckets")
    total: int = Field(..., description="Total documents matched")
    took: int = Field(..., description="Query execution time in milliseconds")

    class Config:
        json_schema_extra = {
            "example": {
                "buckets": [
                    {"key": "api-service", "doc_count": 523},
                    {"key": "web-service", "doc_count": 412},
                    {"key": "db-service", "doc_count": 301}
                ],
                "total": 1236,
                "took": 32
            }
        }
