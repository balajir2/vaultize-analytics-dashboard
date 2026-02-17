"""
Regression Test RT-017: Operations Scripts and DR Documentation

Validates that backup/restore scripts, health check, bootstrap,
and disaster recovery documentation are properly implemented.

Severity: High
Category: Operations - Backup & DR
Authors: Balaji Rajan and Claude (Anthropic)
"""

import ast
from pathlib import Path

import pytest

# ============================================================================
# Constants
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_OPS = PROJECT_ROOT / "scripts" / "ops"
DOCS_OPS = PROJECT_ROOT / "docs" / "operations"


# ============================================================================
# Tests: Script Files Exist
# ============================================================================

class TestOpsScriptsExist:
    """Validate operational scripts are present."""

    def test_backup_script_exists(self):
        """RT-017-01: backup_opensearch.py must exist."""
        assert (SCRIPTS_OPS / "backup_opensearch.py").exists()

    def test_restore_script_exists(self):
        """RT-017-02: restore_opensearch.py must exist."""
        assert (SCRIPTS_OPS / "restore_opensearch.py").exists()

    def test_health_check_script_exists(self):
        """RT-017-03: health_check.py must exist."""
        assert (SCRIPTS_OPS / "health_check.py").exists()

    def test_bootstrap_script_exists(self):
        """RT-017-04: bootstrap.sh must exist."""
        assert (SCRIPTS_OPS / "bootstrap.sh").exists()


# ============================================================================
# Tests: Backup Script Content
# ============================================================================

class TestBackupScript:
    """Validate backup script has required functions."""

    @pytest.fixture
    def backup_content(self):
        return (SCRIPTS_OPS / "backup_opensearch.py").read_text(encoding="utf-8")

    def test_is_valid_python(self, backup_content):
        """RT-017-05: Backup script must be valid Python."""
        ast.parse(backup_content)

    def test_has_create_snapshot(self, backup_content):
        """RT-017-06: Must have create_snapshot function."""
        assert "def create_snapshot" in backup_content

    def test_has_list_snapshots(self, backup_content):
        """RT-017-07: Must have list_snapshots function."""
        assert "def list_snapshots" in backup_content

    def test_has_verify_snapshot(self, backup_content):
        """RT-017-08: Must have verify_snapshot function."""
        assert "def verify_snapshot" in backup_content

    def test_has_repository_management(self, backup_content):
        """RT-017-09: Must have repository management."""
        assert "ensure_repository" in backup_content

    def test_has_argparse(self, backup_content):
        """RT-017-10: Must use argparse for CLI."""
        assert "argparse" in backup_content


# ============================================================================
# Tests: Restore Script Content
# ============================================================================

class TestRestoreScript:
    """Validate restore script has required functions."""

    @pytest.fixture
    def restore_content(self):
        return (SCRIPTS_OPS / "restore_opensearch.py").read_text(encoding="utf-8")

    def test_is_valid_python(self, restore_content):
        """RT-017-11: Restore script must be valid Python."""
        ast.parse(restore_content)

    def test_has_restore_function(self, restore_content):
        """RT-017-12: Must have restore_snapshot function."""
        assert "def restore_snapshot" in restore_content

    def test_has_close_indices(self, restore_content):
        """RT-017-13: Must have close_indices function."""
        assert "def close_indices" in restore_content

    def test_supports_rename(self, restore_content):
        """RT-017-14: Must support rename-on-restore."""
        assert "rename" in restore_content


# ============================================================================
# Tests: Health Check Script
# ============================================================================

class TestHealthCheckScript:
    """Validate health check script."""

    @pytest.fixture
    def health_content(self):
        return (SCRIPTS_OPS / "health_check.py").read_text(encoding="utf-8")

    def test_is_valid_python(self, health_content):
        """RT-017-15: Health check must be valid Python."""
        ast.parse(health_content)

    def test_checks_opensearch(self, health_content):
        """RT-017-16: Must check OpenSearch health."""
        assert "opensearch" in health_content

    def test_checks_api(self, health_content):
        """RT-017-17: Must check Analytics API."""
        assert "analytics-api" in health_content

    def test_checks_alerting(self, health_content):
        """RT-017-18: Must check Alerting Service."""
        assert "alerting-service" in health_content

    def test_checks_fluent_bit(self, health_content):
        """RT-017-19: Must check Fluent Bit."""
        assert "fluent-bit" in health_content


# ============================================================================
# Tests: Bootstrap Script
# ============================================================================

class TestBootstrapScript:
    """Validate bootstrap script content."""

    @pytest.fixture
    def bootstrap_content(self):
        return (SCRIPTS_OPS / "bootstrap.sh").read_text(encoding="utf-8")

    def test_has_shebang(self, bootstrap_content):
        """RT-017-20: Must have bash shebang."""
        assert bootstrap_content.startswith("#!/")

    def test_has_set_e(self, bootstrap_content):
        """RT-017-21: Must use set -e for error handling."""
        assert "set -e" in bootstrap_content

    def test_waits_for_opensearch(self, bootstrap_content):
        """RT-017-22: Must wait for OpenSearch readiness."""
        assert "wait_for" in bootstrap_content.lower() or "Wait" in bootstrap_content

    def test_applies_index_templates(self, bootstrap_content):
        """RT-017-23: Must apply index templates."""
        assert "index-template" in bootstrap_content or "index_template" in bootstrap_content

    def test_applies_ilm_policies(self, bootstrap_content):
        """RT-017-24: Must apply ILM policies."""
        assert "ilm" in bootstrap_content.lower() or "ism" in bootstrap_content.lower()


# ============================================================================
# Tests: DR Documentation
# ============================================================================

class TestDRDocumentation:
    """Validate disaster recovery documentation."""

    def test_dr_doc_exists(self):
        """RT-017-25: Disaster recovery doc must exist."""
        assert (DOCS_OPS / "disaster-recovery.md").exists()

    def test_covers_rpo(self):
        """RT-017-26: Doc must cover RPO."""
        content = (DOCS_OPS / "disaster-recovery.md").read_text(encoding="utf-8")
        assert "RPO" in content

    def test_covers_rto(self):
        """RT-017-27: Doc must cover RTO."""
        content = (DOCS_OPS / "disaster-recovery.md").read_text(encoding="utf-8")
        assert "RTO" in content

    def test_covers_restore_procedures(self):
        """RT-017-28: Doc must cover restore procedures."""
        content = (DOCS_OPS / "disaster-recovery.md").read_text(encoding="utf-8")
        assert "Restore" in content

    def test_covers_failure_scenarios(self):
        """RT-017-29: Doc must cover failure scenarios."""
        content = (DOCS_OPS / "disaster-recovery.md").read_text(encoding="utf-8")
        assert "Scenario" in content or "failure" in content.lower()
