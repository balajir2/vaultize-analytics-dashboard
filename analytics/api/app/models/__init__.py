"""
Pydantic Models

Data validation models for API requests and responses.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

from app.models.common import (
    APIResponse,
    ErrorResponse,
    PaginationParams,
    PaginationMeta
)
from app.models.health import HealthResponse, OpenSearchHealthResponse
from app.models.search import (
    SearchRequest,
    SearchResponse,
    SearchHit,
    AggregationRequest,
    AggregationResponse
)

__all__ = [
    "APIResponse",
    "ErrorResponse",
    "PaginationParams",
    "PaginationMeta",
    "HealthResponse",
    "OpenSearchHealthResponse",
    "SearchRequest",
    "SearchResponse",
    "SearchHit",
    "AggregationRequest",
    "AggregationResponse",
]
