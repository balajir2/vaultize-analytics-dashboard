"""
Regression Test RT-013: TLS Certificate and Security Configuration Validation

Validates that OpenSearch security configuration files exist, are valid YAML,
and define required users, roles, and mappings.

Severity: Critical
Category: Security Infrastructure
Authors: Balaji Rajan and Claude (Anthropic)
"""

from pathlib import Path

import pytest
import yaml

# ============================================================================
# Constants
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SECURITY_DIR = PROJECT_ROOT / "infrastructure" / "docker" / "opensearch" / "security"
CERTS_DIR = PROJECT_ROOT / "infrastructure" / "certs"
CERT_SCRIPT_SH = PROJECT_ROOT / "scripts" / "ops" / "generate_certs.sh"
CERT_SCRIPT_PY = PROJECT_ROOT / "scripts" / "ops" / "generate_certs.py"


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def internal_users():
    """Load and parse internal_users.yml."""
    path = SECURITY_DIR / "internal_users.yml"
    assert path.exists(), f"internal_users.yml not found: {path}"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@pytest.fixture
def roles():
    """Load and parse roles.yml."""
    path = SECURITY_DIR / "roles.yml"
    assert path.exists(), f"roles.yml not found: {path}"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@pytest.fixture
def roles_mapping():
    """Load and parse roles_mapping.yml."""
    path = SECURITY_DIR / "roles_mapping.yml"
    assert path.exists(), f"roles_mapping.yml not found: {path}"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@pytest.fixture
def security_config():
    """Load and parse config.yml."""
    path = SECURITY_DIR / "config.yml"
    assert path.exists(), f"config.yml not found: {path}"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


# ============================================================================
# Tests: Security Files Exist
# ============================================================================

class TestSecurityFilesExist:
    """Validate all required security configuration files exist."""

    def test_security_directory_exists(self):
        """RT-013-01: Security config directory must exist."""
        assert SECURITY_DIR.exists(), f"Security directory not found: {SECURITY_DIR}"

    def test_internal_users_exists(self):
        """RT-013-02: internal_users.yml must exist."""
        assert (SECURITY_DIR / "internal_users.yml").exists()

    def test_roles_exists(self):
        """RT-013-03: roles.yml must exist."""
        assert (SECURITY_DIR / "roles.yml").exists()

    def test_roles_mapping_exists(self):
        """RT-013-04: roles_mapping.yml must exist."""
        assert (SECURITY_DIR / "roles_mapping.yml").exists()

    def test_config_exists(self):
        """RT-013-05: config.yml must exist."""
        assert (SECURITY_DIR / "config.yml").exists()

    def test_certs_directory_exists(self):
        """RT-013-06: infrastructure/certs/ directory must exist."""
        assert CERTS_DIR.exists(), f"Certs directory not found: {CERTS_DIR}"


# ============================================================================
# Tests: Certificate Generation Scripts
# ============================================================================

class TestCertScripts:
    """Validate certificate generation scripts exist."""

    def test_bash_script_exists(self):
        """RT-013-07: Bash cert generation script must exist."""
        assert CERT_SCRIPT_SH.exists(), f"Script not found: {CERT_SCRIPT_SH}"

    def test_python_script_exists(self):
        """RT-013-08: Python cert generation script must exist."""
        assert CERT_SCRIPT_PY.exists(), f"Script not found: {CERT_SCRIPT_PY}"

    def test_bash_script_is_executable_content(self):
        """RT-013-09: Bash script must start with shebang."""
        content = CERT_SCRIPT_SH.read_text(encoding="utf-8")
        assert content.startswith("#!/bin/bash"), "Bash script missing shebang line"

    def test_python_script_has_cryptography_import(self):
        """RT-013-10: Python script must import cryptography library."""
        content = CERT_SCRIPT_PY.read_text(encoding="utf-8")
        assert "from cryptography" in content, "Python script must use cryptography library"


# ============================================================================
# Tests: Internal Users Configuration
# ============================================================================

class TestInternalUsers:
    """Validate internal_users.yml defines required users."""

    def test_has_meta_section(self, internal_users):
        """RT-013-11: Must have _meta section with correct type."""
        assert "_meta" in internal_users
        assert internal_users["_meta"]["type"] == "internalusers"
        assert internal_users["_meta"]["config_version"] == 2

    def test_admin_user_defined(self, internal_users):
        """RT-013-12: Admin user must be defined."""
        assert "admin" in internal_users, "admin user not defined"
        admin = internal_users["admin"]
        assert "hash" in admin, "admin missing password hash"
        assert admin.get("reserved") is True, "admin should be reserved"

    def test_fluent_bit_writer_defined(self, internal_users):
        """RT-013-13: Fluent Bit writer user must be defined."""
        assert "fluent_bit_writer" in internal_users, "fluent_bit_writer user not defined"
        user = internal_users["fluent_bit_writer"]
        assert "hash" in user, "fluent_bit_writer missing password hash"
        assert "logwriter" in user.get("backend_roles", []), \
            "fluent_bit_writer must have 'logwriter' backend role"

    def test_api_user_defined(self, internal_users):
        """RT-013-14: API user must be defined."""
        assert "api_user" in internal_users, "api_user not defined"
        user = internal_users["api_user"]
        assert "hash" in user, "api_user missing password hash"

    def test_viewer_user_defined(self, internal_users):
        """RT-013-15: Viewer user must be defined."""
        assert "viewer" in internal_users, "viewer user not defined"


# ============================================================================
# Tests: Roles Configuration
# ============================================================================

class TestRoles:
    """Validate roles.yml defines required roles."""

    def test_has_meta_section(self, roles):
        """RT-013-16: Must have _meta section with correct type."""
        assert "_meta" in roles
        assert roles["_meta"]["type"] == "roles"

    def test_log_writer_role_defined(self, roles):
        """RT-013-17: log_writer role must be defined."""
        assert "log_writer" in roles, "log_writer role not defined"
        role = roles["log_writer"]
        assert "index_permissions" in role, "log_writer missing index_permissions"

    def test_log_reader_role_defined(self, roles):
        """RT-013-18: log_reader role must be defined."""
        assert "log_reader" in roles, "log_reader role not defined"

    def test_alert_manager_role_defined(self, roles):
        """RT-013-19: alert_manager role must be defined."""
        assert "alert_manager" in roles, "alert_manager role not defined"
        role = roles["alert_manager"]
        # alert_manager must have access to .alerts-* indices
        index_patterns = []
        for perm in role.get("index_permissions", []):
            index_patterns.extend(perm.get("index_patterns", []))
        assert any(".alerts-" in p for p in index_patterns), \
            "alert_manager must have access to .alerts-* indices"

    def test_admin_full_role_defined(self, roles):
        """RT-013-20: admin_full role must be defined."""
        assert "admin_full" in roles, "admin_full role not defined"

    def test_log_writer_can_write_logs(self, roles):
        """RT-013-21: log_writer must have write access to logs-* indices."""
        role = roles["log_writer"]
        index_patterns = []
        for perm in role.get("index_permissions", []):
            index_patterns.extend(perm.get("index_patterns", []))
        assert any("logs-" in p for p in index_patterns), \
            "log_writer must have access to logs-* indices"


# ============================================================================
# Tests: Roles Mapping Configuration
# ============================================================================

class TestRolesMapping:
    """Validate roles_mapping.yml maps backend roles correctly."""

    def test_has_meta_section(self, roles_mapping):
        """RT-013-22: Must have _meta section with correct type."""
        assert "_meta" in roles_mapping
        assert roles_mapping["_meta"]["type"] == "rolesmapping"

    def test_admin_mapping_exists(self, roles_mapping):
        """RT-013-23: Admin role mapping must exist."""
        assert "admin_full" in roles_mapping or "all_access" in roles_mapping, \
            "Admin role mapping not found"

    def test_log_writer_mapping_exists(self, roles_mapping):
        """RT-013-24: Log writer role mapping must exist."""
        assert "log_writer" in roles_mapping, "log_writer mapping not defined"
        mapping = roles_mapping["log_writer"]
        assert "logwriter" in mapping.get("backend_roles", []), \
            "log_writer mapping must include 'logwriter' backend role"


# ============================================================================
# Tests: Security Config
# ============================================================================

class TestSecurityConfig:
    """Validate config.yml security configuration."""

    def test_has_config_section(self, security_config):
        """RT-013-25: Must have config.dynamic section."""
        assert "config" in security_config
        assert "dynamic" in security_config["config"]

    def test_has_authc_section(self, security_config):
        """RT-013-26: Must have authentication configuration."""
        dynamic = security_config["config"]["dynamic"]
        assert "authc" in dynamic, "Missing authc (authentication) configuration"

    def test_has_basic_auth(self, security_config):
        """RT-013-27: Must have HTTP basic authentication configured."""
        authc = security_config["config"]["dynamic"]["authc"]
        # Find a basic auth domain
        has_basic = any(
            domain.get("http_authenticator", {}).get("type") == "basic"
            for domain in authc.values()
            if isinstance(domain, dict)
        )
        assert has_basic, "No HTTP basic authentication domain configured"

    def test_anonymous_auth_disabled(self, security_config):
        """RT-013-28: Anonymous authentication must be disabled."""
        http_config = security_config["config"]["dynamic"].get("http", {})
        assert http_config.get("anonymous_auth_enabled") is False, \
            "Anonymous authentication must be disabled"
