"""
JWT Authentication Middleware

Provides Bearer token authentication for the Analytics API.
Authentication is opt-in via AUTH_ENABLED=true environment variable.
When disabled (default), all routes are accessible without tokens.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer token scheme (auto_error=False so we can handle missing tokens ourselves)
bearer_scheme = HTTPBearer(auto_error=False)


# ============================================================================
# User Database (in-memory for v1, backed by config)
# ============================================================================

def get_users_db() -> dict:
    """
    Return the user database.

    For v1, users are defined via environment variables.
    In production, this would be backed by OpenSearch or an external IdP.
    """
    return {
        settings.auth_admin_username: {
            "username": settings.auth_admin_username,
            "hashed_password": pwd_context.hash(settings.auth_admin_password),
            "role": "admin",
            "disabled": False,
        }
    }


# ============================================================================
# Token Operations
# ============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate a user by username and password."""
    users_db = get_users_db()
    user = users_db.get(username)
    if not user:
        return None
    # For config-defined users, hash and verify each time
    if not pwd_context.verify(password, user["hashed_password"]):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Claims to encode in the token
        expires_delta: Optional custom expiry duration

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded token claims

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ============================================================================
# FastAPI Dependencies
# ============================================================================

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Optional[dict]:
    """
    FastAPI dependency that extracts and validates the current user.

    When AUTH_ENABLED=false (default), returns None (all access allowed).
    When AUTH_ENABLED=true, requires a valid Bearer token.
    """
    if not settings.auth_enabled:
        return None  # Auth disabled, all access allowed

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(credentials.credentials)
    username = payload.get("sub")
    users_db = get_users_db()
    user = users_db.get(username)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.get("disabled"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )

    return user


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
