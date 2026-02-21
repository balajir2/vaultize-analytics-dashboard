"""
Regression Test RT-028: No JWT Error Leakage

Validates that JWT decode errors return a generic message
("Invalid authentication token") instead of leaking internal
validation details via f"Invalid token: {e}".

Date: 2026-02-22
Severity: Medium
Category: Security - Information Disclosure
Authors: Balaji Rajan and Claude (Anthropic)
"""

from pathlib import Path

import pytest

# ============================================================================
# Constants
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
API_AUTH = PROJECT_ROOT / "analytics" / "api" / "app" / "middleware" / "auth.py"
ALERTING_AUTH = PROJECT_ROOT / "analytics" / "alerting" / "app" / "middleware" / "auth.py"


# ============================================================================
# Tests: API Auth Middleware
# ============================================================================

class TestApiJwtErrorLeakage:
    """Validate API auth does not leak JWT error details."""

    def test_regression_028_01_api_no_fstring_token_error(self):
        """RT-028-01: API auth must NOT use f-string with exception in token error."""
        source = API_AUTH.read_text(encoding="utf-8")
        assert 'f"Invalid token: {e}"' not in source, \
            "API auth must not leak JWT error details via f-string interpolation"

    def test_regression_028_02_api_generic_token_message(self):
        """RT-028-02: API auth must use generic 'Invalid authentication token' message."""
        source = API_AUTH.read_text(encoding="utf-8")
        assert "Invalid authentication token" in source, \
            "API auth must return generic 'Invalid authentication token' message"

    def test_regression_028_03_api_logs_jwt_error(self):
        """RT-028-03: API auth must log JWT error details for debugging."""
        source = API_AUTH.read_text(encoding="utf-8")
        assert "JWT validation failed" in source, \
            "API auth must log JWT validation errors for debugging"


# ============================================================================
# Tests: Alerting Auth Middleware
# ============================================================================

class TestAlertingJwtErrorLeakage:
    """Validate alerting auth does not leak JWT error details."""

    def test_regression_028_04_alerting_no_fstring_token_error(self):
        """RT-028-04: Alerting auth must NOT use f-string with exception in token error."""
        source = ALERTING_AUTH.read_text(encoding="utf-8")
        assert 'f"Invalid token: {e}"' not in source, \
            "Alerting auth must not leak JWT error details via f-string interpolation"

    def test_regression_028_05_alerting_generic_token_message(self):
        """RT-028-05: Alerting auth must use generic 'Invalid authentication token' message."""
        source = ALERTING_AUTH.read_text(encoding="utf-8")
        assert "Invalid authentication token" in source, \
            "Alerting auth must return generic 'Invalid authentication token' message"

    def test_regression_028_06_alerting_logs_jwt_error(self):
        """RT-028-06: Alerting auth must log JWT error details for debugging."""
        source = ALERTING_AUTH.read_text(encoding="utf-8")
        assert "JWT validation failed" in source, \
            "Alerting auth must log JWT validation errors for debugging"
