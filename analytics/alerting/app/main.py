"""
Alerting Service - Main Application

Entry point: runs the alert scheduler and management API.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.config import settings
from app.opensearch_client import OpenSearchClient
from app.notifiers.webhook import WebhookNotifier
from app.routers import health, alerts
from app.services.condition_evaluator import ConditionEvaluator
from app.services.query_executor import QueryExecutor
from app.services.rule_loader import RuleLoader
from app.services.scheduler import AlertScheduler
from app.services.state_manager import StateManager
from app.storage.opensearch_storage import AlertHistoryStorage

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    # Initialize OpenSearch client
    try:
        client = OpenSearchClient.get_client()
    except Exception as e:
        logger.error(f"Failed to connect to OpenSearch: {e}")
        yield
        return

    # Build service graph
    rule_loader = RuleLoader(settings.alert_rules_dir)
    query_executor = QueryExecutor(client)
    condition_evaluator = ConditionEvaluator()
    state_manager = StateManager(client, settings.alert_state_index)
    notifier = WebhookNotifier(
        timeout=settings.webhook_timeout, retries=settings.webhook_retries
    )
    history_storage = AlertHistoryStorage(client, settings.alert_history_index)

    # Initialize storage
    state_manager.initialize()
    history_storage.initialize()

    # Create and start scheduler
    scheduler = AlertScheduler(
        rule_loader=rule_loader,
        query_executor=query_executor,
        condition_evaluator=condition_evaluator,
        state_manager=state_manager,
        notifier=notifier,
        history_storage=history_storage,
    )
    scheduler.start()

    # Store scheduler in app state for routers to access
    app.state.scheduler = scheduler

    yield

    # Shutdown
    scheduler.stop()
    OpenSearchClient.close()
    logger.info("Alerting service stopped")


app = FastAPI(
    title=settings.app_name,
    description="Threshold-based alerting service for the Vaultize Analytics Platform",
    version=settings.app_version,
    lifespan=lifespan,
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "Internal server error"},
    )


app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower(),
    )
