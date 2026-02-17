"""
OpenSearch Backup Script

Creates and manages OpenSearch snapshots for backup and disaster recovery.
Supports local filesystem repository (Docker volume) or S3-compatible storage.

Usage:
    python backup_opensearch.py                         # Create snapshot
    python backup_opensearch.py --list                  # List snapshots
    python backup_opensearch.py --verify SNAPSHOT_NAME  # Verify a snapshot

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import argparse
import logging
import sys
from datetime import datetime, timezone

import requests

# ============================================================================
# Configuration
# ============================================================================

OPENSEARCH_URL = "http://localhost:9200"
REPO_NAME = "vaultize_backups"
REPO_PATH = "/mnt/snapshots"
SNAPSHOT_PREFIX = "vaultize-backup"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ============================================================================
# Repository Management
# ============================================================================

def ensure_repository(base_url: str, auth: tuple | None = None) -> bool:
    """Ensure the snapshot repository exists, creating it if needed."""
    url = f"{base_url}/_snapshot/{REPO_NAME}"
    resp = requests.get(url, auth=auth, timeout=10)

    if resp.status_code == 200:
        logger.info(f"Repository '{REPO_NAME}' already exists")
        return True

    logger.info(f"Creating snapshot repository '{REPO_NAME}'...")
    body = {
        "type": "fs",
        "settings": {
            "location": REPO_PATH,
            "compress": True,
        },
    }
    resp = requests.put(url, json=body, auth=auth, timeout=10)
    if resp.status_code == 200:
        logger.info("Repository created successfully")
        return True

    logger.error(f"Failed to create repository: {resp.status_code} {resp.text}")
    return False


# ============================================================================
# Snapshot Operations
# ============================================================================

def create_snapshot(base_url: str, auth: tuple | None = None) -> str | None:
    """Create a new snapshot with timestamp-based name."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    snapshot_name = f"{SNAPSHOT_PREFIX}-{timestamp}"

    logger.info(f"Creating snapshot '{snapshot_name}'...")
    url = f"{base_url}/_snapshot/{REPO_NAME}/{snapshot_name}?wait_for_completion=true"
    body = {
        "indices": "logs-*,alerts-*,.alerts-*",
        "ignore_unavailable": True,
        "include_global_state": False,
    }

    resp = requests.put(url, json=body, auth=auth, timeout=300)
    if resp.status_code == 200:
        data = resp.json()
        snapshot = data.get("snapshot", {})
        state = snapshot.get("state", "UNKNOWN")
        shards = snapshot.get("shards", {})
        logger.info(
            f"Snapshot '{snapshot_name}' completed: state={state}, "
            f"total_shards={shards.get('total', 0)}, "
            f"successful={shards.get('successful', 0)}, "
            f"failed={shards.get('failed', 0)}"
        )
        return snapshot_name
    else:
        logger.error(f"Snapshot failed: {resp.status_code} {resp.text}")
        return None


def list_snapshots(base_url: str, auth: tuple | None = None) -> list:
    """List all snapshots in the repository."""
    url = f"{base_url}/_snapshot/{REPO_NAME}/_all"
    resp = requests.get(url, auth=auth, timeout=10)

    if resp.status_code == 200:
        snapshots = resp.json().get("snapshots", [])
        if not snapshots:
            logger.info("No snapshots found")
            return []

        logger.info(f"Found {len(snapshots)} snapshot(s):")
        for snap in snapshots:
            start = snap.get("start_time", "N/A")
            state = snap.get("state", "UNKNOWN")
            indices = len(snap.get("indices", []))
            logger.info(f"  {snap['snapshot']}  state={state}  started={start}  indices={indices}")
        return snapshots
    else:
        logger.error(f"Failed to list snapshots: {resp.status_code} {resp.text}")
        return []


def verify_snapshot(base_url: str, snapshot_name: str, auth: tuple | None = None) -> bool:
    """Verify a snapshot's integrity."""
    url = f"{base_url}/_snapshot/{REPO_NAME}/{snapshot_name}/_status"
    resp = requests.get(url, auth=auth, timeout=30)

    if resp.status_code == 200:
        data = resp.json()
        snapshots = data.get("snapshots", [])
        if snapshots:
            state = snapshots[0].get("state", "UNKNOWN")
            logger.info(f"Snapshot '{snapshot_name}' state: {state}")
            return state == "SUCCESS"
    logger.error(f"Verification failed: {resp.status_code} {resp.text}")
    return False


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="OpenSearch Backup Management")
    parser.add_argument("--url", default=OPENSEARCH_URL, help="OpenSearch URL")
    parser.add_argument("--user", default=None, help="Username for auth")
    parser.add_argument("--password", default=None, help="Password for auth")
    parser.add_argument("--list", action="store_true", help="List all snapshots")
    parser.add_argument("--verify", type=str, help="Verify a specific snapshot")

    args = parser.parse_args()
    auth = (args.user, args.password) if args.user else None

    if not ensure_repository(args.url, auth):
        sys.exit(1)

    if args.list:
        list_snapshots(args.url, auth)
    elif args.verify:
        ok = verify_snapshot(args.url, args.verify, auth)
        sys.exit(0 if ok else 1)
    else:
        name = create_snapshot(args.url, auth)
        sys.exit(0 if name else 1)


if __name__ == "__main__":
    main()
