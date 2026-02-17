# Secrets Management Guide

This document describes how secrets and credentials are managed in the Vaultize Analytics Platform.

## Overview

The platform uses **environment variables** for all secrets. No secrets are committed to source control. Default values exist only for local development.

## Secrets Inventory

| Secret | Environment Variable | Default (Dev Only) | Used By |
|--------|---------------------|---------------------|---------|
| OpenSearch admin password | `OPENSEARCH_ADMIN_PASSWORD` | `admin` | All services |
| API JWT signing key | `API_SECRET_KEY` | `CHANGE_ME_IN_PRODUCTION` | Analytics API |
| API admin username | `AUTH_ADMIN_USERNAME` | `admin` | Analytics API |
| API admin password | `AUTH_ADMIN_PASSWORD` | `admin` | Analytics API |
| Alerting JWT key | `ALERTING_SECRET_KEY` | `CHANGE_ME_IN_PRODUCTION` | Alerting Service |
| Grafana admin user | `GRAFANA_ADMIN_USER` | `admin` | Grafana |
| Grafana admin password | `GRAFANA_ADMIN_PASSWORD` | `admin` | Grafana |
| Fluent Bit OpenSearch user | `FLUENT_BIT_OS_USER` | (in secure config) | Fluent Bit |
| Fluent Bit OpenSearch pass | `FLUENT_BIT_OS_PASSWORD` | (in secure config) | Fluent Bit |

## Development Mode

In development mode (`ENVIRONMENT=development`), all defaults are acceptable. Authentication is disabled by default (`AUTH_ENABLED=false`) and security plugin is off (`DISABLE_SECURITY_PLUGIN=true`).

No `.env` file is required for basic development.

## Production Deployment

### Step 1: Generate Secrets

Generate strong, unique secrets for each credential:

```bash
# Generate a 256-bit random key for JWT
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate a strong password
python -c "import secrets; print(secrets.token_urlsafe(16))"
```

### Step 2: Create a .env File

Create a `.env` file in the project root (**never committed**):

```bash
# .env - Production Secrets
# WARNING: Never commit this file to version control

# OpenSearch
OPENSEARCH_ADMIN_PASSWORD=<generated-password>

# Authentication
AUTH_ENABLED=true
AUTH_ADMIN_USERNAME=vaultize-admin
AUTH_ADMIN_PASSWORD=<generated-password>
API_SECRET_KEY=<generated-key>

# Alerting
ALERTING_SECRET_KEY=<generated-key>

# Grafana
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=<generated-password>

# Environment
ENVIRONMENT=production
```

### Step 3: Set File Permissions

```bash
chmod 600 .env
```

On Windows, restrict access to the file through file properties.

### Step 4: Verify Configuration

```bash
# Start services
docker compose up -d

# Check API detects production mode
curl http://localhost:8000/health/liveness
```

The API will fail to start if `API_SECRET_KEY` is still set to the default in production mode.

## TLS Certificates

TLS certificates are managed separately from application secrets. See the [TLS setup guide](./security-hardening-checklist.md) for certificate generation.

Certificate files are stored in `infrastructure/certs/` and excluded from Git via `.gitignore`.

## Secret Rotation

### JWT Keys

1. Generate a new key
2. Update `API_SECRET_KEY` in `.env`
3. Restart the Analytics API: `docker compose restart analytics-api`
4. Existing tokens will be invalidated (users must re-authenticate)

### OpenSearch Passwords

1. Update password in OpenSearch security config
2. Run `scripts/ops/initialize_security.sh` to apply changes
3. Update all service `.env` entries
4. Restart affected services

### Grafana Passwords

1. Update `GRAFANA_ADMIN_PASSWORD` in `.env`
2. Restart Grafana: `docker compose restart grafana`

## Security Checklist

- [ ] All default passwords changed
- [ ] `API_SECRET_KEY` set to a random 256-bit value
- [ ] `.env` file has restricted permissions (600)
- [ ] `.env` is in `.gitignore`
- [ ] `AUTH_ENABLED=true` in production
- [ ] TLS certificates generated and configured
- [ ] Security plugin enabled (no `DISABLE_SECURITY_PLUGIN`)
- [ ] `CORS_ORIGINS` set to specific allowed domains
- [ ] Rate limiting enabled with appropriate limits

## Docker Compose Secrets (Alternative)

For Docker Swarm or Compose v2, you can use Docker secrets instead of environment variables:

```yaml
secrets:
  api_secret_key:
    file: ./secrets/api_secret_key.txt
  opensearch_password:
    file: ./secrets/opensearch_password.txt

services:
  analytics-api:
    secrets:
      - api_secret_key
    environment:
      - API_SECRET_KEY_FILE=/run/secrets/api_secret_key
```

This approach is recommended for production as it avoids secrets in environment variable listings.
