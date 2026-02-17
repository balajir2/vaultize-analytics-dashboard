"""
Platform Health Check Script

Validates the health of all Vaultize Analytics Platform services.
Exits with code 0 if all checks pass, 1 if any fail.

Usage:
    python health_check.py             # Check all services
    python health_check.py --verbose   # Detailed output

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

SERVICES = {
    "opensearch": {
        "url": "http://localhost:9200/_cluster/health",
        "check": lambda r: r.json().get("status") in ("green", "yellow"),
        "detail": lambda r: f"status={r.json().get('status')}, nodes={r.json().get('number_of_nodes')}",
    },
    "opensearch-dashboards": {
        "url": "http://localhost:5601/api/status",
        "check": lambda r: r.status_code == 200,
        "detail": lambda r: f"status_code={r.status_code}",
    },
    "analytics-api": {
        "url": "http://localhost:8000/health/liveness",
        "check": lambda r: r.json().get("status") == "healthy",
        "detail": lambda r: f"status={r.json().get('status')}",
    },
    "alerting-service": {
        "url": "http://localhost:8001/health/liveness",
        "check": lambda r: r.json().get("status") == "healthy",
        "detail": lambda r: f"status={r.json().get('status')}",
    },
    "fluent-bit": {
        "url": "http://localhost:2020/api/v1/health",
        "check": lambda r: r.status_code == 200,
        "detail": lambda r: f"status_code={r.status_code}",
    },
}

OPTIONAL_SERVICES = {
    "prometheus": {
        "url": "http://localhost:9090/-/healthy",
        "check": lambda r: r.status_code == 200,
        "detail": lambda r: f"status_code={r.status_code}",
    },
    "grafana": {
        "url": "http://localhost:3000/api/health",
        "check": lambda r: r.status_code == 200,
        "detail": lambda r: f"status_code={r.status_code}",
    },
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ============================================================================
# Health Checks
# ============================================================================

def check_service(name: str, config: dict, verbose: bool = False) -> bool:
    """Check a single service's health."""
    try:
        resp = requests.get(config["url"], timeout=10)
        healthy = config["check"](resp)
        detail = config["detail"](resp) if verbose else ""
        status = "OK" if healthy else "FAIL"
        msg = f"  [{status}] {name}"
        if detail:
            msg += f" ({detail})"
        logger.info(msg)
        return healthy
    except requests.exceptions.ConnectionError:
        logger.info(f"  [FAIL] {name} (connection refused)")
        return False
    except Exception as e:
        logger.info(f"  [FAIL] {name} ({e})")
        return False


def run_health_checks(verbose: bool = False) -> bool:
    """Run all health checks. Returns True if all required services pass."""
    all_ok = True

    logger.info("=== Required Services ===")
    for name, config in SERVICES.items():
        if not check_service(name, config, verbose):
            all_ok = False

    logger.info("")
    logger.info("=== Optional Services ===")
    for name, config in OPTIONAL_SERVICES.items():
        check_service(name, config, verbose)
        # Optional services don't affect the exit code

    return all_ok


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Vaultize Platform Health Check")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    args = parser.parse_args()

    logger.info("Vaultize Analytics Platform - Health Check")
    logger.info("=" * 50)

    ok = run_health_checks(verbose=args.verbose)

    logger.info("")
    if ok:
        logger.info("Result: ALL REQUIRED SERVICES HEALTHY")
    else:
        logger.info("Result: SOME SERVICES UNHEALTHY")

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
