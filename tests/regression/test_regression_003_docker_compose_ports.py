"""
Regression Test RT-003: Docker Compose Port Configuration

Original Bug:
    Docker Compose had hardcoded ports instead of using environment variables.
    This made it impossible to change ports without editing docker-compose.yml,
    which is not best practice for configuration management.

    Example: Grafana port was hardcoded as "3000:3000" instead of "${GRAFANA_PORT:-3000}:3000"

How to Reproduce:
    1. Try to change Grafana port by setting GRAFANA_PORT=3100 in .env
    2. Run docker compose up -d
    3. Grafana still binds to port 3000 (hardcoded)

Fix Applied:
    Updated all port mappings in docker-compose.yml to use environment variables:
    - OpenSearch: ${OPENSEARCH_PORT:-9200}
    - Dashboards: ${OPENSEARCH_DASHBOARDS_PORT:-5601}
    - Prometheus: ${PROMETHEUS_PORT:-9090}
    - Grafana: ${GRAFANA_PORT:-3000}
    - Fluent Bit: ${FLUENT_BIT_FORWARD_PORT:-24224}
    - Analytics API: ${API_PORT:-8000}

Date: 2026-02-04
Severity: Medium
"""

import pytest
import yaml
from pathlib import Path
import re


class TestRegressionDockerComposePorts:
    """Regression tests for Docker Compose port configuration"""

    @pytest.fixture
    def docker_compose_path(self):
        """Path to docker-compose.yml"""
        return Path("docker-compose.yml")

    @pytest.fixture
    def docker_compose_content(self, docker_compose_path):
        """Load docker-compose.yml as text (YAML parsing doesn't preserve variables)"""
        with open(docker_compose_path, 'r') as f:
            return f.read()

    def test_regression_003_no_hardcoded_ports(self, docker_compose_content):
        """
        Verify that all port mappings use environment variables.

        Ports should be in format: "${VAR_NAME:-default}:container_port"
        not hardcoded as: "host_port:container_port"
        """
        # Find all port mapping lines (format: - "XXXX:XXXX")
        port_pattern = r'^\s*-\s+"(\d+):(\d+)"'

        hardcoded_ports = []
        for line_num, line in enumerate(docker_compose_content.split('\n'), 1):
            match = re.search(port_pattern, line)
            if match:
                # Check if line uses environment variable syntax
                if '${' not in line:
                    hardcoded_ports.append((line_num, line.strip()))

        assert len(hardcoded_ports) == 0, (
            f"Found {len(hardcoded_ports)} hardcoded port mappings. "
            f"Use environment variables instead:\n" +
            "\n".join(f"Line {num}: {line}" for num, line in hardcoded_ports)
        )

    def test_regression_003_port_variables_have_defaults(
        self, docker_compose_content
    ):
        """
        Verify that all port environment variables have default values.

        Format should be: ${VAR_NAME:-default} not just ${VAR_NAME}
        """
        # Find all environment variable usages in port mappings
        port_var_pattern = r'-\s+"(\$\{[^}]+\}):\d+"'

        vars_without_defaults = []
        for line_num, line in enumerate(docker_compose_content.split('\n'), 1):
            match = re.search(port_var_pattern, line)
            if match:
                var = match.group(1)
                # Check if variable has default value (contains :-)
                if ':-' not in var:
                    vars_without_defaults.append((line_num, var, line.strip()))

        assert len(vars_without_defaults) == 0, (
            f"Found {len(vars_without_defaults)} port variables without defaults:\n" +
            "\n".join(
                f"Line {num}: {var} in {line}"
                for num, var, line in vars_without_defaults
            )
        )

    def test_regression_003_common_ports_configurable(
        self, docker_compose_content
    ):
        """
        Verify that common service ports are configurable via environment variables.
        """
        # Services and their expected port variables
        expected_port_vars = {
            'OPENSEARCH_PORT': '9200',
            'OPENSEARCH_DASHBOARDS_PORT': '5601',
            'PROMETHEUS_PORT': '9090',
            'GRAFANA_PORT': '3000',  # Should be configurable
            'FLUENT_BIT_FORWARD_PORT': '24224',
        }

        for var_name, default_port in expected_port_vars.items():
            # Check if variable is used in docker-compose.yml
            var_usage = f'${{{var_name}:-{default_port}}}'
            assert var_usage in docker_compose_content or f'${{{var_name}:' in docker_compose_content, (
                f"Port variable {var_name} not found in docker-compose.yml. "
                f"Expected to see ${{{var_name}:-{default_port}}}"
            )
