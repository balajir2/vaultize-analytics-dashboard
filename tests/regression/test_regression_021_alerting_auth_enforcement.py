"""
Regression Test RT-021: Alerting Service Auth Enforcement

Validates that the alerting management API requires authentication
via Depends(get_current_user) at the router level, and that
admin-only endpoints (reload, trigger) require Depends(require_admin).
Health endpoint must remain public.

Date: 2026-02-21
Severity: Critical
Category: Security - Route Protection
Authors: Balaji Rajan and Claude (Anthropic)
"""

import ast
from pathlib import Path

import pytest

# ============================================================================
# Constants
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ALERTING_MAIN = PROJECT_ROOT / "analytics" / "alerting" / "app" / "main.py"
ALERTS_ROUTER = PROJECT_ROOT / "analytics" / "alerting" / "app" / "routers" / "alerts.py"
AUTH_MIDDLEWARE = PROJECT_ROOT / "analytics" / "alerting" / "app" / "middleware" / "auth.py"


# ============================================================================
# Tests: require_admin Exists in Alerting Auth
# ============================================================================

class TestAlertingAuthMiddleware:
    """Validate that alerting auth middleware has require_admin."""

    def test_regression_021_01_require_admin_defined(self):
        """RT-021-01: alerting auth.py must define require_admin function."""
        source = AUTH_MIDDLEWARE.read_text(encoding="utf-8")
        tree = ast.parse(source)
        func_names = [
            node.name for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        assert "require_admin" in func_names, \
            "alerting auth.py must define require_admin"

    def test_regression_021_02_get_current_user_defined(self):
        """RT-021-02: alerting auth.py must define get_current_user function."""
        source = AUTH_MIDDLEWARE.read_text(encoding="utf-8")
        tree = ast.parse(source)
        func_names = [
            node.name for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        assert "get_current_user" in func_names, \
            "alerting auth.py must define get_current_user"

    def test_regression_021_03_require_admin_checks_role(self):
        """RT-021-03: require_admin must check user role."""
        source = AUTH_MIDDLEWARE.read_text(encoding="utf-8")
        assert '"admin"' in source or "'admin'" in source, \
            "require_admin must check for admin role"

    def test_regression_021_04_auth_disabled_bypasses(self):
        """RT-021-04: Both functions must check settings.auth_enabled."""
        source = AUTH_MIDDLEWARE.read_text(encoding="utf-8")
        # Should have at least two auth_enabled checks (one per function)
        count = source.count("settings.auth_enabled")
        assert count >= 2, \
            f"Expected at least 2 auth_enabled checks, found {count}"


# ============================================================================
# Tests: Main.py Auth Registration
# ============================================================================

class TestAlertingMainAuth:
    """Validate that alerting main.py registers auth on alerts router."""

    def test_regression_021_05_main_imports_depends(self):
        """RT-021-05: alerting main.py must import Depends from fastapi."""
        source = ALERTING_MAIN.read_text(encoding="utf-8")
        tree = ast.parse(source)
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "fastapi":
                names = [alias.name for alias in node.names]
                if "Depends" in names:
                    found = True
                    break
        assert found, "alerting main.py must import Depends from fastapi"

    def test_regression_021_06_alerts_router_has_auth(self):
        """RT-021-06: Alerts router include must have dependencies with get_current_user."""
        source = ALERTING_MAIN.read_text(encoding="utf-8")
        for line in source.splitlines():
            if "alerts.router" in line and "include_router" in line:
                assert "dependencies=" in line, \
                    "alerts router must have dependencies kwarg"
                assert "get_current_user" in line, \
                    "alerts router must use get_current_user dependency"
                break
        else:
            pytest.fail("alerts.router include_router call not found")

    def test_regression_021_07_health_router_is_public(self):
        """RT-021-07: Health router must NOT have auth dependencies."""
        source = ALERTING_MAIN.read_text(encoding="utf-8")
        for line in source.splitlines():
            if "health.router" in line and "include_router" in line:
                assert "dependencies=" not in line, \
                    "health router must remain public (no dependencies kwarg)"
                break
        else:
            pytest.fail("health.router include_router call not found")


# ============================================================================
# Tests: Admin-Only Endpoints
# ============================================================================

class TestAlertingAdminEndpoints:
    """Validate that reload and trigger endpoints require admin."""

    def test_regression_021_08_alerts_router_imports_require_admin(self):
        """RT-021-08: alerts.py must import require_admin."""
        source = ALERTS_ROUTER.read_text(encoding="utf-8")
        tree = ast.parse(source)
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "app.middleware.auth":
                names = [alias.name for alias in node.names]
                if "require_admin" in names:
                    found = True
                    break
        assert found, "alerts.py must import require_admin from app.middleware.auth"

    def test_regression_021_09_trigger_requires_admin(self):
        """RT-021-09: POST /rules/{name}/trigger must have require_admin dependency."""
        source = ALERTS_ROUTER.read_text(encoding="utf-8")
        lines = source.splitlines()
        for line in lines:
            if "rules/{rule_name}/trigger" in line and "@router.post" in line:
                assert "require_admin" in line, \
                    "trigger endpoint must use require_admin dependency"
                break
        else:
            pytest.fail("trigger endpoint decorator not found")

    def test_regression_021_10_reload_requires_admin(self):
        """RT-021-10: POST /rules/reload must have require_admin dependency."""
        source = ALERTS_ROUTER.read_text(encoding="utf-8")
        lines = source.splitlines()
        for line in lines:
            if "rules/reload" in line and "@router.post" in line:
                assert "require_admin" in line, \
                    "reload endpoint must use require_admin dependency"
                break
        else:
            pytest.fail("reload endpoint decorator not found")

    def test_regression_021_11_get_endpoints_no_admin(self):
        """RT-021-11: GET endpoints in alerts.py must NOT have require_admin."""
        source = ALERTS_ROUTER.read_text(encoding="utf-8")
        lines = source.splitlines()
        for line in lines:
            if "@router.get" in line:
                assert "require_admin" not in line, \
                    "GET endpoints should not require admin — use router-level get_current_user only"
