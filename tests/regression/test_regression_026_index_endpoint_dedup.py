"""
Regression Test RT-026: Index Endpoint Deduplication

Validates that the duplicate list_indices endpoint in search.py
has been removed. The canonical endpoint is GET /api/v1/indices/
in indices.py (returns detailed info). The removed endpoint was
GET /api/v1/indices in search.py (returned only List[str]).

Date: 2026-02-21
Severity: Low
Category: Code Quality - API Surface
Authors: Balaji Rajan and Claude (Anthropic)
"""

import ast
from pathlib import Path

import pytest

# ============================================================================
# Constants
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SEARCH_ROUTER = PROJECT_ROOT / "analytics" / "api" / "app" / "routers" / "search.py"
INDICES_ROUTER = PROJECT_ROOT / "analytics" / "api" / "app" / "routers" / "indices.py"


# ============================================================================
# Tests: Duplicate Removed
# ============================================================================

class TestIndexEndpointDedup:
    """Validate the duplicate list_indices is removed from search.py."""

    def test_regression_026_01_search_has_no_list_indices(self):
        """RT-026-01: search.py must NOT have a list_indices function."""
        source = SEARCH_ROUTER.read_text(encoding="utf-8")
        tree = ast.parse(source)
        func_names = [
            node.name for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        assert "list_indices" not in func_names, \
            "search.py must not define list_indices (use indices.py instead)"

    def test_regression_026_02_search_has_no_indices_route(self):
        """RT-026-02: search.py must NOT have a /indices GET route."""
        source = SEARCH_ROUTER.read_text(encoding="utf-8")
        lines = source.splitlines()
        for line in lines:
            if "@router.get" in line and '"/indices"' in line:
                pytest.fail("search.py must not have a GET /indices route")

    def test_regression_026_03_indices_router_has_list_all(self):
        """RT-026-03: indices.py must have the canonical list_all_indices function."""
        source = INDICES_ROUTER.read_text(encoding="utf-8")
        tree = ast.parse(source)
        func_names = [
            node.name for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        assert "list_all_indices" in func_names, \
            "indices.py must define the canonical list_all_indices endpoint"
