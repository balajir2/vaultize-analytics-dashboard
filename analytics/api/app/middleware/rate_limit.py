"""
Rate Limiting Middleware

In-memory token bucket rate limiter for the Analytics API.
Rate limiting is configurable via environment variables.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import logging
import time
from collections import defaultdict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config import settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Per-IP rate limiting using a sliding window counter.

    Limits are configured via:
    - API_RATE_LIMIT_ENABLED: Enable/disable rate limiting
    - API_RATE_LIMIT_PER_MINUTE: Maximum requests per minute per IP

    Limitations:
    - **Single-instance only**: The in-memory counter is not shared across
      workers or replicas. Each uvicorn worker maintains its own counter,
      so the effective limit is multiplied by the number of workers.
    - **No proxy-aware IP extraction**: Uses ``request.client.host``
      directly. Behind a reverse proxy (nginx, Traefik), this returns the
      proxy IP unless the proxy sets ``X-Forwarded-For``. For correct
      per-client limiting behind a proxy, configure the ASGI server to
      trust proxy headers or add a ``ProxyHeadersMiddleware``.
    - **Upgrade path**: For multi-replica deployments, replace this
      middleware with a Redis-backed limiter (e.g., ``slowapi`` with
      Redis storage) to share counters across instances.
    """

    def __init__(self, app, requests_per_minute: int = 1000):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60
        # {ip: [(timestamp, ...),]}
        self._requests: dict = defaultdict(list)

    async def dispatch(self, request: Request, call_next) -> Response:
        if not settings.rate_limit_enabled:
            return await call_next(request)

        # Skip rate limiting for health and metrics endpoints
        if request.url.path.startswith("/health") or request.url.path == "/metrics":
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old entries and count recent requests
        self._requests[client_ip] = [
            t for t in self._requests[client_ip] if t > window_start
        ]

        if len(self._requests[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "status": "error",
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": f"Rate limit exceeded. Max {self.requests_per_minute} requests per minute.",
                    },
                },
                headers={"Retry-After": "60"},
            )

        self._requests[client_ip].append(now)

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            self.requests_per_minute - len(self._requests[client_ip])
        )
        return response
