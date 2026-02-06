"""
Regression Test RT-009: OpenSearch Cluster Formation Validation

Original Issue:
    Docker Compose must define exactly 3 OpenSearch nodes with consistent
    cluster configuration for proper HA cluster formation. Mismatched
    cluster names, missing seed hosts, or inconsistent initial manager
    nodes prevent the cluster from forming, causing split-brain or
    single-node operation.

Key Requirements:
    - Must have exactly 3 OpenSearch nodes
    - All nodes must share the same cluster.name
    - discovery.seed_hosts must list all 3 nodes
    - cluster.initial_cluster_manager_nodes must list all 3 nodes
    - All nodes must be on the same Docker network
    - All nodes must mount the shared opensearch.yml config

Date: 2026-02-06
Severity: Critical
"""

import pytest
import yaml
from pathlib import Path


class TestRegressionDockerComposeClusterFormation:
    """Regression tests for OpenSearch cluster formation in Docker Compose"""

    @pytest.fixture
    def compose_path(self):
        """Path to docker-compose.yml"""
        return Path("docker-compose.yml")

    @pytest.fixture
    def compose_content(self, compose_path):
        """Read raw docker-compose.yml content"""
        with open(compose_path, 'r', encoding='utf-8') as f:
            return f.read()

    @pytest.fixture
    def compose_data(self, compose_path):
        """Parse docker-compose.yml as YAML"""
        with open(compose_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    @pytest.fixture
    def opensearch_services(self, compose_data):
        """Extract OpenSearch node services from compose data"""
        services = compose_data.get("services", {})
        return {
            name: config for name, config in services.items()
            if name.startswith("opensearch-node-")
        }

    def test_regression_009_has_three_opensearch_nodes(self, opensearch_services):
        """
        Verify exactly 3 OpenSearch nodes are defined for HA.
        Fewer than 3 nodes cannot form a proper quorum for cluster manager election.
        """
        assert len(opensearch_services) == 3, (
            f"Expected 3 OpenSearch nodes for HA cluster, "
            f"found {len(opensearch_services)}: {list(opensearch_services.keys())}"
        )

    def test_regression_009_consistent_cluster_name(self, opensearch_services):
        """
        Verify all nodes use the same cluster.name.
        Mismatched cluster names cause nodes to form separate clusters.
        """
        cluster_names = set()
        for config in opensearch_services.values():
            env_list = config.get("environment", [])
            for env in env_list:
                if env.startswith("cluster.name="):
                    cluster_names.add(env.split("=", 1)[1])

        assert len(cluster_names) == 1, (
            f"All nodes must have the same cluster.name, "
            f"found: {cluster_names}"
        )
        assert "vaultize-cluster" in cluster_names, (
            f"Cluster name should be 'vaultize-cluster', got: {cluster_names}"
        )

    def test_regression_009_discovery_seed_hosts_lists_all_nodes(self, opensearch_services):
        """
        Verify discovery.seed_hosts includes all 3 nodes.
        Missing seed hosts prevent nodes from discovering each other.
        """
        node_names = set(opensearch_services.keys())

        for name, config in opensearch_services.items():
            env_list = config.get("environment", [])
            for env in env_list:
                if env.startswith("discovery.seed_hosts="):
                    seed_hosts = env.split("=", 1)[1]
                    for node in node_names:
                        assert node in seed_hosts, (
                            f"Node '{name}': discovery.seed_hosts is missing '{node}'. "
                            f"Current value: {seed_hosts}"
                        )

    def test_regression_009_initial_cluster_manager_nodes(self, opensearch_services):
        """
        Verify cluster.initial_cluster_manager_nodes lists all 3 nodes.
        Missing manager nodes prevents proper quorum-based election.
        """
        node_names = set(opensearch_services.keys())

        for name, config in opensearch_services.items():
            env_list = config.get("environment", [])
            for env in env_list:
                if env.startswith("cluster.initial_cluster_manager_nodes="):
                    manager_nodes = env.split("=", 1)[1]
                    for node in node_names:
                        assert node in manager_nodes, (
                            f"Node '{name}': cluster.initial_cluster_manager_nodes "
                            f"is missing '{node}'. Current value: {manager_nodes}"
                        )

    def test_regression_009_all_nodes_on_same_network(self, opensearch_services):
        """
        Verify all OpenSearch nodes are on the same Docker network.
        Nodes on different networks cannot communicate.
        """
        networks_per_node = {}
        for name, config in opensearch_services.items():
            networks = config.get("networks", [])
            networks_per_node[name] = set(networks)

        unique_networks = set(frozenset(n) for n in networks_per_node.values())
        assert len(unique_networks) == 1, (
            f"All OpenSearch nodes must be on the same network. "
            f"Networks: {networks_per_node}"
        )

    def test_regression_009_all_nodes_mount_shared_config(self, opensearch_services):
        """
        Verify all nodes mount the shared opensearch.yml configuration.
        Inconsistent configs between nodes cause unpredictable behavior.
        """
        for name, config in opensearch_services.items():
            volumes = config.get("volumes", [])
            config_mounted = any(
                "opensearch.yml" in str(v) for v in volumes
            )
            assert config_mounted, (
                f"Node '{name}' does not mount opensearch.yml. "
                f"All nodes must share the same configuration file."
            )

    def test_regression_009_memory_lock_enabled(self, opensearch_services):
        """
        Verify bootstrap.memory_lock is true on all nodes.
        Without memory lock, JVM heap can be swapped to disk causing severe
        performance degradation.
        """
        for name, config in opensearch_services.items():
            env_list = config.get("environment", [])
            memory_lock_set = any(
                env.startswith("bootstrap.memory_lock=true") for env in env_list
            )
            assert memory_lock_set, (
                f"Node '{name}' must have bootstrap.memory_lock=true "
                f"to prevent heap swapping"
            )

    def test_regression_009_healthchecks_defined(self, opensearch_services):
        """
        Verify all OpenSearch nodes have healthcheck definitions.
        Without healthchecks, dependent services may start before
        OpenSearch is ready, causing connection failures.
        """
        for name, config in opensearch_services.items():
            assert "healthcheck" in config, (
                f"Node '{name}' must have a healthcheck defined "
                f"for proper service dependency ordering"
            )

    def test_regression_009_consistent_opensearch_version(self, opensearch_services):
        """
        Verify all nodes use the same OpenSearch image version.
        Mixed versions in a cluster cause compatibility issues.
        """
        images = {
            config.get("image", "") for config in opensearch_services.values()
        }
        assert len(images) == 1, (
            f"All OpenSearch nodes must use the same image version. "
            f"Found: {images}"
        )
