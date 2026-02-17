#!/bin/bash
# ==========================================================================
# Initialize OpenSearch Security
#
# Runs securityadmin.sh inside the OpenSearch container to load security
# configuration (users, roles, role mappings) from the mounted config files.
#
# Prerequisites:
#   - Platform must be running in secure mode (start_secure.sh)
#   - Certificates must be generated (generate_certs.sh)
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

echo "=========================================="
echo "Vaultize Analytics - Security Initialization"
echo "=========================================="
echo

# Check container is running
if ! docker ps --format '{{.Names}}' | grep -q "$CONTAINER"; then
    echo "[ERROR] Container '$CONTAINER' is not running."
    echo "  Start the secure stack first: ./scripts/ops/start_secure.sh"
    exit 1
fi

# Wait for OpenSearch to be ready
echo "[INFO] Waiting for OpenSearch to be ready..."
MAX_RETRIES=20
for i in $(seq 1 $MAX_RETRIES); do
    if docker exec "$CONTAINER" curl -sf --insecure https://localhost:9200 > /dev/null 2>&1; then
        echo "[OK] OpenSearch is ready."
        break
    fi
    if [ "$i" -eq "$MAX_RETRIES" ]; then
        echo "[ERROR] OpenSearch not ready after $MAX_RETRIES attempts."
        exit 1
    fi
    echo "  Attempt $i/$MAX_RETRIES..."
    sleep 5
done

echo
echo "[INFO] Running securityadmin.sh..."
echo "  This will load users, roles, and configuration from:"
echo "    $SECURITY_CONFIG"
echo

docker exec "$CONTAINER" bash -c "
    chmod +x $SECURITY_ADMIN && \
    $SECURITY_ADMIN \
        -cd $SECURITY_CONFIG \
        -cacert $CERTS_PATH/ca.pem \
        -cert $CERTS_PATH/admin.pem \
        -key $CERTS_PATH/admin-key.pem \
        -icl -nhnv
"

echo
echo "[OK] Security initialization complete!"
echo
echo "Verifying..."
HEALTH=$(docker exec "$CONTAINER" curl -sf --insecure -u admin:admin https://localhost:9200/_cluster/health 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "[OK] Authenticated access works."
    echo "$HEALTH" | python3 -m json.tool 2>/dev/null || echo "$HEALTH"
else
    echo "[WARN] Could not verify authenticated access. Check logs:"
    echo "  docker compose logs opensearch-node-1"
fi
