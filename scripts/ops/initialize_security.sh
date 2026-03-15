#!/bin/bash
# ==========================================================================
# Initialize OpenSearch Security
#
# Runs securityadmin.sh inside the OpenSearch container to load security
# configuration (users, roles, role mappings) from the mounted config files.
#
# Prerequisites:
#   - Platform must be running in secure mode:
#       docker compose -f docker-compose.yml -f docker-compose.security.yml up -d
#   - Certificates must be generated: python scripts/ops/generate_certs.py
#   - Admin key must be in PKCS#8 format (generate_certs.py ensures this)
#
# NOTE: This script connects to OpenSearch via transport port (9300), not HTTP.
# It works even when OpenSearch returns "not initialized" on HTTP — that is
# expected before this script runs.
#
# Usage: ./scripts/ops/initialize_security.sh
#
# Authors: Balaji Rajan and Claude (Anthropic)
# License: Apache 2.0
# ==========================================================================

set -euo pipefail

CONTAINER="opensearch-node-1"
SECURITY_ADMIN="/usr/share/opensearch/plugins/opensearch-security/tools/securityadmin.sh"
CERTS_PATH="/usr/share/opensearch/config/certs"
SECURITY_CONFIG="/usr/share/opensearch/config/opensearch-security"
ADMIN_PASSWORD="${OPENSEARCH_ADMIN_PASSWORD:-vaultize}"

echo "=========================================="
echo "Vaultize Analytics - Security Initialization"
echo "=========================================="
echo

# Check container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    echo "[ERROR] Container '$CONTAINER' is not running."
    echo "  Start the secure stack first:"
    echo "    docker compose -f docker-compose.yml -f docker-compose.security.yml up -d"
    exit 1
fi

# Wait for OpenSearch transport port to be accepting connections (not HTTP)
# securityadmin connects via transport, which works before security is initialized.
echo "[INFO] Waiting for OpenSearch transport layer to be ready..."
MAX_RETRIES=30
for i in $(seq 1 $MAX_RETRIES); do
    if docker exec "$CONTAINER" bash -c "curl -sf --insecure https://localhost:9200 >/dev/null 2>&1 || true; ls /usr/share/opensearch/config/opensearch-security/*.yml >/dev/null 2>&1"; then
        echo "[OK] OpenSearch container is ready."
        break
    fi
    if [ "$i" -eq "$MAX_RETRIES" ]; then
        echo "[ERROR] Container not ready after $MAX_RETRIES attempts."
        exit 1
    fi
    echo "  Waiting... ($i/$MAX_RETRIES)"
    sleep 3
done

# Give the cluster time to elect a manager node
echo "[INFO] Waiting 10s for cluster formation..."
sleep 10

echo
echo "[INFO] Running securityadmin.sh..."
echo "  Loading config from: $SECURITY_CONFIG"
echo

docker exec "$CONTAINER" bash -c "
    chmod +x $SECURITY_ADMIN && \
    $SECURITY_ADMIN \
        -cd $SECURITY_CONFIG \
        -cacert $CERTS_PATH/ca.pem \
        -cert $CERTS_PATH/admin.pem \
        -key $CERTS_PATH/admin-key.pem \
        -icl -nhnv \
        -h localhost
"

echo
echo "[OK] Security initialization complete!"
echo

echo "[INFO] Verifying authenticated access..."
sleep 3
HEALTH=$(docker exec "$CONTAINER" curl -sf --insecure -u "admin:${ADMIN_PASSWORD}" https://localhost:9200/_cluster/health 2>/dev/null || true)
if [ -n "$HEALTH" ] && echo "$HEALTH" | python3 -c "import sys,json; d=json.load(sys.stdin); print('[OK] Cluster status:', d['status'])" 2>/dev/null; then
    :
else
    echo "[WARN] Could not verify. Check logs: docker compose logs opensearch-node-1"
fi
