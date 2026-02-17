"""
OpenSearch Restore Script

Restores indices from a snapshot to the OpenSearch cluster.
Supports full restore, specific indices, and rename-on-restore.

Usage:
    python restore_opensearch.py SNAPSHOT_NAME                     # Full restore
    python restore_opensearch.py SNAPSHOT_NAME --indices "logs-*"  # Specific indices
    python restore_opensearch.py SNAPSHOT_NAME --rename             # Restore with rename prefix

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import argparse
import logging
import sys

import requests

# ============================================================================
# Configuration
# ============================================================================

OPENSEARCH_URL = "http://localhost:9200"
REPO_NAME = "vaultize_backups"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ============================================================================
# Restore Operations
# ============================================================================

def restore_snapshot(
    base_url: str,
    snapshot_name: str,
    indices: str | None = None,
    rename: bool = False,
    auth: tuple | None = None,
) -> bool:
    """
    Restore a snapshot to the cluster.

    Args:
        base_url: OpenSearch URL
        snapshot_name: Name of the snapshot to restore
        indices: Comma-separated index pattern to restore (default: all)
        rename: If True, restore with "restored_" prefix to avoid conflicts
        auth: Optional (username, password) tuple
    """
    url = f"{base_url}/_snapshot/{REPO_NAME}/{snapshot_name}/_restore?wait_for_completion=true"

    body = {
        "ignore_unavailable": True,
        "include_global_state": False,
    }

    if indices:
        body["indices"] = indices

    if rename:
        body["rename_pattern"] = "(.+)"
        body["rename_replacement"] = "restored_$1"

    logger.info(f"Restoring snapshot '{snapshot_name}'...")
    if indices:
        logger.info(f"  Indices filter: {indices}")
    if rename:
        logger.info("  Restoring with 'restored_' prefix")

    resp = requests.post(url, json=body, auth=auth, timeout=300)

    if resp.status_code == 200:
        data = resp.json()
        snapshot = data.get("snapshot", {})
        shards = snapshot.get("shards", {})
        logger.info(
            f"Restore completed: "
            f"total_shards={shards.get('total', 0)}, "
            f"successful={shards.get('successful', 0)}, "
            f"failed={shards.get('failed', 0)}"
        )
        return shards.get("failed", 0) == 0
    else:
        logger.error(f"Restore failed: {resp.status_code} {resp.text}")
        return False


def close_indices(base_url: str, pattern: str, auth: tuple | None = None) -> bool:
    """Close indices before restore (required for existing indices)."""
    url = f"{base_url}/{pattern}/_close"
    logger.info(f"Closing indices matching '{pattern}'...")
    resp = requests.post(url, auth=auth, timeout=30)

    if resp.status_code in (200, 404):
        return True
    logger.error(f"Failed to close indices: {resp.status_code} {resp.text}")
    return False


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="OpenSearch Restore from Snapshot")
    parser.add_argument("snapshot", help="Snapshot name to restore")
    parser.add_argument("--url", default=OPENSEARCH_URL, help="OpenSearch URL")
    parser.add_argument("--user", default=None, help="Username for auth")
    parser.add_argument("--password", default=None, help="Password for auth")
    parser.add_argument("--indices", default=None, help="Indices to restore (e.g. 'logs-*')")
    parser.add_argument("--rename", action="store_true", help="Restore with 'restored_' prefix")
    parser.add_argument("--close-first", action="store_true",
                        help="Close existing indices before restore")

    args = parser.parse_args()
    auth = (args.user, args.password) if args.user else None

    if args.close_first and args.indices:
        if not close_indices(args.url, args.indices, auth):
            logger.error("Failed to close indices, aborting restore")
            sys.exit(1)

    ok = restore_snapshot(
        args.url, args.snapshot,
        indices=args.indices, rename=args.rename, auth=auth,
    )
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
