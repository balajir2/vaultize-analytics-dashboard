"""
Regression Test RT-002: OpenSearch Dashboards Config Validation

Original Bug:
    OpenSearch Dashboards configuration had multiple invalid settings:
    1. server.basePath set to empty string "" instead of being omitted
    2. server.cors.enabled instead of server.cors (boolean expected)
    3. Unsupported config keys: opensearch_security.*, telemetry.*

    These caused container restart loops with validation errors.

How to Reproduce:
    1. Set server.basePath: "" in opensearch_dashboards.yml
    2. Set server.cors.enabled: false
    3. Add opensearch_security.auth.type: ""
    4. Start Dashboards container
    5. Container fails with config validation errors

Fix Applied:
    - Commented out server.basePath (use default)
    - Changed server.cors.enabled to server.cors: false
    - Removed all opensearch_security.* and telemetry.* keys

Date: 2026-02-04
Severity: Critical
"""

import pytest
import yaml
from pathlib import Path


class TestRegressionDashboardsConfig:
    """Regression tests for OpenSearch Dashboards configuration"""

    @pytest.fixture
    def dashboards_config_path(self):
        """Path to opensearch_dashboards.yml"""
        return Path("infrastructure/docker/opensearch-dashboards/opensearch_dashboards.yml")

    @pytest.fixture
    def dashboards_config(self, dashboards_config_path):
        """Load opensearch_dashboards.yml configuration"""
        with open(dashboards_config_path, 'r') as f:
            return yaml.safe_load(f)

    @pytest.fixture
    def dashboards_config_raw(self, dashboards_config_path):
        """Load raw config file to check for commented lines"""
        with open(dashboards_config_path, 'r') as f:
            return f.read()

    def test_regression_002_base_path_not_set_to_empty_string(
        self, dashboards_config, dashboards_config_raw
    ):
        """
        Verify server.basePath is not set to empty string.

        Empty string causes validation error:
        "must start with a slash, don't end with one"
        """
        if dashboards_config and 'server.basePath' in dashboards_config:
            base_path = dashboards_config['server.basePath']
            assert base_path != "", (
                "server.basePath cannot be empty string. "
                "Either omit it or set to valid path like '/dashboards'"
            )
            if base_path:  # If set, must start with /
                assert base_path.startswith('/'), (
                    f"server.basePath must start with /, got {base_path}"
                )

        # Verify it's either commented out or not present
        assert 'server.basePath: ""' not in dashboards_config_raw, (
            "server.basePath should not be set to empty string"
        )

    def test_regression_002_cors_is_boolean_not_object(
        self, dashboards_config
    ):
        """
        Verify server.cors is a boolean, not an object.

        Original error: "expected value of type [boolean] but got [Object]"
        This happened when using server.cors.enabled instead of server.cors.
        """
        if dashboards_config and 'server.cors' in dashboards_config:
            cors_value = dashboards_config['server.cors']
            assert isinstance(cors_value, bool), (
                f"server.cors must be boolean (true/false), got {type(cors_value)}"
            )

        # Ensure server.cors.enabled is not used
        if dashboards_config:
            assert 'server.cors.enabled' not in dashboards_config, (
                "Use 'server.cors: false' not 'server.cors.enabled: false'"
            )

    def test_regression_002_no_unsupported_security_keys(
        self, dashboards_config
    ):
        """
        Verify no unsupported opensearch_security.* keys are present.

        These keys cause: "Unknown configuration key(s)" errors.
        """
        if not dashboards_config:
            return

        unsupported_keys = [
            'opensearch_security.auth.type',
            'opensearch_security.multitenancy.enabled',
            'opensearch_security.readonly_mode.roles',
        ]

        for key in unsupported_keys:
            assert key not in dashboards_config, (
                f"Unsupported config key '{key}' found. "
                f"Remove it from opensearch_dashboards.yml"
            )

    def test_regression_002_no_unsupported_telemetry_keys(
        self, dashboards_config
    ):
        """
        Verify no unsupported telemetry.* keys are present.

        These keys cause: "Unknown configuration key(s)" errors in version 2.11.1.
        """
        if not dashboards_config:
            return

        unsupported_keys = [
            'telemetry.enabled',
            'telemetry.optIn',
        ]

        for key in unsupported_keys:
            assert key not in dashboards_config, (
                f"Unsupported config key '{key}' found. "
                f"Remove it from opensearch_dashboards.yml (not supported in 2.11.1)"
            )
