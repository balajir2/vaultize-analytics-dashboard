"""
Regression Test RT-027: Auth Required in Production/Staging

Validates that both the Analytics API and Alerting Service config.py
files enforce AUTH_ENABLED=true in production and staging environments.
A misconfigured deploy must not pass startup validation with auth disabled.

Date: 2026-02-22
Severity: High
Category: Security - Authentication
Authors: Balaji Rajan and Claude (Anthropic)
"""

from pathlib import Path

import pytest

# ============================================================================
# Constants
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
API_CONFIG = PROJECT_ROOT / "analytics" / "api" / "app" / "config.py"
ALERTING_CONFIG = PROJECT_ROOT / "analytics" / "alerting" / "app" / "config.py"


# ============================================================================
# Tests: API Config
# ============================================================================

class TestApiAuthEnforcement:
    """Validate API config enforces auth in production/staging."""

    def test_regression_027_01_api_checks_auth_disabled(self):
        """RT-027-01: API config must check if auth is disabled in production."""
        source = API_CONFIG.read_text(encoding="utf-8")
        assert "not settings.auth_enabled" in source, \
            "API config must check for auth disabled in production/staging"

    def test_regression_027_02_api_auth_error_message(self):
        """RT-027-02: API config must have auth enforcement error message."""
        source = API_CONFIG.read_text(encoding="utf-8")
        assert "AUTH_ENABLED must be true in production/staging" in source, \
            "API config must error when AUTH_ENABLED is false in production/staging"

    def test_regression_027_03_api_check_inside_prod_block(self):
        """RT-027-03: Auth check must be inside the production/staging block."""
        source = API_CONFIG.read_text(encoding="utf-8")
        lines = source.splitlines()
        in_prod_block = False
        found = False
        for line in lines:
            if 'settings.environment in ("production", "staging")' in line:
                in_prod_block = True
                continue
            if in_prod_block and "not settings.auth_enabled" in line:
                found = True
                break
        assert found, \
            "Auth enforcement check must be inside production/staging validation block"


# ============================================================================
# Tests: Alerting Config
# ============================================================================

class TestAlertingAuthEnforcement:
    """Validate alerting config enforces auth in production/staging."""

    def test_regression_027_04_alerting_checks_auth_disabled(self):
        """RT-027-04: Alerting config must check if auth is disabled in production."""
        source = ALERTING_CONFIG.read_text(encoding="utf-8")
        assert "not settings.auth_enabled" in source, \
            "Alerting config must check for auth disabled in production/staging"

    def test_regression_027_05_alerting_auth_error_message(self):
        """RT-027-05: Alerting config must have auth enforcement error message."""
        source = ALERTING_CONFIG.read_text(encoding="utf-8")
        assert "AUTH_ENABLED must be true in production/staging" in source, \
            "Alerting config must error when AUTH_ENABLED is false in production/staging"

    def test_regression_027_06_alerting_check_inside_prod_block(self):
        """RT-027-06: Auth check must be inside the production/staging block."""
        source = ALERTING_CONFIG.read_text(encoding="utf-8")
        lines = source.splitlines()
        in_prod_block = False
        found = False
        for line in lines:
            if 'settings.environment in ("production", "staging")' in line:
                in_prod_block = True
                continue
            if in_prod_block and "not settings.auth_enabled" in line:
                found = True
                break
        assert found, \
            "Auth enforcement check must be inside production/staging validation block"
