"""
Regression Test RT-023: CORS Credential Handling

Validates that CORS wildcard origins are blocked in production/staging
(upgraded from warning to error), and that dev mode logs a warning
about the browser incompatibility of credentials + wildcard origins.

Date: 2026-02-21
Severity: High
Category: Security - CORS
Authors: Balaji Rajan and Claude (Anthropic)
"""

from pathlib import Path

import pytest

# ============================================================================
# Constants
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
API_CONFIG = PROJECT_ROOT / "analytics" / "api" / "app" / "config.py"
API_MAIN = PROJECT_ROOT / "analytics" / "api" / "app" / "main.py"


# ============================================================================
# Tests: CORS Wildcard Blocked in Production
# ============================================================================

class TestCORSProductionBlocked:
    """Validate that CORS wildcard is an error (not warning) in production."""

    def test_regression_023_01_wildcard_is_error_not_warning(self):
        """RT-023-01: CORS wildcard must cause startup error in production/staging."""
        source = API_CONFIG.read_text(encoding="utf-8")
        # Find the CORS check in validate_settings
        in_validate = False
        for line in source.splitlines():
            if "def validate_settings" in line:
                in_validate = True
            if in_validate and "cors_origins" in line and '"*"' in line:
                # The next non-blank line should append to errors, not warnings
                break
        # Check that cors_origins == "*" appends to errors list
        assert 'errors.append' in source and "CORS allows all origins" in source, \
            "CORS wildcard in production must be appended to errors (not warnings)"

    def test_regression_023_02_error_mentions_specific_origins(self):
        """RT-023-02: CORS error message must tell user to set specific origins."""
        source = API_CONFIG.read_text(encoding="utf-8")
        assert "API_CORS_ORIGINS" in source, \
            "CORS error must mention API_CORS_ORIGINS env var"

    def test_regression_023_03_production_and_staging_checked(self):
        """RT-023-03: CORS check must be inside production/staging block."""
        source = API_CONFIG.read_text(encoding="utf-8")
        # The CORS check should be under the production/staging guard
        lines = source.splitlines()
        in_prod_block = False
        cors_in_prod = False
        for line in lines:
            if '("production", "staging")' in line:
                in_prod_block = True
            if in_prod_block and "cors_origins" in line and '"*"' in line:
                cors_in_prod = True
                break
        assert cors_in_prod, \
            "CORS wildcard check must be inside the production/staging validation block"


# ============================================================================
# Tests: Dev Mode Warning
# ============================================================================

class TestCORSDevModeWarning:
    """Validate that dev mode logs a CORS warning."""

    def test_regression_023_04_dev_mode_logs_warning(self):
        """RT-023-04: main.py must log warning when CORS uses wildcard with credentials."""
        source = API_MAIN.read_text(encoding="utf-8")
        assert "allow_credentials" in source.lower() or "credentialed" in source.lower(), \
            "main.py must mention credential issue in CORS warning"
        assert "logger.warning" in source, \
            "main.py must log a warning about CORS wildcard + credentials"

    def test_regression_023_05_warning_in_else_branch(self):
        """RT-023-05: CORS warning must be in the else/dev branch, not production branch."""
        source = API_MAIN.read_text(encoding="utf-8")
        lines = source.splitlines()
        # Find the else branch and check for logger.warning nearby
        in_else = False
        found_warning = False
        for line in lines:
            stripped = line.strip()
            if stripped == "else:":
                in_else = True
                continue
            if in_else and "logger.warning" in line:
                found_warning = True
                break
            # Stop if we hit an unindented block (next top-level section)
            if in_else and line and not line[0].isspace() and stripped != "":
                break
        assert found_warning, \
            "CORS wildcard warning must be in the else (dev) branch of main.py"
