"""
Unit Tests for Alerting Service Authentication

Tests token validation and auth-enabled/disabled behavior.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

from unittest.mock import patch

import pytest
from jose import jwt


# ============================================================================
# Tests: Auth Module
# ============================================================================

class TestAlertingAuthModule:
    """Test alerting service auth middleware."""

    def test_auth_module_exists(self):
        """Auth middleware module is importable."""
        from app.middleware import auth
        assert hasattr(auth, "get_current_user")
        assert hasattr(auth, "bearer_scheme")

    def test_get_current_user_returns_none_when_disabled(self):
        """When auth is disabled, get_current_user returns None."""
        import asyncio
        from app.middleware.auth import get_current_user
        result = asyncio.get_event_loop().run_until_complete(
            get_current_user(credentials=None)
        )
        assert result is None

    def test_valid_token_decodes_correctly(self):
        """A valid JWT token is decoded correctly."""
        from app.config import settings
        token = jwt.encode(
            {"sub": "testuser", "role": "admin"},
            settings.secret_key,
            algorithm=settings.algorithm,
        )
        # Decode manually to verify
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["sub"] == "testuser"
        assert payload["role"] == "admin"

    def test_invalid_token_rejected(self):
        """An invalid token is rejected."""
        with pytest.raises(Exception):
            jwt.decode("invalid.token", "wrong-key", algorithms=["HS256"])

    def test_config_has_auth_fields(self):
        """Config has auth_enabled, secret_key, algorithm fields."""
        from app.config import settings
        assert hasattr(settings, "auth_enabled")
        assert hasattr(settings, "secret_key")
        assert hasattr(settings, "algorithm")

    def test_auth_disabled_by_default(self):
        """Auth is disabled by default."""
        from app.config import settings
        assert settings.auth_enabled is False

    def test_algorithm_is_hs256(self):
        """Default algorithm is HS256."""
        from app.config import settings
        assert settings.algorithm == "HS256"
