"""
Regression Test RT-029: Dev CORS Wildcard No Credentials

Validates that the dev/wildcard CORS branch in main.py sets
allow_credentials=False to avoid the browser-incompatible
wildcard+credentials combination. Also validates the warning
log still exists for wildcard CORS usage.

Date: 2026-02-22
Severity: Low
Category: Security - CORS
Authors: Balaji Rajan and Claude (Anthropic)
"""

from pathlib import Path

import pytest

# ============================================================================
# Constants
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
API_MAIN = PROJECT_ROOT / "analytics" / "api" / "app" / "main.py"


# ============================================================================
# Tests: Wildcard CORS Branch
# ============================================================================

class TestDevCorsWildcardNoCredentials:
    """Validate CORS wildcard branch disables credentials."""

    def test_regression_029_01_wildcard_branch_credentials_false(self):
        """RT-029-01: Wildcard CORS branch must use allow_credentials=False."""
        source = API_MAIN.read_text(encoding="utf-8")
        lines = source.splitlines()
        in_else = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("else:"):
                in_else = True
                continue
            if not in_else:
                continue
            # Skip string literals (log messages containing allow_credentials text)
            if stripped.startswith('"') or stripped.startswith("'"):
                continue
            if "allow_credentials=False" in line:
                return  # Pass
            if "allow_credentials=True" in line:
                pytest.fail(
                    "Wildcard CORS branch must use allow_credentials=False, "
                    f"found allow_credentials=True at line {i + 1}"
                )
        pytest.fail("Could not find allow_credentials setting in wildcard CORS branch")

    def test_regression_029_02_wildcard_origins_explicit(self):
        """RT-029-02: Wildcard CORS branch must set allow_origins=["*"]."""
        source = API_MAIN.read_text(encoding="utf-8")
        lines = source.splitlines()
        in_else = False
        found = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("else:"):
                in_else = True
                continue
            if in_else and 'allow_origins=["*"]' in line:
                found = True
                break
        assert found, \
            'Wildcard CORS branch must explicitly set allow_origins=["*"]'

    def test_regression_029_03_warning_log_still_exists(self):
        """RT-029-03: Warning log for wildcard CORS usage must still exist."""
        source = API_MAIN.read_text(encoding="utf-8")
        lines = source.splitlines()
        in_else = False
        found_warning = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("else:"):
                in_else = True
                continue
            if in_else and "logger.warning" in line:
                found_warning = True
                break
        assert found_warning, \
            "Warning log for wildcard CORS usage must still be present in the else branch"

    def test_regression_029_04_no_wildcard_credentials_combo(self):
        """RT-029-04: No CORSMiddleware call should combine wildcard + credentials=True."""
        source = API_MAIN.read_text(encoding="utf-8")
        lines = source.splitlines()
        in_cors_middleware = False
        has_wildcard = False
        has_cred_true = False
        for line in lines:
            stripped = line.strip()
            if "CORSMiddleware" in stripped:
                in_cors_middleware = True
                has_wildcard = False
                has_cred_true = False
                continue
            if in_cors_middleware:
                if 'allow_origins=["*"]' in stripped:
                    has_wildcard = True
                if "allow_credentials=True" in stripped:
                    has_cred_true = True
                if stripped.startswith(")"):
                    if has_wildcard and has_cred_true:
                        pytest.fail(
                            "CORSMiddleware must not combine allow_origins=['*'] "
                            "with allow_credentials=True"
                        )
                    in_cors_middleware = False
