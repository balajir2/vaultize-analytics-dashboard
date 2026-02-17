"""
Regression Test RT-015: JWT Authentication Configuration Validation

Validates that authentication middleware, models, and configuration
are properly implemented in both the Analytics API and Alerting Service.

Severity: Critical
Category: Security - Authentication
Authors: Balaji Rajan and Claude (Anthropic)
"""

import ast
from pathlib import Path

import pytest

# ============================================================================
# Constants
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
API_APP_DIR = PROJECT_ROOT / "analytics" / "api" / "app"
ALERTING_APP_DIR = PROJECT_ROOT / "analytics" / "alerting" / "app"
API_REQUIREMENTS = PROJECT_ROOT / "analytics" / "api" / "requirements.txt"


# ============================================================================
# Tests: Auth Module Existence
# ============================================================================

class TestAuthModuleExists:
    """Validate auth middleware modules exist."""

    def test_api_middleware_init(self):
        """RT-015-01: API middleware __init__.py must exist."""
        assert (API_APP_DIR / "middleware" / "__init__.py").exists()

    def test_api_auth_module(self):
        """RT-015-02: API auth.py middleware must exist."""
        assert (API_APP_DIR / "middleware" / "auth.py").exists()

    def test_api_rate_limit_module(self):
        """RT-015-03: API rate_limit.py middleware must exist."""
        assert (API_APP_DIR / "middleware" / "rate_limit.py").exists()

    def test_api_user_model(self):
        """RT-015-04: API user.py model must exist."""
        assert (API_APP_DIR / "models" / "user.py").exists()

    def test_api_auth_router(self):
        """RT-015-05: API auth.py router must exist."""
        assert (API_APP_DIR / "routers" / "auth.py").exists()

    def test_alerting_middleware_init(self):
        """RT-015-06: Alerting middleware __init__.py must exist."""
        assert (ALERTING_APP_DIR / "middleware" / "__init__.py").exists()

    def test_alerting_auth_module(self):
        """RT-015-07: Alerting auth.py middleware must exist."""
        assert (ALERTING_APP_DIR / "middleware" / "auth.py").exists()


# ============================================================================
# Tests: Auth Dependencies
# ============================================================================

class TestAuthDependencies:
    """Validate required libraries are in requirements.txt."""

    def test_jose_in_requirements(self):
        """RT-015-08: python-jose must be in API requirements."""
        content = API_REQUIREMENTS.read_text(encoding="utf-8")
        assert "python-jose" in content, "python-jose (JWT) not in requirements.txt"

    def test_passlib_in_requirements(self):
        """RT-015-09: passlib must be in API requirements."""
        content = API_REQUIREMENTS.read_text(encoding="utf-8")
        assert "passlib" in content, "passlib (password hashing) not in requirements.txt"

    def test_python_multipart_in_requirements(self):
        """RT-015-10: python-multipart must be in API requirements."""
        content = API_REQUIREMENTS.read_text(encoding="utf-8")
        assert "python-multipart" in content, "python-multipart (OAuth2 forms) not in requirements.txt"


# ============================================================================
# Tests: Auth Configuration
# ============================================================================

class TestAuthConfiguration:
    """Validate auth config fields exist in Settings classes."""

    def test_api_config_has_auth_enabled(self):
        """RT-015-11: API config must have auth_enabled field."""
        content = (API_APP_DIR / "config.py").read_text(encoding="utf-8")
        assert "auth_enabled" in content, "API config missing auth_enabled field"

    def test_api_config_has_auth_username(self):
        """RT-015-12: API config must have auth_admin_username field."""
        content = (API_APP_DIR / "config.py").read_text(encoding="utf-8")
        assert "auth_admin_username" in content, "API config missing auth_admin_username"

    def test_api_config_has_auth_password(self):
        """RT-015-13: API config must have auth_admin_password field."""
        content = (API_APP_DIR / "config.py").read_text(encoding="utf-8")
        assert "auth_admin_password" in content, "API config missing auth_admin_password"

    def test_alerting_config_has_auth_enabled(self):
        """RT-015-14: Alerting config must have auth_enabled field."""
        content = (ALERTING_APP_DIR / "config.py").read_text(encoding="utf-8")
        assert "auth_enabled" in content, "Alerting config missing auth_enabled field"

    def test_alerting_config_has_secret_key(self):
        """RT-015-15: Alerting config must have secret_key field."""
        content = (ALERTING_APP_DIR / "config.py").read_text(encoding="utf-8")
        assert "secret_key" in content, "Alerting config missing secret_key"

    def test_auth_disabled_by_default(self):
        """RT-015-16: Auth must default to disabled (False)."""
        content = (API_APP_DIR / "config.py").read_text(encoding="utf-8")
        assert "default=False" in content.split("auth_enabled")[1].split("\n")[0], \
            "auth_enabled must default to False"


# ============================================================================
# Tests: Main.py Integration
# ============================================================================

class TestMainIntegration:
    """Validate auth is registered in main.py."""

    def test_api_main_imports_auth_router(self):
        """RT-015-17: API main.py must import auth router."""
        content = (API_APP_DIR / "main.py").read_text(encoding="utf-8")
        assert "auth" in content, "API main.py must import auth router"

    def test_api_main_includes_auth_router(self):
        """RT-015-18: API main.py must include auth router."""
        content = (API_APP_DIR / "main.py").read_text(encoding="utf-8")
        assert 'prefix="/auth"' in content, "API main.py must include auth router with /auth prefix"

    def test_api_main_imports_rate_limit(self):
        """RT-015-19: API main.py must import rate limit middleware."""
        content = (API_APP_DIR / "main.py").read_text(encoding="utf-8")
        assert "RateLimitMiddleware" in content, "API main.py must import RateLimitMiddleware"

    def test_api_main_adds_rate_limit_middleware(self):
        """RT-015-20: API main.py must add rate limit middleware."""
        content = (API_APP_DIR / "main.py").read_text(encoding="utf-8")
        assert "rate_limit_enabled" in content, "API main.py must conditionally add rate limiting"


# ============================================================================
# Tests: Auth Module Content
# ============================================================================

class TestAuthModuleContent:
    """Validate auth modules have required functions."""

    def test_api_auth_has_create_token(self):
        """RT-015-21: API auth must have create_access_token function."""
        content = (API_APP_DIR / "middleware" / "auth.py").read_text(encoding="utf-8")
        assert "def create_access_token" in content

    def test_api_auth_has_decode_token(self):
        """RT-015-22: API auth must have decode_token function."""
        content = (API_APP_DIR / "middleware" / "auth.py").read_text(encoding="utf-8")
        assert "def decode_token" in content

    def test_api_auth_has_get_current_user(self):
        """RT-015-23: API auth must have get_current_user dependency."""
        content = (API_APP_DIR / "middleware" / "auth.py").read_text(encoding="utf-8")
        assert "async def get_current_user" in content

    def test_api_auth_has_authenticate_user(self):
        """RT-015-24: API auth must have authenticate_user function."""
        content = (API_APP_DIR / "middleware" / "auth.py").read_text(encoding="utf-8")
        assert "def authenticate_user" in content

    def test_alerting_auth_has_get_current_user(self):
        """RT-015-25: Alerting auth must have get_current_user dependency."""
        content = (ALERTING_APP_DIR / "middleware" / "auth.py").read_text(encoding="utf-8")
        assert "async def get_current_user" in content
