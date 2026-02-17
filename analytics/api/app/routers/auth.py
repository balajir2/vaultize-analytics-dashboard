"""
Authentication Router

Provides login and user info endpoints.
Only active when AUTH_ENABLED=true.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.config import settings
from app.middleware.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
)
from app.models.user import Token, UserInfo

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate and receive a JWT access token.

    - **username**: Account username
    - **password**: Account password

    Returns a Bearer token for use in Authorization headers.
    """
    if not settings.auth_enabled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authentication is not enabled",
        )

    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )
    logger.info(f"User '{user['username']}' authenticated successfully")
    return Token(access_token=access_token)


@router.get("/me", response_model=UserInfo)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user info.

    Requires a valid Bearer token in the Authorization header.
    """
    if not settings.auth_enabled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Authentication is not enabled",
        )

    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    return UserInfo(
        username=current_user["username"],
        role=current_user["role"],
        disabled=current_user.get("disabled", False),
    )
