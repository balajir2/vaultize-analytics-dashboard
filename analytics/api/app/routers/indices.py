"""
Index Management Router

API endpoints for managing OpenSearch indices.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import logging
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from opensearchpy import exceptions as os_exceptions

from app.middleware.auth import require_admin
from app.models.common import APIResponse
from app.opensearch_client import get_opensearch

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/{index_name}/stats", response_model=APIResponse[Dict[str, Any]])
async def get_index_stats(
    index_name: str = Path(..., description="Index name or pattern")
):
    """
    Get statistics for an index or index pattern.

    Returns detailed statistics including document count, size, and shard information.

    Args:
        index_name: Index name or pattern (e.g., 'logs-2026-02-04' or 'logs-*')

    Returns:
        APIResponse[Dict]: Index statistics

    Example:
        GET /api/v1/indices/logs-2026-02-04/stats
    """
    try:
        client = get_opensearch()

        # Get index stats
        stats = client.indices.stats(index=index_name)

        # Extract useful information
        indices_stats = {}
        for idx, idx_stats in stats.get("indices", {}).items():
            indices_stats[idx] = {
                "total": {
                    "docs": {
                        "count": idx_stats["total"]["docs"]["count"],
                        "deleted": idx_stats["total"]["docs"]["deleted"]
                    },
                    "store": {
                        "size_in_bytes": idx_stats["total"]["store"]["size_in_bytes"]
                    }
                },
                "primaries": {
                    "docs": {
                        "count": idx_stats["primaries"]["docs"]["count"]
                    },
                    "store": {
                        "size_in_bytes": idx_stats["primaries"]["store"]["size_in_bytes"]
                    }
                }
            }

        return APIResponse(
            status="success",
            data=indices_stats,
            message=f"Retrieved stats for {len(indices_stats)} indices"
        )

    except os_exceptions.NotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Index not found: {index_name}"
        )
    except Exception as e:
        logger.error(f"Failed to get index stats: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get index stats due to an internal error"
        )


@router.get("/{index_name}/mappings", response_model=APIResponse[Dict[str, Any]])
async def get_index_mappings(
    index_name: str = Path(..., description="Index name or pattern")
):
    """
    Get field mappings for an index.

    Returns the field mapping schema for the specified index.

    Args:
        index_name: Index name or pattern

    Returns:
        APIResponse[Dict]: Index mappings

    Example:
        GET /api/v1/indices/logs-2026-02-04/mappings
    """
    try:
        client = get_opensearch()

        # Get mappings
        mappings = client.indices.get_mapping(index=index_name)

        return APIResponse(
            status="success",
            data=mappings,
            message=f"Retrieved mappings for {len(mappings)} indices"
        )

    except os_exceptions.NotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Index not found: {index_name}"
        )
    except Exception as e:
        logger.error(f"Failed to get index mappings: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get index mappings due to an internal error"
        )


@router.get("/{index_name}/settings", response_model=APIResponse[Dict[str, Any]])
async def get_index_settings(
    index_name: str = Path(..., description="Index name or pattern")
):
    """
    Get settings for an index.

    Returns the configuration settings for the specified index.

    Args:
        index_name: Index name or pattern

    Returns:
        APIResponse[Dict]: Index settings

    Example:
        GET /api/v1/indices/logs-2026-02-04/settings
    """
    try:
        client = get_opensearch()

        # Get settings
        settings = client.indices.get_settings(index=index_name)

        return APIResponse(
            status="success",
            data=settings,
            message=f"Retrieved settings for {len(settings)} indices"
        )

    except os_exceptions.NotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Index not found: {index_name}"
        )
    except Exception as e:
        logger.error(f"Failed to get index settings: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get index settings due to an internal error"
        )


@router.delete("/{index_name}", response_model=APIResponse[Dict[str, Any]], dependencies=[Depends(require_admin)])
async def delete_index(
    index_name: str = Path(..., description="Index name (no wildcards for safety)")
):
    """
    Delete an index.

    **WARNING**: This is a destructive operation and cannot be undone.
    Wildcards are not allowed for safety.

    Args:
        index_name: Exact index name (wildcards not permitted)

    Returns:
        APIResponse[Dict]: Deletion confirmation

    Raises:
        HTTPException: If index contains wildcards or deletion fails

    Example:
        DELETE /api/v1/indices/logs-2026-02-04
    """
    # Safety check: don't allow wildcards
    if "*" in index_name or "?" in index_name:
        raise HTTPException(
            status_code=400,
            detail="Wildcards not allowed in index deletion for safety. Specify exact index name."
        )

    try:
        client = get_opensearch()

        # Delete index
        response = client.indices.delete(index=index_name)

        logger.info(f"Deleted index: {index_name}")

        return APIResponse(
            status="success",
            data=response,
            message=f"Index '{index_name}' deleted successfully"
        )

    except os_exceptions.NotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Index not found: {index_name}"
        )
    except Exception as e:
        logger.error(f"Failed to delete index: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete index due to an internal error"
        )


@router.get("/", response_model=APIResponse[List[Dict[str, Any]]])
async def list_all_indices(
    pattern: str = Query(default="*", description="Index pattern"),
    health: str = Query(default=None, description="Filter by health: green, yellow, red")
):
    """
    List all indices with health and stats.

    Returns a comprehensive list of indices with their health status and basic stats.

    Args:
        pattern: Index pattern to match (default: all indices)
        health: Optional filter by health status

    Returns:
        APIResponse[List[Dict]]: List of indices with stats

    Example:
        GET /api/v1/indices/?pattern=logs-*&health=green
    """
    try:
        client = get_opensearch()

        # Get index information using cat API
        indices = client.cat.indices(index=pattern, format="json", v=True)

        # Filter by health if specified
        if health:
            indices = [idx for idx in indices if idx.get("health") == health]

        # Sort by index name
        indices = sorted(indices, key=lambda x: x.get("index", ""))

        return APIResponse(
            status="success",
            data=indices,
            message=f"Found {len(indices)} indices"
        )

    except Exception as e:
        logger.error(f"Failed to list indices: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to list indices due to an internal error"
        )
