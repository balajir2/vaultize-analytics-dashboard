#!/usr/bin/env python3
"""
TLS Certificate Generator for Vaultize Analytics Platform (Python/Windows)

Generates a self-signed CA and server certificates for all services.
Certificates are stored in infrastructure/certs/

Usage: python scripts/ops/generate_certs.py

Authors: Balaji Rajan and Claude (Anthropic)
License: Apache 2.0
"""

import datetime
import ipaddress
from pathlib import Path

try:
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID
except ImportError:
    print("[ERROR] 'cryptography' library is required.")
    print("  Install it with: pip install cryptography")
    raise SystemExit(1)

# ============================================================================
# Configuration
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CERTS_DIR = PROJECT_ROOT / "infrastructure" / "certs"
VALIDITY_DAYS = 365

SERVICES = [
    "opensearch-node-1",
    "opensearch-node-2",
    "opensearch-node-3",
    "opensearch-dashboards",
    "analytics-api",
    "alerting-service",
]


# ============================================================================
# Certificate Generation
# ============================================================================

def generate_key(key_size: int = 2048) -> rsa.RSAPrivateKey:
    """Generate an RSA private key."""
    return rsa.generate_private_key(public_exponent=65537, key_size=key_size)


def save_key(key: rsa.RSAPrivateKey, path: Path) -> None:
    """Save a private key to PEM file."""
    path.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )


def save_cert(cert: x509.Certificate, path: Path) -> None:
    """Save a certificate to PEM file."""
    path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))


def generate_ca() -> tuple:
    """Generate a self-signed CA certificate and key."""
    key = generate_key(4096)

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "SanFrancisco"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Vaultize"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Analytics"),
        x509.NameAttribute(NameOID.COMMON_NAME, "Vaultize CA"),
    ])

    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=VALIDITY_DAYS))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(key, hashes.SHA256())
    )

    return key, cert


def generate_server_cert(ca_key, ca_cert) -> tuple:
    """Generate a server certificate signed by the CA."""
    key = generate_key(2048)

    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "SanFrancisco"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Vaultize"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Analytics"),
        x509.NameAttribute(NameOID.COMMON_NAME, "Vaultize Server"),
    ])

    # Build SAN list
    san_names = [
        x509.DNSName("localhost"),
        x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
    ]
    for svc in SERVICES:
        san_names.append(x509.DNSName(svc))

    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=VALIDITY_DAYS))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True, key_encipherment=True,
                content_commitment=False, data_encipherment=False,
                key_agreement=False, key_cert_sign=False,
                crl_sign=False, encipher_only=False, decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.ExtendedKeyUsage([
                ExtendedKeyUsageOID.SERVER_AUTH,
                ExtendedKeyUsageOID.CLIENT_AUTH,
            ]),
            critical=False,
        )
        .add_extension(
            x509.SubjectAlternativeName(san_names),
            critical=False,
        )
        .sign(ca_key, hashes.SHA256())
    )

    return key, cert


def generate_admin_cert(ca_key, ca_cert) -> tuple:
    """Generate an admin certificate for securityadmin.sh."""
    key = generate_key(2048)

    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CA"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "SanFrancisco"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Vaultize"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Analytics"),
        x509.NameAttribute(NameOID.COMMON_NAME, "Admin"),
    ])

    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + datetime.timedelta(days=VALIDITY_DAYS))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .sign(ca_key, hashes.SHA256())
    )

    return key, cert


# ============================================================================
# Main
# ============================================================================

def main():
    print("=" * 50)
    print("Vaultize Analytics - TLS Certificate Generator")
    print("=" * 50)
    print()

    CERTS_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: CA
    print("[1/3] Generating Certificate Authority (CA)...")
    ca_key_path = CERTS_DIR / "ca-key.pem"
    ca_cert_path = CERTS_DIR / "ca.pem"

    if ca_cert_path.exists():
        print("  CA certificate already exists. Skipping.")
        print(f"  Delete {ca_cert_path} to regenerate.")
        # Load existing CA
        ca_key = serialization.load_pem_private_key(ca_key_path.read_bytes(), password=None)
        ca_cert = x509.load_pem_x509_certificate(ca_cert_path.read_bytes())
    else:
        ca_key, ca_cert = generate_ca()
        save_key(ca_key, ca_key_path)
        save_cert(ca_cert, ca_cert_path)
        print(f"  [OK] CA certificate: {ca_cert_path}")

    # Step 2: Server certificate
    print("[2/3] Generating server certificate...")
    server_key, server_cert = generate_server_cert(ca_key, ca_cert)
    save_key(server_key, CERTS_DIR / "node-key.pem")
    save_cert(server_cert, CERTS_DIR / "node.pem")
    print(f"  [OK] Server certificate: {CERTS_DIR / 'node.pem'}")

    # Step 3: Admin certificate
    print("[3/3] Generating admin certificate...")
    admin_key, admin_cert = generate_admin_cert(ca_key, ca_cert)
    save_key(admin_key, CERTS_DIR / "admin-key.pem")
    save_cert(admin_cert, CERTS_DIR / "admin.pem")
    print(f"  [OK] Admin certificate: {CERTS_DIR / 'admin.pem'}")

    print()
    print("=" * 50)
    print("Certificate generation complete!")
    print("=" * 50)
    print()
    print(f"Files in {CERTS_DIR}:")
    for f in sorted(CERTS_DIR.glob("*.pem")):
        print(f"  {f.name}")
    print()
    print("Next steps:")
    print("  1. Start the secure stack: scripts/ops/start_secure.sh")
    print("  2. Initialize security: scripts/ops/initialize_security.sh")
    print()
    print("WARNING: These are self-signed certificates for development/testing.")
    print("         Use proper CA-signed certificates in production.")


if __name__ == "__main__":
    main()
