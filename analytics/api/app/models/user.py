"""
User and Token Models

Pydantic models for authentication request/response schemas.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

from typing import Optional

from pydantic import BaseModel, Field


class Token(BaseModel):
    """OAuth2 token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenData(BaseModel):
    """Decoded token data."""
    username: Optional[str] = None
    role: Optional[str] = None


class UserInfo(BaseModel):
    """User information response."""
    username: str = Field(..., description="Username")
    role: str = Field(..., description="User role (admin, viewer, api_client)")
    disabled: bool = Field(default=False, description="Whether the account is disabled")
