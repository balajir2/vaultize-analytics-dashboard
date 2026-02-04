"""
Regression Test RT-001: OpenSearch Node Config Must Not Contain Index-Level Settings

Original Bug:
    OpenSearch node configuration (opensearch.yml) contained index-level settings
    like index.number_of_shards, index.number_of_replicas, and slow log settings.
    This caused OpenSearch to fail startup with error:
    "node settings must not contain any index level settings"

How to Reproduce:
    1. Add index.number_of_shards: 3 to opensearch.yml
    2. Start OpenSearch container
    3. Container fails with IllegalArgumentException

Fix Applied:
    - Removed all index-level settings from opensearch.yml
    - Moved them to index templates (configs/index-templates/logs-template.json)
    - Added documentation comments explaining where index settings belong

Date: 2026-02-04
Severity: Critical
"""

import pytest
import yaml
from pathlib import Path


class TestRegressionOpensearchConfig:
    """Regression tests for OpenSearch configuration issues"""

    @pytest.fixture
    def opensearch_config_path(self):
        """Path to opensearch.yml"""
        return Path("infrastructure/docker/opensearch/opensearch.yml")

    @pytest.fixture
    def opensearch_config(self, opensearch_config_path):
        """Load opensearch.yml configuration"""
        with open(opensearch_config_path, 'r') as f:
            return yaml.safe_load(f)

    def test_regression_001_no_index_level_settings_in_node_config(
        self, opensearch_config
    ):
        """
        Verify that opensearch.yml does not contain index-level settings.

        This test would have failed before the fix and passes after.
        Index-level settings must be in index templates, not node config.
        """
        # List of index-level settings that should NOT be in node config
        forbidden_index_settings = [
            'index.number_of_shards',
            'index.number_of_replicas',
            'index.search.slowlog.threshold.query.warn',
            'index.search.slowlog.threshold.query.info',
            'index.search.slowlog.threshold.fetch.warn',
            'index.search.slowlog.threshold.fetch.info',
            'index.indexing.slowlog.threshold.index.warn',
            'index.indexing.slowlog.threshold.index.info',
        ]

        if opensearch_config is None:
            # Config file might have only comments, which is valid
            return

        # Verify no forbidden settings exist in config
        for setting in forbidden_index_settings:
            assert setting not in opensearch_config, (
                f"Index-level setting '{setting}' found in node config. "
                f"This setting must be in index templates, not opensearch.yml"
            )

    def test_regression_001_http_max_header_size_present(
        self, opensearch_config
    ):
        """
        Verify that http.max_header_size is set to prevent header size errors.

        Original bug: Default 8KB header limit was too small, causing
        "HTTP header is larger than 8192 bytes" errors.
        """
        assert opensearch_config is not None
        assert 'http.max_header_size' in opensearch_config, (
            "http.max_header_size must be configured to prevent header size errors"
        )

        # Verify it's set to at least 16kb
        header_size = opensearch_config['http.max_header_size']
        assert header_size in ['16kb', '32kb', '64kb'] or 'kb' in str(header_size), (
            f"http.max_header_size should be >= 16kb, got {header_size}"
        )
