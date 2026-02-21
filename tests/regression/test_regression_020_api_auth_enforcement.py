"""
Regression Test RT-020: API Route Auth Enforcement

Validates that protected API routes require authentication via
Depends(get_current_user) at the router level, and that destructive
DELETE operations require admin role via Depends(require_admin).
Health and auth endpoints must remain public.

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
API_MAIN = PROJECT_ROOT / "analytics" / "api" / "app" / "main.py"
INDICES_ROUTER = PROJECT_ROOT / "analytics" / "api" / "app" / "routers" / "indices.py"
AUTH_MIDDLEWARE = PROJECT_ROOT / "analytics" / "api" / "app" / "middleware" / "auth.py"


# ============================================================================
# Tests: Auth Import in main.py
# ============================================================================

class TestMainAuthImports:
    """Validate that main.py imports auth dependencies."""

    def test_regression_020_01_main_imports_depends(self):
        """RT-020-01: main.py must import Depends from fastapi."""
        source = API_MAIN.read_text(encoding="utf-8")
        tree = ast.parse(source)
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "fastapi":
                names = [alias.name for alias in node.names]
                if "Depends" in names:
                    found = True
                    break
        assert found, "main.py must import Depends from fastapi"

    def test_regression_020_02_main_imports_get_current_user(self):
        """RT-020-02: main.py must import get_current_user from auth middleware."""
        source = API_MAIN.read_text(encoding="utf-8")
        tree = ast.parse(source)
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "app.middleware.auth":
                names = [alias.name for alias in node.names]
                if "get_current_user" in names:
                    found = True
                    break
        assert found, "main.py must import get_current_user from app.middleware.auth"


# ============================================================================
# Tests: Protected Router Registration
# ============================================================================

class TestProtectedRouterRegistration:
    """Validate that search, aggregations, and indices routers have auth dependencies."""

    def _get_include_router_calls(self):
        """Parse main.py and return all include_router call AST nodes."""
        source = API_MAIN.read_text(encoding="utf-8")
        tree = ast.parse(source)
        calls = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if (isinstance(func, ast.Attribute) and func.attr == "include_router"):
                    calls.append(node)
        return calls

    def _has_dependencies_kwarg(self, call_node):
        """Check if an include_router call has a dependencies keyword argument."""
        for kw in call_node.keywords:
            if kw.arg == "dependencies":
                return True
        return False

    def _get_router_name(self, call_node):
        """Extract the router module name from the first positional argument."""
        if call_node.args:
            arg = call_node.args[0]
            if isinstance(arg, ast.Attribute):
                if isinstance(arg.value, ast.Attribute):
                    return arg.value.attr
                elif isinstance(arg.value, ast.Name):
                    return arg.value.id
        return None

    def test_regression_020_03_search_router_has_auth(self):
        """RT-020-03: Search router must have dependencies=[Depends(get_current_user)]."""
        source = API_MAIN.read_text(encoding="utf-8")
        # Check that the search router include has dependencies with get_current_user
        assert "search.router" in source
        # Find the line with search.router and verify it has dependencies
        for line in source.splitlines():
            if "search.router" in line and "include_router" in line:
                assert "dependencies=" in line, "search router must have dependencies kwarg"
                assert "get_current_user" in line, "search router must use get_current_user dependency"
                break
        else:
            pytest.fail("search.router include_router call not found")

    def test_regression_020_04_aggregations_router_has_auth(self):
        """RT-020-04: Aggregations router must have dependencies=[Depends(get_current_user)]."""
        source = API_MAIN.read_text(encoding="utf-8")
        for line in source.splitlines():
            if "aggregations.router" in line and "include_router" in line:
                assert "dependencies=" in line, "aggregations router must have dependencies kwarg"
                assert "get_current_user" in line, "aggregations router must use get_current_user dependency"
                break
        else:
            pytest.fail("aggregations.router include_router call not found")

    def test_regression_020_05_indices_router_has_auth(self):
        """RT-020-05: Indices router must have dependencies=[Depends(get_current_user)]."""
        source = API_MAIN.read_text(encoding="utf-8")
        for line in source.splitlines():
            if "indices.router" in line and "include_router" in line:
                assert "dependencies=" in line, "indices router must have dependencies kwarg"
                assert "get_current_user" in line, "indices router must use get_current_user dependency"
                break
        else:
            pytest.fail("indices.router include_router call not found")


# ============================================================================
# Tests: Public Routes Stay Public
# ============================================================================

class TestPublicRoutesRemainPublic:
    """Validate that health and auth routers do NOT have auth dependencies."""

    def test_regression_020_06_health_router_is_public(self):
        """RT-020-06: Health router must NOT have auth dependencies."""
        source = API_MAIN.read_text(encoding="utf-8")
        for line in source.splitlines():
            if "health.router" in line and "include_router" in line:
                assert "dependencies=" not in line, \
                    "health router must remain public (no dependencies kwarg)"
                break
        else:
            pytest.fail("health.router include_router call not found")

    def test_regression_020_07_auth_router_is_public(self):
        """RT-020-07: Auth router must NOT have auth dependencies."""
        source = API_MAIN.read_text(encoding="utf-8")
        for line in source.splitlines():
            if "auth.router" in line and "include_router" in line:
                assert "dependencies=" not in line, \
                    "auth router must remain public (no dependencies kwarg)"
                break
        else:
            pytest.fail("auth.router include_router call not found")


# ============================================================================
# Tests: DELETE Index Requires Admin
# ============================================================================

class TestDeleteIndexRequiresAdmin:
    """Validate that DELETE /{index_name} requires admin role."""

    def test_regression_020_08_indices_imports_require_admin(self):
        """RT-020-08: indices.py must import require_admin from auth middleware."""
        source = INDICES_ROUTER.read_text(encoding="utf-8")
        tree = ast.parse(source)
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "app.middleware.auth":
                names = [alias.name for alias in node.names]
                if "require_admin" in names:
                    found = True
                    break
        assert found, "indices.py must import require_admin from app.middleware.auth"

    def test_regression_020_09_delete_endpoint_has_admin_dependency(self):
        """RT-020-09: DELETE endpoint decorator must include dependencies=[Depends(require_admin)]."""
        source = INDICES_ROUTER.read_text(encoding="utf-8")
        # Find the @router.delete decorator line
        lines = source.splitlines()
        for i, line in enumerate(lines):
            if "@router.delete" in line:
                assert "dependencies=" in line, \
                    "DELETE endpoint must have dependencies kwarg"
                assert "require_admin" in line, \
                    "DELETE endpoint must use require_admin dependency"
                break
        else:
            pytest.fail("@router.delete decorator not found in indices.py")

    def test_regression_020_10_get_endpoints_no_admin(self):
        """RT-020-10: GET endpoints in indices.py must NOT have require_admin."""
        source = INDICES_ROUTER.read_text(encoding="utf-8")
        lines = source.splitlines()
        for line in lines:
            if "@router.get" in line:
                assert "require_admin" not in line, \
                    "GET endpoints should not require admin — use router-level get_current_user only"


# ============================================================================
# Tests: Auth Middleware Functions Exist
# ============================================================================

class TestAuthMiddlewareFunctions:
    """Validate that the auth middleware has the required functions."""

    def test_regression_020_11_get_current_user_exists(self):
        """RT-020-11: auth.py must define get_current_user function."""
        source = AUTH_MIDDLEWARE.read_text(encoding="utf-8")
        tree = ast.parse(source)
        func_names = [
            node.name for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        assert "get_current_user" in func_names, \
            "auth.py must define get_current_user"

    def test_regression_020_12_require_admin_exists(self):
        """RT-020-12: auth.py must define require_admin function."""
        source = AUTH_MIDDLEWARE.read_text(encoding="utf-8")
        tree = ast.parse(source)
        func_names = [
            node.name for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        assert "require_admin" in func_names, \
            "auth.py must define require_admin"

    def test_regression_020_13_auth_disabled_returns_none(self):
        """RT-020-13: get_current_user must return None when auth is disabled."""
        source = AUTH_MIDDLEWARE.read_text(encoding="utf-8")
        # Verify the auth_enabled check and None return pattern exist
        assert "if not settings.auth_enabled:" in source, \
            "get_current_user must check settings.auth_enabled"
        assert "return None" in source, \
            "get_current_user must return None when auth disabled"
