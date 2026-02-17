"""
Unit Tests for JWT Authentication

Tests token creation, validation, user authentication,
and auth-enabled/disabled behavior.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import time
from unittest.mock import patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def auth_disabled_app():
    """Create a test app with auth disabled (default)."""
    with patch.dict("os.environ", {"AUTH_ENABLED": "false", "API_RATE_LIMIT_ENABLED": "false"}, clear=False):
        # Re-import to pick up new settings
        import importlib
        import app.config
        importlib.reload(app.config)
        import app.middleware.auth
        importlib.reload(app.middleware.auth)
        import app.routers.auth
        importlib.reload(app.routers.auth)
        import app.main
        importlib.reload(app.main)
        client = TestClient(app.main.app)
        yield client


@pytest.fixture
def auth_enabled_app():
    """Create a test app with auth enabled."""
    with patch.dict("os.environ", {
        "AUTH_ENABLED": "true",
        "AUTH_ADMIN_USERNAME": "testadmin",
        "AUTH_ADMIN_PASSWORD": "testpass123",
        "API_SECRET_KEY": "test-secret-key-for-jwt",
        "API_RATE_LIMIT_ENABLED": "false",
    }, clear=False):
        import importlib
        import app.config
        importlib.reload(app.config)
        import app.middleware.auth
        importlib.reload(app.middleware.auth)
        import app.routers.auth
        importlib.reload(app.routers.auth)
        import app.main
        importlib.reload(app.main)
        client = TestClient(app.main.app)
        yield client


# ============================================================================
# Tests: Token Operations
# ============================================================================

class TestTokenOperations:
    """Test JWT token creation and validation."""

    def test_create_access_token(self):
        """Token creation returns a non-empty string."""
        from app.middleware.auth import create_access_token
        token = create_access_token(data={"sub": "testuser", "role": "admin"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_valid_token(self):
        """Valid token can be decoded."""
        from app.middleware.auth import create_access_token, decode_token
        token = create_access_token(data={"sub": "testuser", "role": "admin"})
        payload = decode_token(token)
        assert payload["sub"] == "testuser"
        assert payload["role"] == "admin"

    def test_decode_token_has_expiry(self):
        """Token contains expiry claim."""
        from app.middleware.auth import create_access_token, decode_token
        token = create_access_token(data={"sub": "testuser"})
        payload = decode_token(token)
        assert "exp" in payload

    def test_decode_invalid_token_raises(self):
        """Invalid token raises HTTPException."""
        from fastapi import HTTPException
        from app.middleware.auth import decode_token
        with pytest.raises(HTTPException) as exc_info:
            decode_token("invalid.token.string")
        assert exc_info.value.status_code == 401

    def test_decode_token_missing_subject_raises(self):
        """Token without subject raises HTTPException."""
        from fastapi import HTTPException
        from jose import jwt
        from app.config import settings
        from app.middleware.auth import decode_token
        token = jwt.encode({"role": "admin"}, settings.secret_key, algorithm=settings.algorithm)
        with pytest.raises(HTTPException):
            decode_token(token)


# ============================================================================
# Tests: Password Operations
# ============================================================================

class TestPasswordOperations:
    """Test password hashing and verification."""

    def test_verify_correct_password(self):
        """Correct password verification succeeds."""
        from app.middleware.auth import pwd_context
        hashed = pwd_context.hash("mypassword")
        assert pwd_context.verify("mypassword", hashed)

    def test_verify_wrong_password(self):
        """Wrong password verification fails."""
        from app.middleware.auth import pwd_context
        hashed = pwd_context.hash("mypassword")
        assert not pwd_context.verify("wrongpassword", hashed)


# ============================================================================
# Tests: Authentication (Enabled Mode)
# ============================================================================

class TestAuthEnabled:
    """Test auth endpoints when AUTH_ENABLED=true."""

    def test_login_success(self, auth_enabled_app):
        """Valid credentials return a token."""
        response = auth_enabled_app.post(
            "/auth/token",
            data={"username": "testadmin", "password": "testpass123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, auth_enabled_app):
        """Wrong password returns 401."""
        response = auth_enabled_app.post(
            "/auth/token",
            data={"username": "testadmin", "password": "wrongpassword"},
        )
        assert response.status_code == 401

    def test_login_wrong_username(self, auth_enabled_app):
        """Wrong username returns 401."""
        response = auth_enabled_app.post(
            "/auth/token",
            data={"username": "nonexistent", "password": "testpass123"},
        )
        assert response.status_code == 401

    def test_get_me_with_token(self, auth_enabled_app):
        """Authenticated /auth/me returns user info."""
        # Login first
        login_response = auth_enabled_app.post(
            "/auth/token",
            data={"username": "testadmin", "password": "testpass123"},
        )
        token = login_response.json()["access_token"]

        # Get user info
        response = auth_enabled_app.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testadmin"
        assert data["role"] == "admin"

    def test_get_me_without_token(self, auth_enabled_app):
        """Unauthenticated /auth/me returns 401."""
        response = auth_enabled_app.get("/auth/me")
        assert response.status_code == 401


# ============================================================================
# Tests: Authentication (Disabled Mode)
# ============================================================================

class TestAuthDisabled:
    """Test behavior when AUTH_ENABLED=false (default)."""

    def test_login_returns_404_when_disabled(self, auth_disabled_app):
        """Login endpoint returns 404 when auth is disabled."""
        response = auth_disabled_app.post(
            "/auth/token",
            data={"username": "admin", "password": "admin"},
        )
        assert response.status_code == 404

    def test_health_accessible_without_auth(self, auth_disabled_app):
        """Health endpoints work without auth."""
        response = auth_disabled_app.get("/health/liveness")
        assert response.status_code == 200

    def test_root_accessible_without_auth(self, auth_disabled_app):
        """Root endpoint works without auth."""
        response = auth_disabled_app.get("/")
        assert response.status_code == 200


# ============================================================================
# Tests: Rate Limiting
# ============================================================================

class TestRateLimiting:
    """Test rate limiting middleware behavior."""

    def test_rate_limit_headers_present(self):
        """Response includes rate limit headers when enabled."""
        with patch.dict("os.environ", {
            "API_RATE_LIMIT_ENABLED": "true",
            "API_RATE_LIMIT_PER_MINUTE": "100",
            "AUTH_ENABLED": "false",
        }, clear=False):
            import importlib
            import app.config
            importlib.reload(app.config)
            import app.main
            importlib.reload(app.main)
            client = TestClient(app.main.app)
            response = client.get("/")
            assert "X-RateLimit-Limit" in response.headers
            assert "X-RateLimit-Remaining" in response.headers

    def test_health_exempt_from_rate_limit(self):
        """Health endpoints are exempt from rate limiting."""
        with patch.dict("os.environ", {
            "API_RATE_LIMIT_ENABLED": "true",
            "API_RATE_LIMIT_PER_MINUTE": "1",
            "AUTH_ENABLED": "false",
        }, clear=False):
            import importlib
            import app.config
            importlib.reload(app.config)
            import app.main
            importlib.reload(app.main)
            client = TestClient(app.main.app)
            # Health should always work even under rate limit
            for _ in range(5):
                response = client.get("/health/liveness")
                assert response.status_code == 200
