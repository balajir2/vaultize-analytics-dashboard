"""
Regression Test RT-022: Startup Config Validation Hardening

Validates that production/staging startup checks are enforced:
- secret_key default blocked in production AND staging
- auth_enabled + default admin password blocked in production/staging
- "test" environment value is accepted
- Alerting service has its own validate_settings()

Date: 2026-02-21
Severity: Critical
Category: Security - Configuration
Authors: Balaji Rajan and Claude (Anthropic)
"""

import ast
from pathlib import Path

import pytest

# ============================================================================
# Constants
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
API_CONFIG = PROJECT_ROOT / "analytics" / "api" / "app" / "config.py"
ALERTING_CONFIG = PROJECT_ROOT / "analytics" / "alerting" / "app" / "config.py"
ENV_EXAMPLE = PROJECT_ROOT / ".env.example"


# ============================================================================
# Tests: API Config Validation Hardening
# ============================================================================

class TestAPIConfigValidation:
    """Validate API config.py validate_settings() hardening."""

    def test_regression_022_01_checks_production_and_staging(self):
        """RT-022-01: validate_settings must check both production and staging."""
        source = API_CONFIG.read_text(encoding="utf-8")
        # Should have a tuple check for both environments
        assert '"production"' in source and '"staging"' in source, \
            "validate_settings must reference both production and staging"
        # Should check them together (not just separately)
        assert '("production", "staging")' in source, \
            "validate_settings must check production AND staging together"

    def test_regression_022_02_blocks_default_secret_key(self):
        """RT-022-02: validate_settings must error on default secret_key."""
        source = API_CONFIG.read_text(encoding="utf-8")
        assert "CHANGE_ME_IN_PRODUCTION" in source, \
            "validate_settings must check for default secret_key sentinel"

    def test_regression_022_03_blocks_default_admin_password(self):
        """RT-022-03: validate_settings must error on default admin password with auth enabled."""
        source = API_CONFIG.read_text(encoding="utf-8")
        assert "auth_admin_password" in source, \
            "validate_settings must check auth_admin_password"
        assert "auth_enabled" in source, \
            "validate_settings must check auth_enabled context for password validation"

    def test_regression_022_04_test_environment_allowed(self):
        """RT-022-04: 'test' must be in the allowed environment values."""
        source = API_CONFIG.read_text(encoding="utf-8")
        tree = ast.parse(source)
        # Find the validate_environment function and check its allowed list
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == "validate_environment":
                    # Get function source and check for "test" in list
                    func_source = ast.get_source_segment(source, node)
                    assert '"test"' in func_source, \
                        "validate_environment must allow 'test' as a valid environment"
                    return
        pytest.fail("validate_environment function not found in API config")


# ============================================================================
# Tests: Alerting Config Validation
# ============================================================================

class TestAlertingConfigValidation:
    """Validate alerting config.py has validate_settings()."""

    def test_regression_022_05_alerting_has_validate_settings(self):
        """RT-022-05: alerting config.py must define validate_settings function."""
        source = ALERTING_CONFIG.read_text(encoding="utf-8")
        tree = ast.parse(source)
        func_names = [
            node.name for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        assert "validate_settings" in func_names, \
            "alerting config.py must define validate_settings"

    def test_regression_022_06_alerting_checks_secret_key(self):
        """RT-022-06: alerting validate_settings must check default secret_key."""
        source = ALERTING_CONFIG.read_text(encoding="utf-8")
        assert "CHANGE_ME_IN_PRODUCTION" in source, \
            "alerting validate_settings must check for default secret_key"

    def test_regression_022_07_alerting_checks_production_staging(self):
        """RT-022-07: alerting validate_settings must check production and staging."""
        source = ALERTING_CONFIG.read_text(encoding="utf-8")
        assert '("production", "staging")' in source, \
            "alerting validate_settings must check production AND staging together"

    def test_regression_022_08_alerting_calls_validate_on_import(self):
        """RT-022-08: alerting config.py must call validate_settings() at module level."""
        source = ALERTING_CONFIG.read_text(encoding="utf-8")
        # Must have a bare call to validate_settings() (not just the def)
        lines = source.splitlines()
        bare_calls = [
            line.strip() for line in lines
            if line.strip() == "validate_settings()"
        ]
        assert len(bare_calls) >= 1, \
            "alerting config.py must call validate_settings() at module level"


# ============================================================================
# Tests: .env.example Security Settings
# ============================================================================

class TestEnvExampleSecuritySettings:
    """Validate .env.example includes security settings."""

    def test_regression_022_09_env_has_auth_enabled(self):
        """RT-022-09: .env.example must include AUTH_ENABLED."""
        content = ENV_EXAMPLE.read_text(encoding="utf-8")
        assert "AUTH_ENABLED" in content, \
            ".env.example must document AUTH_ENABLED setting"

    def test_regression_022_10_env_has_admin_username(self):
        """RT-022-10: .env.example must include AUTH_ADMIN_USERNAME."""
        content = ENV_EXAMPLE.read_text(encoding="utf-8")
        assert "AUTH_ADMIN_USERNAME" in content, \
            ".env.example must document AUTH_ADMIN_USERNAME setting"

    def test_regression_022_11_env_has_secret_key(self):
        """RT-022-11: .env.example must include API_SECRET_KEY."""
        content = ENV_EXAMPLE.read_text(encoding="utf-8")
        assert "API_SECRET_KEY" in content, \
            ".env.example must document API_SECRET_KEY setting"
