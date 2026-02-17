"""
Regression Test RT-014: Security Override Configuration Validation

Validates that docker-compose.security.yml is a valid overlay that enables
TLS and security for all services.

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
SECURITY_COMPOSE = PROJECT_ROOT / "docker-compose.security.yml"
OPENSEARCH_SECURE_YML = PROJECT_ROOT / "infrastructure" / "docker" / "opensearch" / "opensearch-secure.yml"
DASHBOARDS_SECURE_YML = PROJECT_ROOT / "infrastructure" / "docker" / "opensearch-dashboards" / "opensearch_dashboards-secure.yml"
FLUENT_BIT_SECURE_CONF = PROJECT_ROOT / "ingestion" / "configs" / "fluent-bit" / "fluent-bit-secure.conf"
START_SCRIPT = PROJECT_ROOT / "scripts" / "ops" / "start_secure.sh"
INIT_SCRIPT = PROJECT_ROOT / "scripts" / "ops" / "initialize_security.sh"


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def compose_security():
    """Load and parse docker-compose.security.yml."""
    assert SECURITY_COMPOSE.exists(), f"Security compose not found: {SECURITY_COMPOSE}"
    return yaml.safe_load(SECURITY_COMPOSE.read_text(encoding="utf-8"))


# ============================================================================
# Tests: Files Exist
# ============================================================================

class TestSecurityFilesExist:
    """Validate all security overlay files exist."""

    def test_security_compose_exists(self):
        """RT-014-01: docker-compose.security.yml must exist."""
        assert SECURITY_COMPOSE.exists()

    def test_opensearch_secure_yml_exists(self):
        """RT-014-02: OpenSearch secure config must exist."""
        assert OPENSEARCH_SECURE_YML.exists()

    def test_dashboards_secure_yml_exists(self):
        """RT-014-03: OpenSearch Dashboards secure config must exist."""
        assert DASHBOARDS_SECURE_YML.exists()

    def test_fluent_bit_secure_conf_exists(self):
        """RT-014-04: Fluent Bit secure config must exist."""
        assert FLUENT_BIT_SECURE_CONF.exists()

    def test_start_secure_script_exists(self):
        """RT-014-05: start_secure.sh script must exist."""
        assert START_SCRIPT.exists()

    def test_init_security_script_exists(self):
        """RT-014-06: initialize_security.sh script must exist."""
        assert INIT_SCRIPT.exists()


# ============================================================================
# Tests: Docker Compose Security Overlay
# ============================================================================

class TestComposeSecurityOverlay:
    """Validate docker-compose.security.yml content."""

    def test_is_valid_yaml(self, compose_security):
        """RT-014-07: Must be valid YAML."""
        assert compose_security is not None

    def test_has_services(self, compose_security):
        """RT-014-08: Must define services."""
        assert "services" in compose_security

    def test_overrides_opensearch_nodes(self, compose_security):
        """RT-014-09: Must override all 3 OpenSearch nodes."""
        services = compose_security["services"]
        for node in ["opensearch-node-1", "opensearch-node-2", "opensearch-node-3"]:
            assert node in services, f"Missing override for {node}"

    def test_no_disable_security_plugin(self, compose_security):
        """RT-014-10: Must NOT have DISABLE_SECURITY_PLUGIN in environment."""
        for node_name in ["opensearch-node-1", "opensearch-node-2", "opensearch-node-3"]:
            node = compose_security["services"][node_name]
            env_vars = node.get("environment", [])
            for env in env_vars:
                assert "DISABLE_SECURITY_PLUGIN" not in str(env), \
                    f"Security override must not disable security plugin on {node_name}"

    def test_nodes_mount_certificates(self, compose_security):
        """RT-014-11: OpenSearch nodes must mount TLS certificates."""
        node = compose_security["services"]["opensearch-node-1"]
        volumes = [str(v) for v in node.get("volumes", [])]
        cert_paths = ["ca.pem", "node.pem", "node-key.pem"]
        for cert in cert_paths:
            assert any(cert in v for v in volumes), \
                f"opensearch-node-1 missing volume mount for {cert}"

    def test_nodes_mount_secure_config(self, compose_security):
        """RT-014-12: OpenSearch nodes must use opensearch-secure.yml."""
        node = compose_security["services"]["opensearch-node-1"]
        volumes = [str(v) for v in node.get("volumes", [])]
        assert any("opensearch-secure.yml" in v for v in volumes), \
            "opensearch-node-1 must mount opensearch-secure.yml"

    def test_dashboards_uses_https(self, compose_security):
        """RT-014-13: Dashboards must connect to OpenSearch via HTTPS."""
        dashboards = compose_security["services"]["opensearch-dashboards"]
        env_vars = dashboards.get("environment", [])
        has_https = any("https" in str(e) for e in env_vars)
        assert has_https, "Dashboards must use HTTPS for OpenSearch connection"

    def test_api_uses_https_scheme(self, compose_security):
        """RT-014-14: Analytics API must use HTTPS scheme for OpenSearch."""
        api = compose_security["services"]["analytics-api"]
        env_vars = api.get("environment", [])
        has_https = any("OPENSEARCH_SCHEME=https" in str(e) for e in env_vars)
        assert has_https, "Analytics API must set OPENSEARCH_SCHEME=https"

    def test_alerting_uses_https_scheme(self, compose_security):
        """RT-014-15: Alerting service must use HTTPS scheme for OpenSearch."""
        alerting = compose_security["services"]["alerting-service"]
        env_vars = alerting.get("environment", [])
        has_https = any("OPENSEARCH_SCHEME=https" in str(e) for e in env_vars)
        assert has_https, "Alerting service must set OPENSEARCH_SCHEME=https"


# ============================================================================
# Tests: OpenSearch Secure Configuration
# ============================================================================

class TestOpenSearchSecureConfig:
    """Validate opensearch-secure.yml has security settings."""

    def test_has_tls_transport_settings(self):
        """RT-014-16: Must configure TLS for transport layer."""
        content = OPENSEARCH_SECURE_YML.read_text(encoding="utf-8")
        assert "plugins.security.ssl.transport.pemcert_filepath" in content
        assert "plugins.security.ssl.transport.pemkey_filepath" in content
        assert "plugins.security.ssl.transport.pemtrustedcas_filepath" in content

    def test_has_tls_http_settings(self):
        """RT-014-17: Must configure TLS for HTTP layer."""
        content = OPENSEARCH_SECURE_YML.read_text(encoding="utf-8")
        assert "plugins.security.ssl.http.enabled: true" in content
        assert "plugins.security.ssl.http.pemcert_filepath" in content

    def test_has_admin_dn(self):
        """RT-014-18: Must configure admin DN for securityadmin.sh."""
        content = OPENSEARCH_SECURE_YML.read_text(encoding="utf-8")
        assert "plugins.security.authcz.admin_dn" in content

    def test_allows_security_index_init(self):
        """RT-014-19: Must allow default security index initialization."""
        content = OPENSEARCH_SECURE_YML.read_text(encoding="utf-8")
        assert "plugins.security.allow_default_init_securityindex: true" in content


# ============================================================================
# Tests: Fluent Bit Secure Configuration
# ============================================================================

class TestFluentBitSecureConfig:
    """Validate fluent-bit-secure.conf has TLS and auth."""

    def test_has_tls_enabled(self):
        """RT-014-20: Must enable TLS for OpenSearch output."""
        content = FLUENT_BIT_SECURE_CONF.read_text(encoding="utf-8")
        assert "tls             On" in content

    def test_has_authentication(self):
        """RT-014-21: Must have HTTP authentication for OpenSearch."""
        content = FLUENT_BIT_SECURE_CONF.read_text(encoding="utf-8")
        assert "HTTP_User" in content
        assert "HTTP_Passwd" in content

    def test_has_ca_cert(self):
        """RT-014-22: Must reference CA certificate file."""
        content = FLUENT_BIT_SECURE_CONF.read_text(encoding="utf-8")
        assert "tls.ca_file" in content
