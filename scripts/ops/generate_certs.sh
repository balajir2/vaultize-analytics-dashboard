#!/bin/bash
# ==========================================================================
# TLS Certificate Generator for Vaultize Analytics Platform
#
# Generates a self-signed CA and server certificates for all services.
# Certificates are stored in infrastructure/certs/
#
# Usage: ./scripts/ops/generate_certs.sh
#
# Authors: Balaji Rajan and Claude (Anthropic)
# License: Apache 2.0
# ==========================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CERTS_DIR="$PROJECT_ROOT/infrastructure/certs"
VALIDITY_DAYS=365

# Service hostnames (must match Docker Compose service names)
SERVICES=(
    "opensearch-node-1"
    "opensearch-node-2"
    "opensearch-node-3"
    "opensearch-dashboards"
    "analytics-api"
    "alerting-service"
)

echo "=========================================="
echo "Vaultize Analytics - TLS Certificate Generator"
echo "=========================================="
echo

# Create certs directory
mkdir -p "$CERTS_DIR"

# --------------------------------------------------------------------------
# Step 1: Generate CA certificate
# --------------------------------------------------------------------------
echo "[1/3] Generating Certificate Authority (CA)..."

if [ -f "$CERTS_DIR/ca.pem" ]; then
    echo "  CA certificate already exists. Skipping."
    echo "  Delete $CERTS_DIR/ca.pem to regenerate."
else
    openssl genrsa -out "$CERTS_DIR/ca-key.pem" 4096

    openssl req -new -x509 \
        -key "$CERTS_DIR/ca-key.pem" \
        -out "$CERTS_DIR/ca.pem" \
        -days "$VALIDITY_DAYS" \
        -subj "/C=US/ST=CA/L=SanFrancisco/O=Vaultize/OU=Analytics/CN=Vaultize CA"

    echo "  [OK] CA certificate generated: $CERTS_DIR/ca.pem"
fi

echo

# --------------------------------------------------------------------------
# Step 2: Generate server certificates with SAN
# --------------------------------------------------------------------------
echo "[2/3] Generating server certificates..."

# Build SAN string with all service hostnames + localhost
SAN="DNS:localhost,IP:127.0.0.1"
for svc in "${SERVICES[@]}"; do
    SAN="$SAN,DNS:$svc"
done

# Create OpenSSL config for SAN
cat > "$CERTS_DIR/openssl.cnf" <<EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = v3_req

[dn]
C = US
ST = CA
L = SanFrancisco
O = Vaultize
OU = Analytics
CN = Vaultize Server

[v3_req]
basicConstraints = CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth, clientAuth
subjectAltName = $SAN
EOF

# Generate server key and CSR
openssl genrsa -out "$CERTS_DIR/node-key.pem" 2048

openssl req -new \
    -key "$CERTS_DIR/node-key.pem" \
    -out "$CERTS_DIR/node.csr" \
    -config "$CERTS_DIR/openssl.cnf"

# Sign with CA
openssl x509 -req \
    -in "$CERTS_DIR/node.csr" \
    -CA "$CERTS_DIR/ca.pem" \
    -CAkey "$CERTS_DIR/ca-key.pem" \
    -CAcreateserial \
    -out "$CERTS_DIR/node.pem" \
    -days "$VALIDITY_DAYS" \
    -extensions v3_req \
    -extfile "$CERTS_DIR/openssl.cnf"

echo "  [OK] Server certificate generated: $CERTS_DIR/node.pem"
echo "  [OK] Server key generated: $CERTS_DIR/node-key.pem"

# Clean up CSR and serial
rm -f "$CERTS_DIR/node.csr" "$CERTS_DIR/ca.srl" "$CERTS_DIR/openssl.cnf"

echo

# --------------------------------------------------------------------------
# Step 3: Generate admin certificate (for securityadmin.sh)
# --------------------------------------------------------------------------
echo "[3/3] Generating admin certificate..."

openssl genrsa -out "$CERTS_DIR/admin-key.pem" 2048

openssl req -new \
    -key "$CERTS_DIR/admin-key.pem" \
    -out "$CERTS_DIR/admin.csr" \
    -subj "/C=US/ST=CA/L=SanFrancisco/O=Vaultize/OU=Analytics/CN=Admin"

openssl x509 -req \
    -in "$CERTS_DIR/admin.csr" \
    -CA "$CERTS_DIR/ca.pem" \
    -CAkey "$CERTS_DIR/ca-key.pem" \
    -CAcreateserial \
    -out "$CERTS_DIR/admin.pem" \
    -days "$VALIDITY_DAYS"

rm -f "$CERTS_DIR/admin.csr" "$CERTS_DIR/ca.srl"

echo "  [OK] Admin certificate generated: $CERTS_DIR/admin.pem"

echo
echo "=========================================="
echo "Certificate generation complete!"
echo "=========================================="
echo
echo "Files created in $CERTS_DIR:"
ls -la "$CERTS_DIR"/*.pem 2>/dev/null || echo "  (no .pem files found)"
echo
echo "Next steps:"
echo "  1. Start the secure stack: ./scripts/ops/start_secure.sh"
echo "  2. Initialize security: ./scripts/ops/initialize_security.sh"
echo
echo "WARNING: These are self-signed certificates for development/testing."
echo "         Use proper CA-signed certificates in production."
