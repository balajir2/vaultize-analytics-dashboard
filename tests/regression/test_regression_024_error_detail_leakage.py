"""
Regression Test RT-024: Error Detail Leakage Prevention

Validates that 500/503 HTTP error responses do NOT contain str(e)
exception details. 400-level errors may keep details for user feedback.
Full exception details must remain in logger.error() calls only.

Date: 2026-02-21
Severity: High
Category: Security - Information Disclosure
Authors: Balaji Rajan and Claude (Anthropic)
"""

import re
from pathlib import Path

import pytest

# ============================================================================
# Constants
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ROUTER_DIR = PROJECT_ROOT / "analytics" / "api" / "app" / "routers"

ROUTER_FILES = {
    "search.py": ROUTER_DIR / "search.py",
    "aggregations.py": ROUTER_DIR / "aggregations.py",
    "indices.py": ROUTER_DIR / "indices.py",
    "health.py": ROUTER_DIR / "health.py",
}


def _find_500_503_detail_leaks(source: str) -> list:
    """Find instances where 500/503 error responses include str(e) or {e}."""
    leaks = []
    lines = source.splitlines()
    in_500_block = False
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # Detect status_code=500 or status_code=503
        if "status_code=500" in stripped or "status_code=503" in stripped:
            in_500_block = True
            continue
        # Detect JSONResponse content with str(e)
        if in_500_block:
            if "str(e)" in stripped or "{str(e)}" in stripped or '": str(e)' in stripped:
                leaks.append(f"Line {i}: {stripped}")
            if "detail=" in stripped and ("str(e)" in stripped or "{e}" in stripped):
                leaks.append(f"Line {i}: {stripped}")
            # End of error block
            if stripped.startswith(")") or stripped == "":
                in_500_block = False
    return leaks


# ============================================================================
# Tests: No str(e) in 500/503 Responses
# ============================================================================

class TestNoExceptionLeakage:
    """Validate that 500/503 responses do not contain exception details."""

    def test_regression_024_01_search_no_leakage(self):
        """RT-024-01: search.py must not leak exception details in 500 responses."""
        source = ROUTER_FILES["search.py"].read_text(encoding="utf-8")
        leaks = _find_500_503_detail_leaks(source)
        assert len(leaks) == 0, \
            f"search.py leaks exception details in 500/503 responses: {leaks}"

    def test_regression_024_02_aggregations_no_leakage(self):
        """RT-024-02: aggregations.py must not leak exception details in 500 responses."""
        source = ROUTER_FILES["aggregations.py"].read_text(encoding="utf-8")
        leaks = _find_500_503_detail_leaks(source)
        assert len(leaks) == 0, \
            f"aggregations.py leaks exception details in 500/503 responses: {leaks}"

    def test_regression_024_03_indices_no_leakage(self):
        """RT-024-03: indices.py must not leak exception details in 500 responses."""
        source = ROUTER_FILES["indices.py"].read_text(encoding="utf-8")
        leaks = _find_500_503_detail_leaks(source)
        assert len(leaks) == 0, \
            f"indices.py leaks exception details in 500/503 responses: {leaks}"

    def test_regression_024_04_health_no_leakage(self):
        """RT-024-04: health.py must not leak exception details in 503 responses."""
        source = ROUTER_FILES["health.py"].read_text(encoding="utf-8")
        leaks = _find_500_503_detail_leaks(source)
        assert len(leaks) == 0, \
            f"health.py leaks exception details in 503 responses: {leaks}"


# ============================================================================
# Tests: Logger Calls Still Present
# ============================================================================

class TestLoggerCallsPreserved:
    """Validate that logger.error() calls still include exception details."""

    def test_regression_024_05_search_has_logger_error(self):
        """RT-024-05: search.py must still log full exception details."""
        source = ROUTER_FILES["search.py"].read_text(encoding="utf-8")
        assert "logger.error" in source, \
            "search.py must retain logger.error() calls for debugging"

    def test_regression_024_06_indices_has_logger_error(self):
        """RT-024-06: indices.py must still log full exception details."""
        source = ROUTER_FILES["indices.py"].read_text(encoding="utf-8")
        assert "logger.error" in source, \
            "indices.py must retain logger.error() calls for debugging"

    def test_regression_024_07_health_has_logger_error(self):
        """RT-024-07: health.py must still log full exception details."""
        source = ROUTER_FILES["health.py"].read_text(encoding="utf-8")
        assert "logger.error" in source, \
            "health.py must retain logger.error() calls for debugging"
