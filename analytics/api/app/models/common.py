"""
Common Pydantic Models

Shared models used across multiple endpoints.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

from typing import Any, Optional, Generic, TypeVar
from pydantic import BaseModel, Field

# Generic type for data in APIResponse
T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    """
    Standard API response wrapper.

    Provides consistent response format across all endpoints.
    """
    status: str = Field(default="success", description="Response status: success or error")
    data: Optional[T] = Field(default=None, description="Response data")
    message: Optional[str] = Field(default=None, description="Optional message")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "data": {"key": "value"},
                "message": "Operation completed successfully"
            }
        }


class ErrorResponse(BaseModel):
    """
    Standard error response format.

    Used when an operation fails.
    """
    status: str = Field(default="error", description="Always 'error' for error responses")
    error: dict = Field(..., description="Error details")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "error": {
                    "code": "RESOURCE_NOT_FOUND",
                    "message": "The requested resource was not found",
                    "details": None
                }
            }
        }


class PaginationParams(BaseModel):
    """
    Query parameters for paginated endpoints.
    """
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    size: int = Field(default=100, ge=1, le=10000, description="Items per page")

    @property
    def offset(self) -> int:
        """Calculate offset from page and size."""
        return (self.page - 1) * self.size

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "size": 100
            }
        }


class PaginationMeta(BaseModel):
    """
    Pagination metadata included in paginated responses.
    """
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Items per page")
    total: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "size": 100,
                "total": 1523,
                "total_pages": 16
            }
        }


class TimeRange(BaseModel):
    """
    Time range filter for queries.
    """
    start: Optional[str] = Field(default=None, description="Start time (ISO 8601 or relative like 'now-1h')")
    end: Optional[str] = Field(default=None, description="End time (ISO 8601 or relative like 'now')")
    field: str = Field(default="@timestamp", description="Time field to filter on")

    class Config:
        json_schema_extra = {
            "example": {
                "start": "now-1h",
                "end": "now",
                "field": "@timestamp"
            }
        }
