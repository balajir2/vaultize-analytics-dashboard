"""
Regression Test RT-019: Prometheus Metrics Integration

Validates that Prometheus metrics are properly configured across
the platform: Fluent Bit port exposure, FastAPI instrumentator
integration, Prometheus scrape targets, rate limiter exclusion,
and Grafana dashboard panels.

Date: 2026-02-21
Severity: Medium
Category: Configuration - Metrics & Monitoring
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
DOCKER_COMPOSE = PROJECT_ROOT / "docker-compose.yml"
PROMETHEUS_CONFIG = PROJECT_ROOT / "ingestion" / "configs" / "prometheus" / "prometheus.yml"
FLUENT_BIT_CONFIG = PROJECT_ROOT / "ingestion" / "configs" / "fluent-bit" / "fluent-bit.conf"
API_REQUIREMENTS = PROJECT_ROOT / "analytics" / "api" / "requirements.txt"
API_MAIN = PROJECT_ROOT / "analytics" / "api" / "app" / "main.py"
API_RATE_LIMIT = PROJECT_ROOT / "analytics" / "api" / "app" / "middleware" / "rate_limit.py"
ALERTING_REQUIREMENTS = PROJECT_ROOT / "analytics" / "alerting" / "requirements.txt"
ALERTING_MAIN = PROJECT_ROOT / "analytics" / "alerting" / "app" / "main.py"
GRAFANA_DASHBOARD = PROJECT_ROOT / "dashboards" / "grafana" / "dashboards" / "platform-health.json"


# ============================================================================
# Tests: Fluent Bit Metrics Port
# ============================================================================

class TestFluentBitMetricsPort:
    """Validate Fluent Bit metrics port is exposed."""

    def test_regression_019_01_fluent_bit_exposes_port_2020(self):
        """RT-019-01: docker-compose.yml must expose Fluent Bit port 2020."""
        content = DOCKER_COMPOSE.read_text()
        assert "2020}:2020" in content

    def test_regression_019_02_fluent_bit_http_server_enabled(self):
        """RT-019-02: Fluent Bit config must have HTTP server enabled on port 2020."""
        content = FLUENT_BIT_CONFIG.read_text()
        assert "HTTP_Server" in content
        assert "2020" in content

    def test_regression_019_03_fluent_bit_metrics_port_configurable(self):
        """RT-019-03: Fluent Bit metrics port must use env var pattern."""
        content = DOCKER_COMPOSE.read_text()
        assert "FLUENT_BIT_METRICS_PORT" in content


# ============================================================================
# Tests: Analytics API Metrics
# ============================================================================

class TestAnalyticsAPIMetrics:
    """Validate Analytics API Prometheus instrumentation."""

    def test_regression_019_04_api_has_instrumentator_dependency(self):
        """RT-019-04: Analytics API requirements must include prometheus-fastapi-instrumentator."""
        content = API_REQUIREMENTS.read_text()
        assert "prometheus-fastapi-instrumentator" in content

    def test_regression_019_05_api_main_imports_instrumentator(self):
        """RT-019-05: Analytics API main.py must use Instrumentator."""
        content = API_MAIN.read_text()
        assert "Instrumentator" in content
        assert "prometheus_fastapi_instrumentator" in content

    def test_regression_019_06_api_metrics_excluded_from_schema(self):
        """RT-019-06: API metrics endpoint must be excluded from OpenAPI schema."""
        content = API_MAIN.read_text()
        assert "include_in_schema=False" in content


# ============================================================================
# Tests: Alerting Service Metrics
# ============================================================================

class TestAlertingServiceMetrics:
    """Validate Alerting Service Prometheus instrumentation."""

    def test_regression_019_07_alerting_has_instrumentator_dependency(self):
        """RT-019-07: Alerting requirements must include prometheus-fastapi-instrumentator."""
        content = ALERTING_REQUIREMENTS.read_text()
        assert "prometheus-fastapi-instrumentator" in content

    def test_regression_019_08_alerting_main_imports_instrumentator(self):
        """RT-019-08: Alerting main.py must use Instrumentator."""
        content = ALERTING_MAIN.read_text()
        assert "Instrumentator" in content
        assert "prometheus_fastapi_instrumentator" in content


# ============================================================================
# Tests: Prometheus Scrape Configuration
# ============================================================================

class TestPrometheusConfig:
    """Validate Prometheus scrape targets are correctly configured."""

    @pytest.fixture(autouse=True)
    def load_config(self):
        """Load Prometheus config once per test class."""
        self.config_text = PROMETHEUS_CONFIG.read_text()
        self.config = yaml.safe_load(self.config_text)

    def test_regression_019_09_prometheus_scrapes_fluent_bit(self):
        """RT-019-09: Prometheus must have fluent-bit scrape target."""
        jobs = {j["job_name"] for j in self.config["scrape_configs"]}
        assert "fluent-bit" in jobs
        fb_job = next(j for j in self.config["scrape_configs"] if j["job_name"] == "fluent-bit")
        assert fb_job["metrics_path"] == "/api/v1/metrics/prometheus"

    def test_regression_019_10_prometheus_scrapes_analytics_api(self):
        """RT-019-10: Prometheus must have analytics-api scrape target."""
        jobs = {j["job_name"] for j in self.config["scrape_configs"]}
        assert "analytics-api" in jobs
        api_job = next(j for j in self.config["scrape_configs"] if j["job_name"] == "analytics-api")
        assert api_job["metrics_path"] == "/metrics"

    def test_regression_019_11_prometheus_scrapes_alerting_service(self):
        """RT-019-11: Prometheus must have alerting-service scrape target."""
        jobs = {j["job_name"] for j in self.config["scrape_configs"]}
        assert "alerting-service" in jobs
        alert_job = next(j for j in self.config["scrape_configs"] if j["job_name"] == "alerting-service")
        assert alert_job["metrics_path"] == "/metrics"

    def test_regression_019_12_prometheus_scrapes_opensearch_exporter(self):
        """RT-019-12: Prometheus must scrape OpenSearch via opensearch-exporter."""
        jobs = {j["job_name"] for j in self.config["scrape_configs"]}
        assert "opensearch" in jobs
        os_job = next(j for j in self.config["scrape_configs"] if j["job_name"] == "opensearch")
        targets = os_job["static_configs"][0]["targets"]
        assert "opensearch-exporter:9114" in targets


# ============================================================================
# Tests: Rate Limiter Metrics Exclusion
# ============================================================================

class TestRateLimiterMetricsExclusion:
    """Validate rate limiter skips /metrics endpoint."""

    def test_regression_019_13_rate_limiter_skips_metrics(self):
        """RT-019-13: Rate limit middleware must exclude /metrics path."""
        content = API_RATE_LIMIT.read_text()
        assert "/metrics" in content


# ============================================================================
# Tests: Grafana Dashboard Metrics Panels
# ============================================================================

class TestGrafanaDashboardMetrics:
    """Validate Grafana dashboard includes service metrics panels."""

    @pytest.fixture(autouse=True)
    def load_dashboard(self):
        """Load Grafana dashboard JSON."""
        self.dashboard = json.loads(GRAFANA_DASHBOARD.read_text())
        self.panels = self.dashboard["panels"]

    def _find_panel_with_expr(self, expr_substring):
        """Find a panel whose target expr contains the given substring."""
        for panel in self.panels:
            for target in panel.get("targets", []):
                if expr_substring in target.get("expr", ""):
                    return panel
        return None

    def test_regression_019_14_dashboard_has_api_request_rate(self):
        """RT-019-14: Dashboard must have Analytics API request rate panel."""
        panel = self._find_panel_with_expr('http_requests_total{job="analytics-api"}')
        assert panel is not None, "Missing Analytics API request rate panel"

    def test_regression_019_15_dashboard_has_alerting_request_rate(self):
        """RT-019-15: Dashboard must have Alerting Service request rate panel."""
        panel = self._find_panel_with_expr('http_requests_total{job="alerting-service"}')
        assert panel is not None, "Missing Alerting Service request rate panel"

    def test_regression_019_16_dashboard_has_api_latency(self):
        """RT-019-16: Dashboard must have Analytics API P95 latency panel."""
        panel = self._find_panel_with_expr('http_request_duration_seconds_bucket{job="analytics-api"}')
        assert panel is not None, "Missing Analytics API latency panel"

    def test_regression_019_17_dashboard_has_alerting_latency(self):
        """RT-019-17: Dashboard must have Alerting Service P95 latency panel."""
        panel = self._find_panel_with_expr('http_request_duration_seconds_bucket{job="alerting-service"}')
        assert panel is not None, "Missing Alerting Service latency panel"

    def test_regression_019_18_dashboard_has_service_metrics_row(self):
        """RT-019-18: Dashboard must have a 'Service Metrics' row."""
        row_titles = [p.get("title") for p in self.panels if p.get("type") == "row"]
        assert "Service Metrics" in row_titles

    def test_regression_019_19_dashboard_has_opensearch_cluster_panel(self):
        """RT-019-19: Dashboard must have OpenSearch cluster health panel via exporter."""
        panel = self._find_panel_with_expr('up{job="opensearch"}')
        assert panel is not None, "Missing OpenSearch cluster health panel"

    def test_regression_019_20_dashboard_has_opensearch_node_count(self):
        """RT-019-20: Dashboard must have OpenSearch node count panel."""
        panel = self._find_panel_with_expr('elasticsearch_cluster_health_number_of_nodes')
        assert panel is not None, "Missing OpenSearch node count panel"


# ============================================================================
# Tests: OpenSearch Exporter in Docker Compose
# ============================================================================

class TestOpenSearchExporter:
    """Validate opensearch-exporter sidecar is configured."""

    def test_regression_019_21_exporter_in_docker_compose(self):
        """RT-019-21: docker-compose.yml must define opensearch-exporter service."""
        content = DOCKER_COMPOSE.read_text()
        assert "opensearch-exporter:" in content

    def test_regression_019_22_exporter_uses_correct_image(self):
        """RT-019-22: Exporter must use prometheuscommunity/elasticsearch-exporter."""
        content = DOCKER_COMPOSE.read_text()
        assert "prometheuscommunity/elasticsearch-exporter" in content

    def test_regression_019_23_exporter_port_configurable(self):
        """RT-019-23: Exporter port must use env var pattern."""
        content = DOCKER_COMPOSE.read_text()
        assert "OPENSEARCH_EXPORTER_PORT" in content
