"""
Analytics API - Main Application

FastAPI application entry point for the Vaultize Analytics Platform.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import logging
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.opensearch_client import OpenSearchClient
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import RateLimitMiddleware
from app.routers import health, search, aggregations, indices, auth

# ============================================================================
# Logging Configuration
# ============================================================================

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Lifespan Events
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.

    Handles startup and shutdown tasks.
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")

    # Initialize OpenSearch client
    try:
        client = OpenSearchClient.get_client()
        health = client.cluster.health()
        logger.info(f"OpenSearch cluster status: {health['status']}")
    except Exception as e:
        logger.error(f"Failed to connect to OpenSearch: {e}")
        # Don't fail startup - let health endpoint report the issue

    yield

    # Shutdown
    logger.info("Shutting down Analytics API")
    OpenSearchClient.close()


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title=settings.app_name,
    description="RESTful API for the Vaultize Analytics Platform",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ============================================================================
# Middleware
# ============================================================================

# CORS Middleware
# In production/staging, restrict CORS to configured origins only.
# In development, allow all origins for convenience.
if settings.environment in ("production", "staging") and settings.cors_origins != "*":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept", "X-Request-ID"],
    )
else:
    if settings.cors_origins == "*":
        logger.warning(
            "CORS configured with allow_origins=['*'] and allow_credentials=True. "
            "Browsers will block credentialed cross-origin requests with wildcard origins. "
            "Set API_CORS_ORIGINS to specific origins before enabling auth."
        )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Rate Limiting Middleware
if settings.rate_limit_enabled:
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=settings.rate_limit_per_minute,
    )

# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled exceptions.

    Args:
        request: The request that caused the exception
        exc: The exception that was raised

    Returns:
        JSONResponse: Error response
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred",
                "details": str(exc) if settings.debug else None
            }
        }
    )


# ============================================================================
# Routers
# ============================================================================

# Include routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(search.router, prefix=settings.api_root_path, tags=["Search"], dependencies=[Depends(get_current_user)])
app.include_router(aggregations.router, prefix=settings.api_root_path, tags=["Aggregations"], dependencies=[Depends(get_current_user)])
app.include_router(indices.router, prefix=f"{settings.api_root_path}/indices", tags=["Index Management"], dependencies=[Depends(get_current_user)])

# ============================================================================
# Prometheus Metrics
# ============================================================================

from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app, include_in_schema=False)

# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/")
async def root():
    """
    Root endpoint - API information.

    Returns:
        dict: API metadata
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs",
        "health": "/health",
        "api_root": settings.api_root_path
    }


# ============================================================================
# Entry Point (for direct execution)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower()
    )
