#!/usr/bin/env python3
"""
Sample Log Generator

Generates realistic log data and indexes it into OpenSearch for testing
the Vaultize Analytics API.

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import json
import random
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any
import requests

# ============================================================================
# Configuration
# ============================================================================

OPENSEARCH_URL = "http://localhost:9200"
INDEX_PREFIX = "logs"

# Sample data pools
SERVICES = ["api-service", "web-service", "db-service", "cache-service", "auth-service"]
LOG_LEVELS = ["DEBUG", "INFO", "WARN", "ERROR", "FATAL"]
ERROR_MESSAGES = [
    "Connection timeout after 30s",
    "Database query failed",
    "Authentication token expired",
    "Rate limit exceeded",
    "Service unavailable",
    "Invalid request parameters",
    "Resource not found",
    "Permission denied",
    "Internal server error",
    "Network connection lost"
]
INFO_MESSAGES = [
    "Request processed successfully",
    "User logged in",
    "Cache hit for key",
    "Database connection established",
    "Health check passed",
    "Configuration reloaded",
    "Metrics published",
    "Session created",
    "File uploaded successfully",
    "Background job completed"
]
HOSTS = ["server-01", "server-02", "server-03", "server-04", "server-05"]
USERS = ["user1", "user2", "user3", "admin", "service-account"]
ENVIRONMENTS = ["development", "staging", "production"]

# ============================================================================
# Log Generation
# ============================================================================

def generate_log_entry(timestamp: datetime) -> Dict[str, Any]:
    """
    Generate a single log entry with realistic data.

    Args:
        timestamp: Log timestamp

    Returns:
        dict: Log entry
    """
    level = random.choice(LOG_LEVELS)
    service = random.choice(SERVICES)

    # Weight error messages towards ERROR/FATAL levels
    if level in ["ERROR", "FATAL"]:
        message = random.choice(ERROR_MESSAGES)
    else:
        message = random.choice(INFO_MESSAGES)

    log_entry = {
        "@timestamp": timestamp.isoformat() + "Z",
        "level": level,
        "service": service,
        "message": message,
        "host": random.choice(HOSTS),
        "environment": random.choice(ENVIRONMENTS),
        "request_id": f"req-{random.randint(100000, 999999)}",
        "user": random.choice(USERS) if random.random() > 0.3 else None,
        "duration_ms": random.randint(10, 5000) if random.random() > 0.5 else None,
        "status_code": random.choice([200, 201, 400, 401, 404, 500]) if random.random() > 0.4 else None,
    }

    # Add extra fields for errors
    if level in ["ERROR", "FATAL"]:
        log_entry["stack_trace"] = f"Error at {service}.handler.process()"
        log_entry["error_code"] = f"ERR_{random.randint(1000, 9999)}"

    return log_entry


def generate_logs(count: int, time_range_hours: int = 24) -> List[Dict[str, Any]]:
    """
    Generate multiple log entries spread across a time range.

    Args:
        count: Number of log entries to generate
        time_range_hours: Time range in hours to spread logs across

    Returns:
        list: List of log entries
    """
    logs = []
    now = datetime.utcnow()
    start_time = now - timedelta(hours=time_range_hours)

    for i in range(count):
        # Distribute logs across the time range
        random_offset = random.uniform(0, time_range_hours * 3600)
        timestamp = start_time + timedelta(seconds=random_offset)
        logs.append(generate_log_entry(timestamp))

    # Sort by timestamp
    logs.sort(key=lambda x: x["@timestamp"])

    return logs


# ============================================================================
# OpenSearch Indexing
# ============================================================================

def create_index_if_not_exists(index_name: str):
    """
    Create OpenSearch index if it doesn't exist.

    Args:
        index_name: Name of the index
    """
    # Check if index exists
    response = requests.head(f"{OPENSEARCH_URL}/{index_name}")

    if response.status_code == 404:
        # Create index with mapping
        mapping = {
            "mappings": {
                "properties": {
                    "@timestamp": {"type": "date"},
                    "level": {"type": "keyword"},
                    "service": {"type": "keyword"},
                    "message": {"type": "text"},
                    "host": {"type": "keyword"},
                    "environment": {"type": "keyword"},
                    "request_id": {"type": "keyword"},
                    "user": {"type": "keyword"},
                    "duration_ms": {"type": "integer"},
                    "status_code": {"type": "integer"},
                    "stack_trace": {"type": "text"},
                    "error_code": {"type": "keyword"}
                }
            }
        }

        response = requests.put(
            f"{OPENSEARCH_URL}/{index_name}",
            json=mapping,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code in [200, 201]:
            print(f"[OK] Created index: {index_name}")
        else:
            print(f"[ERROR] Failed to create index: {response.text}")
            sys.exit(1)
    else:
        print(f"[OK] Index already exists: {index_name}")


def index_logs(logs: List[Dict[str, Any]], index_name: str):
    """
    Index logs into OpenSearch using bulk API.

    Args:
        logs: List of log entries
        index_name: Index name
    """
    # Build bulk request body
    bulk_body = []
    for log in logs:
        # Action line
        bulk_body.append(json.dumps({"index": {"_index": index_name}}))
        # Document line
        bulk_body.append(json.dumps(log))

    bulk_data = "\n".join(bulk_body) + "\n"

    # Send bulk request
    response = requests.post(
        f"{OPENSEARCH_URL}/_bulk",
        data=bulk_data,
        headers={"Content-Type": "application/x-ndjson"}
    )

    if response.status_code == 200:
        result = response.json()
        if result.get("errors"):
            error_count = sum(1 for item in result["items"] if "error" in item.get("index", {}))
            print(f"[ERROR] Indexed with errors: {error_count} errors out of {len(logs)} documents")
        else:
            print(f"[OK] Successfully indexed {len(logs)} log entries")
    else:
        print(f"[ERROR] Bulk indexing failed: {response.text}")
        sys.exit(1)


# ============================================================================
# Main
# ============================================================================

def main():
    """Main entry point."""
    print("=" * 70)
    print("Vaultize Analytics - Sample Log Generator")
    print("=" * 70)
    print()

    # Configuration
    num_logs = 1000
    time_range_hours = 24

    # Today's index
    today = datetime.utcnow().strftime("%Y-%m-%d")
    index_name = f"{INDEX_PREFIX}-{today}"

    print(f"Configuration:")
    print(f"  OpenSearch URL: {OPENSEARCH_URL}")
    print(f"  Index Name: {index_name}")
    print(f"  Number of Logs: {num_logs}")
    print(f"  Time Range: Last {time_range_hours} hours")
    print()

    # Check OpenSearch connection
    try:
        response = requests.get(OPENSEARCH_URL)
        if response.status_code == 200:
            info = response.json()
            print(f"[OK] Connected to OpenSearch {info['version']['number']}")
        else:
            print(f"[ERROR] Failed to connect to OpenSearch: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Cannot connect to OpenSearch: {e}")
        print(f"  Make sure OpenSearch is running at {OPENSEARCH_URL}")
        sys.exit(1)

    print()

    # Create index
    create_index_if_not_exists(index_name)

    # Generate logs
    print(f"Generating {num_logs} log entries...")
    logs = generate_logs(num_logs, time_range_hours)

    # Index logs
    print(f"Indexing logs into {index_name}...")
    index_logs(logs, index_name)

    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"[OK] Generated and indexed {num_logs} sample log entries")
    print(f"[OK] Index: {index_name}")
    print(f"[OK] Time Range: {logs[0]['@timestamp']} to {logs[-1]['@timestamp']}")
    print()
    print("Distribution by log level:")
    for level in LOG_LEVELS:
        count = sum(1 for log in logs if log["level"] == level)
        percentage = (count / len(logs)) * 100
        print(f"  {level:8s}: {count:4d} ({percentage:5.1f}%)")

    print()
    print("Next steps:")
    print(f"  1. View logs in OpenSearch Dashboards: http://localhost:5601")
    print(f"  2. Search via API: curl http://localhost:8000/api/v1/search/simple?q=level:ERROR")
    print(f"  3. View API docs: http://localhost:8000/docs")
    print()


if __name__ == "__main__":
    main()
