#!/bin/bash
# ==========================================================================
# Start Vaultize Analytics Platform in Secure Mode
#
# Starts the platform with TLS/SSL and OpenSearch security enabled.
#
# Usage: ./scripts/ops/start_secure.sh [--services] [--metrics]
#
# Authors: Balaji Rajan and Claude (Anthropic)
# License: Apache 2.0
# ==========================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CERTS_DIR="$PROJECT_ROOT/infrastructure/certs"

echo "=========================================="
echo "Vaultize Analytics - Secure Startup"
echo "=========================================="
echo

# Step 1: Check/generate certificates
if [ ! -f "$CERTS_DIR/ca.pem" ] || [ ! -f "$CERTS_DIR/node.pem" ]; then
    echo "[INFO] Certificates not found. Generating..."
    bash "$SCRIPT_DIR/generate_certs.sh"
    echo
fi

# Step 2: Build profile arguments
PROFILES=""
for arg in "$@"; do
    case $arg in
        --services) PROFILES="$PROFILES --profile services" ;;
        --metrics) PROFILES="$PROFILES --profile metrics" ;;
    esac
done

# Step 3: Start with security overlay
echo "[INFO] Starting platform with security enabled..."
echo "  Command: docker compose -f docker-compose.yml -f docker-compose.security.yml $PROFILES up -d"
echo

cd "$PROJECT_ROOT"
docker compose -f docker-compose.yml -f docker-compose.security.yml $PROFILES up -d

echo
echo "[INFO] Waiting for cluster health..."
echo "  This may take 60-90 seconds..."

# Wait for OpenSearch to be ready
MAX_RETRIES=30
RETRY_INTERVAL=5
for i in $(seq 1 $MAX_RETRIES); do
    if curl -sf --insecure -u admin:admin https://localhost:9200/_cluster/health > /dev/null 2>&1; then
        echo "[OK] OpenSearch cluster is up and healthy!"
        curl -s --insecure -u admin:admin https://localhost:9200/_cluster/health?pretty
        break
    fi
    echo "  Attempt $i/$MAX_RETRIES - waiting ${RETRY_INTERVAL}s..."
    sleep $RETRY_INTERVAL
done

echo
echo "=========================================="
echo "Secure Platform Status"
echo "=========================================="
docker compose -f docker-compose.yml -f docker-compose.security.yml $PROFILES ps
echo
echo "Access URLs (HTTPS):"
echo "  OpenSearch:  https://localhost:9200 (admin/admin)"
echo "  Dashboards:  https://localhost:5601"
if echo "$PROFILES" | grep -q "services"; then
    echo "  API:         http://localhost:8000/docs"
    echo "  Alerting:    http://localhost:8001/docs"
fi
echo
echo "First-time setup: Run ./scripts/ops/initialize_security.sh"
