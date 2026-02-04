"""
Search Router

API endpoints for log search and query operations.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import logging
import math
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from opensearchpy import OpenSearch, exceptions as os_exceptions

from app.config import settings
from app.models.common import APIResponse, PaginationMeta
from app.models.search import SearchRequest, SearchResponse, SearchHit
from app.opensearch_client import get_opensearch

logger = logging.getLogger(__name__)

router = APIRouter()


def build_query(search_req: SearchRequest) -> Dict[str, Any]:
    """
    Build OpenSearch query from search request.

    Args:
        search_req: Search request parameters

    Returns:
        dict: OpenSearch query DSL
    """
    query_body = {"query": {"bool": {"must": [], "filter": []}}}

    # Add query string if provided
    if search_req.query:
        query_body["query"]["bool"]["must"].append({
            "query_string": {
                "query": search_req.query,
                "default_operator": "AND"
            }
        })
    else:
        # Match all if no query provided
        query_body["query"]["bool"]["must"].append({"match_all": {}})

    # Add time range filter if provided
    if search_req.time_range:
        time_filter = {"range": {}}
        time_filter["range"][search_req.time_range.field] = {}

        if search_req.time_range.start:
            time_filter["range"][search_req.time_range.field]["gte"] = search_req.time_range.start
        if search_req.time_range.end:
            time_filter["range"][search_req.time_range.field]["lte"] = search_req.time_range.end

        query_body["query"]["bool"]["filter"].append(time_filter)

    # Add sort
    if search_req.sort:
        query_body["sort"] = search_req.sort

    # Add field filtering if specified
    if search_req.fields:
        query_body["_source"] = search_req.fields

    # Add pagination
    query_body["from"] = search_req.from_
    query_body["size"] = search_req.size

    return query_body


@router.post("/search", response_model=APIResponse[SearchResponse])
async def search_logs(search_req: SearchRequest):
    """
    Search logs using Lucene query syntax.

    Execute a search query across specified indices using Lucene query syntax.
    Supports time range filtering, field selection, sorting, and pagination.

    Args:
        search_req: Search request parameters

    Returns:
        APIResponse[SearchResponse]: Search results with pagination

    Raises:
        HTTPException: If search fails (400/500)

    Example:
        ```json
        {
            "query": "level:ERROR AND service:api",
            "indices": ["logs-2026-02-*"],
            "time_range": {
                "start": "now-1h",
                "end": "now"
            },
            "size": 100,
            "from": 0
        }
        ```
    """
    try:
        client = get_opensearch()
        query_body = build_query(search_req)

        logger.info(f"Executing search on indices: {search_req.indices}")
        logger.debug(f"Query: {query_body}")

        # Execute search
        response = client.search(
            index=",".join(search_req.indices),
            body=query_body
        )

        # Parse response
        hits = []
        for hit in response["hits"]["hits"]:
            hits.append(SearchHit(
                index=hit["_index"],
                id=hit["_id"],
                score=hit.get("_score"),
                source=hit["_source"]
            ))

        total = response["hits"]["total"]["value"]
        took = response["took"]

        # Calculate pagination
        total_pages = math.ceil(total / search_req.size)
        current_page = (search_req.from_ // search_req.size) + 1

        pagination = PaginationMeta(
            page=current_page,
            size=search_req.size,
            total=total,
            total_pages=total_pages
        )

        search_response = SearchResponse(
            hits=hits,
            total=total,
            took=took,
            pagination=pagination
        )

        return APIResponse(
            status="success",
            data=search_response,
            message=f"Found {total} results in {took}ms"
        )

    except os_exceptions.RequestError as e:
        logger.error(f"Invalid search query: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid query: {str(e)}"
        )
    except os_exceptions.NotFoundError as e:
        logger.error(f"Index not found: {e}")
        raise HTTPException(
            status_code=404,
            detail=f"Index not found: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/search/simple", response_model=APIResponse[SearchResponse])
async def simple_search(
    q: str = Query(..., description="Search query string"),
    indices: str = Query(default="logs-*", description="Comma-separated index patterns"),
    size: int = Query(default=100, ge=1, le=10000, description="Number of results"),
    from_: int = Query(default=0, ge=0, alias="from", description="Offset for pagination")
):
    """
    Simple GET-based search endpoint.

    Simplified search endpoint using query parameters instead of request body.
    Useful for quick searches and testing.

    Args:
        q: Lucene query string
        indices: Comma-separated index patterns
        size: Number of results to return
        from_: Offset for pagination

    Returns:
        APIResponse[SearchResponse]: Search results

    Example:
        GET /api/v1/search/simple?q=level:ERROR&indices=logs-*&size=50
    """
    # Convert to SearchRequest
    search_req = SearchRequest(
        query=q,
        indices=indices.split(","),
        size=size,
        from_=from_
    )

    # Use the main search function
    return await search_logs(search_req)


@router.get("/indices", response_model=APIResponse[List[str]])
async def list_indices(
    pattern: str = Query(default="logs-*", description="Index pattern to match")
):
    """
    List available indices matching a pattern.

    Returns a list of index names that match the specified pattern.

    Args:
        pattern: Index pattern (supports wildcards)

    Returns:
        APIResponse[List[str]]: List of matching index names

    Example:
        GET /api/v1/indices?pattern=logs-2026-02-*
    """
    try:
        client = get_opensearch()

        # Get indices matching pattern
        indices = client.indices.get(index=pattern)

        # Return sorted list of index names
        index_names = sorted(indices.keys())

        return APIResponse(
            status="success",
            data=index_names,
            message=f"Found {len(index_names)} indices"
        )

    except os_exceptions.NotFoundError:
        # No indices found matching pattern
        return APIResponse(
            status="success",
            data=[],
            message=f"No indices found matching pattern: {pattern}"
        )
    except Exception as e:
        logger.error(f"Failed to list indices: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list indices: {str(e)}"
        )
