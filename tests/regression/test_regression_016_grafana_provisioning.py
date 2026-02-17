"""
Regression Test RT-016: Grafana Provisioning and CORS Hardening

Validates that Grafana auto-provisioning is configured and that
the API enforces restrictive CORS in non-development environments.

Severity: High
Category: Configuration - Visualization & Security
Authors: Balaji Rajan and Claude (Anthropic)
"""

import json
from pathlib import Path

import pytest
import yaml

# ============================================================================
# Constants
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
GRAFANA_DIR = PROJECT_ROOT / "dashboards" / "grafana"
PROVISIONING_DIR = GRAFANA_DIR / "provisioning"
DASHBOARDS_DIR = GRAFANA_DIR / "dashboards"
API_MAIN = PROJECT_ROOT / "analytics" / "api" / "app" / "main.py"
API_CONFIG = PROJECT_ROOT / "analytics" / "api" / "app" / "config.py"
SECRETS_DOC = PROJECT_ROOT / "docs" / "operations" / "secrets-management.md"


# ============================================================================
# Tests: Grafana Directory Structure
# ============================================================================

class TestGrafanaDirectoryStructure:
    """Validate Grafana provisioning directory layout."""

    def test_grafana_dir_exists(self):
        """RT-016-01: Grafana root directory must exist."""
        assert GRAFANA_DIR.exists()

    def test_provisioning_dir_exists(self):
        """RT-016-02: Provisioning directory must exist."""
        assert PROVISIONING_DIR.exists()

    def test_datasources_dir_exists(self):
        """RT-016-03: Datasources provisioning directory must exist."""
        assert (PROVISIONING_DIR / "datasources").exists()

    def test_dashboards_provisioning_dir_exists(self):
        """RT-016-04: Dashboards provisioning directory must exist."""
        assert (PROVISIONING_DIR / "dashboards").exists()

    def test_dashboards_dir_exists(self):
        """RT-016-05: Dashboards JSON directory must exist."""
        assert DASHBOARDS_DIR.exists()


# ============================================================================
# Tests: Datasource Provisioning
# ============================================================================

class TestDatasourceProvisioning:
    """Validate Grafana datasource auto-provisioning."""

    @pytest.fixture
    def datasources_config(self):
        path = PROVISIONING_DIR / "datasources" / "datasources.yml"
        assert path.exists(), "datasources.yml does not exist"
        return yaml.safe_load(path.read_text(encoding="utf-8"))

    def test_has_api_version(self, datasources_config):
        """RT-016-06: Datasources config must have apiVersion."""
        assert datasources_config.get("apiVersion") == 1

    def test_has_datasources_list(self, datasources_config):
        """RT-016-07: Config must contain datasources list."""
        assert "datasources" in datasources_config
        assert len(datasources_config["datasources"]) >= 1

    def test_opensearch_datasource_present(self, datasources_config):
        """RT-016-08: OpenSearch datasource must be configured."""
        names = [ds["name"] for ds in datasources_config["datasources"]]
        assert "OpenSearch" in names

    def test_opensearch_is_default(self, datasources_config):
        """RT-016-09: OpenSearch must be the default datasource."""
        for ds in datasources_config["datasources"]:
            if ds["name"] == "OpenSearch":
                assert ds.get("isDefault") is True
                return
        pytest.fail("OpenSearch datasource not found")

    def test_opensearch_points_to_cluster(self, datasources_config):
        """RT-016-10: OpenSearch URL must point to the cluster."""
        for ds in datasources_config["datasources"]:
            if ds["name"] == "OpenSearch":
                assert "opensearch" in ds["url"]
                assert "9200" in ds["url"]
                return

    def test_prometheus_datasource_present(self, datasources_config):
        """RT-016-11: Prometheus datasource must be configured."""
        names = [ds["name"] for ds in datasources_config["datasources"]]
        assert "Prometheus" in names

    def test_prometheus_points_to_service(self, datasources_config):
        """RT-016-12: Prometheus URL must point to the service."""
        for ds in datasources_config["datasources"]:
            if ds["name"] == "Prometheus":
                assert "prometheus" in ds["url"]
                assert "9090" in ds["url"]
                return


# ============================================================================
# Tests: Dashboard Provisioning Config
# ============================================================================

class TestDashboardProvisioning:
    """Validate Grafana dashboard provider config."""

    @pytest.fixture
    def dashboards_config(self):
        path = PROVISIONING_DIR / "dashboards" / "dashboards.yml"
        assert path.exists(), "dashboards.yml does not exist"
        return yaml.safe_load(path.read_text(encoding="utf-8"))

    def test_has_api_version(self, dashboards_config):
        """RT-016-13: Dashboard config must have apiVersion."""
        assert dashboards_config.get("apiVersion") == 1

    def test_has_providers(self, dashboards_config):
        """RT-016-14: Config must have providers list."""
        assert "providers" in dashboards_config
        assert len(dashboards_config["providers"]) >= 1

    def test_provider_uses_file_type(self, dashboards_config):
        """RT-016-15: Provider must use file type."""
        provider = dashboards_config["providers"][0]
        assert provider["type"] == "file"

    def test_provider_path_is_correct(self, dashboards_config):
        """RT-016-16: Provider path must match Docker mount."""
        provider = dashboards_config["providers"][0]
        assert provider["options"]["path"] == "/var/lib/grafana/dashboards"


# ============================================================================
# Tests: Platform Health Dashboard
# ============================================================================

class TestPlatformHealthDashboard:
    """Validate the platform health Grafana dashboard JSON."""

    @pytest.fixture
    def dashboard(self):
        path = DASHBOARDS_DIR / "platform-health.json"
        assert path.exists(), "platform-health.json does not exist"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_is_valid_json(self, dashboard):
        """RT-016-17: Dashboard must be valid JSON."""
        assert isinstance(dashboard, dict)

    def test_has_title(self, dashboard):
        """RT-016-18: Dashboard must have a title."""
        assert "title" in dashboard
        assert len(dashboard["title"]) > 0

    def test_has_panels(self, dashboard):
        """RT-016-19: Dashboard must have panels."""
        assert "panels" in dashboard
        assert len(dashboard["panels"]) > 0

    def test_has_uid(self, dashboard):
        """RT-016-20: Dashboard must have a UID."""
        assert "uid" in dashboard
        assert len(dashboard["uid"]) > 0

    def test_has_schema_version(self, dashboard):
        """RT-016-21: Dashboard must have schemaVersion."""
        assert "schemaVersion" in dashboard

    def test_has_vaultize_tag(self, dashboard):
        """RT-016-22: Dashboard must have vaultize tag."""
        assert "vaultize" in dashboard.get("tags", [])


# ============================================================================
# Tests: CORS Hardening
# ============================================================================

class TestCORSHardening:
    """Validate CORS configuration handles environments."""

    def test_main_has_environment_cors_check(self):
        """RT-016-23: API main.py must check environment for CORS."""
        content = API_MAIN.read_text(encoding="utf-8")
        assert "production" in content and "staging" in content, \
            "main.py must have production/staging CORS check"

    def test_config_has_cors_origins(self):
        """RT-016-24: API config must have cors_origins setting."""
        content = API_CONFIG.read_text(encoding="utf-8")
        assert "cors_origins" in content

    def test_production_cors_restricts_methods(self):
        """RT-016-25: Production CORS must restrict HTTP methods."""
        content = API_MAIN.read_text(encoding="utf-8")
        assert "GET" in content and "POST" in content
        assert "OPTIONS" in content

    def test_production_cors_restricts_headers(self):
        """RT-016-26: Production CORS must restrict headers."""
        content = API_MAIN.read_text(encoding="utf-8")
        assert "Authorization" in content
        assert "Content-Type" in content


# ============================================================================
# Tests: Secrets Documentation
# ============================================================================

class TestSecretsDocumentation:
    """Validate secrets management documentation."""

    def test_secrets_doc_exists(self):
        """RT-016-27: Secrets management doc must exist."""
        assert SECRETS_DOC.exists()

    def test_covers_jwt_secret(self):
        """RT-016-28: Doc must cover JWT secret key."""
        content = SECRETS_DOC.read_text(encoding="utf-8")
        assert "API_SECRET_KEY" in content

    def test_covers_opensearch_password(self):
        """RT-016-29: Doc must cover OpenSearch password."""
        content = SECRETS_DOC.read_text(encoding="utf-8")
        assert "OPENSEARCH_ADMIN_PASSWORD" in content

    def test_covers_rotation(self):
        """RT-016-30: Doc must cover secret rotation."""
        content = SECRETS_DOC.read_text(encoding="utf-8")
        assert "rotation" in content.lower() or "Rotation" in content
