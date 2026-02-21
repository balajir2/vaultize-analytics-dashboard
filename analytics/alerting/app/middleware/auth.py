"""
API Key Authentication Middleware for Alerting Service

Provides Bearer token authentication for the Alerting Service management API.
Authentication is opt-in via AUTH_ENABLED=true environment variable.
Uses the same JWT tokens as the Analytics API.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import logging
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import settings

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Optional[dict]:
    """
    Validate a Bearer token for alerting service access.

    When AUTH_ENABLED=false (default), returns None (all access allowed).
    When AUTH_ENABLED=true, requires a valid JWT Bearer token.
    """
    if not settings.auth_enabled:
        return None

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"username": username, "role": payload.get("role", "viewer")}
    except JWTError as e:
        logger.warning("JWT validation failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_admin(
    user: Optional[dict] = Depends(get_current_user),
) -> Optional[dict]:
    """
    FastAPI dependency that requires admin role.

    When AUTH_ENABLED=false, returns None (all access allowed).
    """
    if not settings.auth_enabled:
        return None

    if user is None or user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return user
