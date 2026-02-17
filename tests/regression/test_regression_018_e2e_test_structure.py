"""
Regression Test RT-018: E2E Test Structure Validation

Validates that E2E test files exist and follow the required conventions:
- Proper pytest markers
- Service availability fixtures
- Test organization

Severity: Medium
Category: Testing - E2E
Authors: Balaji Rajan and Claude (Anthropic)
"""

import ast
from pathlib import Path

import pytest

# ============================================================================
# Constants
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
E2E_DIR = PROJECT_ROOT / "tests" / "e2e"


# ============================================================================
# Tests: E2E Directory Structure
# ============================================================================

class TestE2EStructure:
    """Validate E2E test file organization."""

    def test_e2e_dir_exists(self):
        """RT-018-01: E2E test directory must exist."""
        assert E2E_DIR.exists()

    def test_conftest_exists(self):
        """RT-018-02: conftest.py must exist in E2E directory."""
        assert (E2E_DIR / "conftest.py").exists()

    def test_log_ingestion_flow_exists(self):
        """RT-018-03: Log ingestion flow test must exist."""
        assert (E2E_DIR / "test_log_ingestion_flow.py").exists()

    def test_alert_flow_exists(self):
        """RT-018-04: Alert flow test must exist."""
        assert (E2E_DIR / "test_alert_flow.py").exists()

    def test_dashboard_flow_exists(self):
        """RT-018-05: Dashboard flow test must exist."""
        assert (E2E_DIR / "test_dashboard_flow.py").exists()


# ============================================================================
# Tests: E2E conftest.py Content
# ============================================================================

class TestE2EConftest:
    """Validate E2E conftest has required fixtures."""

    @pytest.fixture
    def conftest_content(self):
        return (E2E_DIR / "conftest.py").read_text(encoding="utf-8")

    def test_is_valid_python(self, conftest_content):
        """RT-018-06: conftest.py must be valid Python."""
        ast.parse(conftest_content)

    def test_has_opensearch_fixture(self, conftest_content):
        """RT-018-07: Must have opensearch_available fixture."""
        assert "opensearch_available" in conftest_content

    def test_has_api_fixture(self, conftest_content):
        """RT-018-08: Must have api_available fixture."""
        assert "api_available" in conftest_content

    def test_has_alerting_fixture(self, conftest_content):
        """RT-018-09: Must have alerting_available fixture."""
        assert "alerting_available" in conftest_content

    def test_has_dashboards_fixture(self, conftest_content):
        """RT-018-10: Must have dashboards_available fixture."""
        assert "dashboards_available" in conftest_content

    def test_has_cleanup_fixture(self, conftest_content):
        """RT-018-11: Must have cleanup_test_indices fixture."""
        assert "cleanup_test_indices" in conftest_content

    def test_fixtures_skip_when_unavailable(self, conftest_content):
        """RT-018-12: Fixtures must use pytest.skip for unavailable services."""
        assert "pytest.skip" in conftest_content


# ============================================================================
# Tests: E2E Test Files Are Valid Python
# ============================================================================

class TestE2EFilesValid:
    """Validate all E2E test files parse correctly."""

    def test_log_ingestion_is_valid(self):
        """RT-018-13: Log ingestion test must be valid Python."""
        content = (E2E_DIR / "test_log_ingestion_flow.py").read_text(encoding="utf-8")
        ast.parse(content)

    def test_alert_flow_is_valid(self):
        """RT-018-14: Alert flow test must be valid Python."""
        content = (E2E_DIR / "test_alert_flow.py").read_text(encoding="utf-8")
        ast.parse(content)

    def test_dashboard_flow_is_valid(self):
        """RT-018-15: Dashboard flow test must be valid Python."""
        content = (E2E_DIR / "test_dashboard_flow.py").read_text(encoding="utf-8")
        ast.parse(content)


# ============================================================================
# Tests: E2E Test Markers
# ============================================================================

class TestE2EMarkers:
    """Validate E2E tests use proper pytest markers."""

    def test_log_ingestion_has_e2e_marker(self):
        """RT-018-16: Log ingestion test must have e2e marker."""
        content = (E2E_DIR / "test_log_ingestion_flow.py").read_text(encoding="utf-8")
        assert "pytest.mark.e2e" in content

    def test_alert_flow_has_e2e_marker(self):
        """RT-018-17: Alert flow test must have e2e marker."""
        content = (E2E_DIR / "test_alert_flow.py").read_text(encoding="utf-8")
        assert "pytest.mark.e2e" in content

    def test_dashboard_flow_has_e2e_marker(self):
        """RT-018-18: Dashboard flow test must have e2e marker."""
        content = (E2E_DIR / "test_dashboard_flow.py").read_text(encoding="utf-8")
        assert "pytest.mark.e2e" in content


# ============================================================================
# Tests: E2E Tests Use Service Fixtures
# ============================================================================

class TestE2EUseFixtures:
    """Validate E2E tests reference service fixtures."""

    def test_log_test_uses_opensearch(self):
        """RT-018-19: Log test must use opensearch_available."""
        content = (E2E_DIR / "test_log_ingestion_flow.py").read_text(encoding="utf-8")
        assert "opensearch_available" in content

    def test_log_test_uses_api(self):
        """RT-018-20: Log test must use api_available."""
        content = (E2E_DIR / "test_log_ingestion_flow.py").read_text(encoding="utf-8")
        assert "api_available" in content

    def test_alert_test_uses_alerting(self):
        """RT-018-21: Alert test must use alerting_available."""
        content = (E2E_DIR / "test_alert_flow.py").read_text(encoding="utf-8")
        assert "alerting_available" in content

    def test_dashboard_test_uses_dashboards(self):
        """RT-018-22: Dashboard test must use dashboards_available."""
        content = (E2E_DIR / "test_dashboard_flow.py").read_text(encoding="utf-8")
        assert "dashboards_available" in content
