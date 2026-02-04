"""
API Routers

FastAPI route handlers for different API endpoints.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

from app.routers import health, search, aggregations, indices

__all__ = ["health", "search", "aggregations", "indices"]
