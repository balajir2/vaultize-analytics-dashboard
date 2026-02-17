"""
Health Check Router

Health, liveness, and readiness endpoints for the alerting service.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import logging
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.opensearch_client import get_opensearch

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def health_check(request: Request):
    """Overall health including OpenSearch and scheduler status."""
    scheduler = request.app.state.scheduler if hasattr(request.app.state, "scheduler") else None

    os_status = None
    try:
        client = get_opensearch()
        health = client.cluster.health()
        os_status = {"status": health["status"], "nodes": health["number_of_nodes"]}
    except Exception as e:
        logger.warning(f"OpenSearch health check failed: {e}")

    scheduler_running = scheduler.is_running if scheduler else False
    rules_loaded = 0
    if scheduler:
        rules_loaded = len(scheduler.rule_loader.rules)

    status = "healthy" if os_status and scheduler_running else "degraded"

    return {
        "status": status,
        "version": settings.app_version,
        "environment": settings.environment,
        "opensearch": os_status,
        "scheduler": "running" if scheduler_running else "stopped",
        "rules_loaded": rules_loaded,
    }


@router.get("/liveness")
async def liveness():
    """Liveness probe - always returns alive."""
    return {"status": "alive"}


@router.get("/readiness")
async def readiness(request: Request):
    """Readiness probe - checks OpenSearch and scheduler."""
    scheduler = request.app.state.scheduler if hasattr(request.app.state, "scheduler") else None

    try:
        client = get_opensearch()
        client.cluster.health()
    except Exception:
        return JSONResponse(status_code=503, content={"status": "not_ready", "reason": "OpenSearch unavailable"})

    if not (scheduler and scheduler.is_running):
        return JSONResponse(status_code=503, content={"status": "not_ready", "reason": "Scheduler not running"})

    return {"status": "ready"}
