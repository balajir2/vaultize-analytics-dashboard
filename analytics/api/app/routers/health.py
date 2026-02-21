"""
Health Check Router

API endpoints for health checks and readiness probes.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from opensearchpy import OpenSearch, exceptions as os_exceptions

from app.config import settings
from app.models.common import APIResponse
from app.models.health import HealthResponse, OpenSearchHealthResponse
from app.opensearch_client import get_opensearch

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Overall API health check.

    Returns health status of the API and connected services.

    Returns:
        HealthResponse: API and service health information
    """
    try:
        # Get OpenSearch health
        client = get_opensearch()
        os_health = client.cluster.health()

        opensearch_health = OpenSearchHealthResponse(
            cluster_name=os_health.get("cluster_name", "unknown"),
            status=os_health.get("status", "unknown"),
            timed_out=os_health.get("timed_out", False),
            number_of_nodes=os_health.get("number_of_nodes", 0),
            number_of_data_nodes=os_health.get("number_of_data_nodes", 0),
            active_primary_shards=os_health.get("active_primary_shards", 0),
            active_shards=os_health.get("active_shards", 0),
            relocating_shards=os_health.get("relocating_shards", 0),
            initializing_shards=os_health.get("initializing_shards", 0),
            unassigned_shards=os_health.get("unassigned_shards", 0)
        )

        # Determine overall health status
        status = "healthy"
        if os_health.get("status") == "red":
            status = "degraded"
        elif os_health.get("status") == "yellow":
            status = "partially_healthy"

        return HealthResponse(
            status=status,
            version=settings.app_version,
            environment=settings.environment,
            opensearch=opensearch_health
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        # Return degraded status but don't raise HTTP error
        # (API itself is up, but OpenSearch is unreachable)
        return HealthResponse(
            status="degraded",
            version=settings.app_version,
            environment=settings.environment,
            opensearch=None
        )


@router.get("/readiness")
async def readiness_check():
    """
    Kubernetes readiness probe.

    Checks if the API is ready to accept traffic.

    Returns:
        dict: Readiness status

    Raises:
        HTTPException: If service is not ready (503)
    """
    try:
        client = get_opensearch()
        health = client.cluster.health()

        # Service is ready if OpenSearch is reachable (even if yellow)
        if health.get("status") in ["green", "yellow"]:
            return {"status": "ready"}
        else:
            return JSONResponse(
                status_code=503,
                content={"status": "not_ready", "reason": "OpenSearch cluster is red"}
            )

    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "reason": "OpenSearch is unreachable"}
        )


@router.get("/liveness")
async def liveness_check():
    """
    Kubernetes liveness probe.

    Checks if the API process is alive and responsive.

    Returns:
        dict: Liveness status
    """
    # Simple liveness check - if we can respond, we're alive
    return {"status": "alive"}


@router.get("/cluster", response_model=APIResponse[Dict[str, Any]])
async def cluster_health():
    """
    Detailed OpenSearch cluster health (wrapped in standard API response).

    Returns detailed information about the OpenSearch cluster in the
    standard APIResponse format.

    Returns:
        APIResponse[Dict]: Cluster health details

    Raises:
        HTTPException: If unable to connect to OpenSearch (503)
    """
    try:
        client = get_opensearch()
        health = client.cluster.health()

        return APIResponse(
            status="success",
            data=health,
            message=f"Cluster status: {health.get('status', 'unknown')}"
        )

    except (os_exceptions.ConnectionError, Exception) as e:
        logger.error(f"Failed to get cluster health: {e}")
        raise HTTPException(
            status_code=503,
            detail="Unable to connect to OpenSearch"
        )


@router.get("/opensearch")
async def opensearch_health():
    """
    Detailed OpenSearch cluster health.

    Returns detailed information about the OpenSearch cluster.

    Returns:
        OpenSearchHealthResponse: Cluster health details

    Raises:
        HTTPException: If unable to connect to OpenSearch (503)
    """
    try:
        client = get_opensearch()
        health = client.cluster.health()

        return OpenSearchHealthResponse(
            cluster_name=health.get("cluster_name", "unknown"),
            status=health.get("status", "unknown"),
            timed_out=health.get("timed_out", False),
            number_of_nodes=health.get("number_of_nodes", 0),
            number_of_data_nodes=health.get("number_of_data_nodes", 0),
            active_primary_shards=health.get("active_primary_shards", 0),
            active_shards=health.get("active_shards", 0),
            relocating_shards=health.get("relocating_shards", 0),
            initializing_shards=health.get("initializing_shards", 0),
            unassigned_shards=health.get("unassigned_shards", 0)
        )

    except Exception as e:
        logger.error(f"Failed to get OpenSearch health: {e}")
        raise HTTPException(
            status_code=503,
            detail="Unable to connect to OpenSearch"
        )
