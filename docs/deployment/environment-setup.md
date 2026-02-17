# Environment Setup Guide

> Quick guide to configuring environments for Vaultize Analytics Platform

**Authors**: Balaji Rajan and Claude (Anthropic)
**Last Updated**: 2026-02-17

---

## Quick Start

### Development (Local)

```bash
# 1. Copy example file
cp .env.example .env

# 2. Start services
docker compose up -d

# 3. Access services
open http://localhost:5601  # OpenSearch Dashboards
```

### Staging

```bash
# 1. Copy staging template
cp .env.staging.example .env.staging

# 2. Edit with your staging URLs
nano .env.staging

# 3. Deploy with staging config
docker compose --env-file .env.staging up -d
```

### Production

```bash
# 1. Copy production template
cp .env.production.example .env.production

# 2. IMPORTANT: Edit with production URLs and secrets
nano .env.production

# 3. Validate configuration
./scripts/ops/validate-config.sh .env.production

# 4. Deploy with production config
docker compose --env-file .env.production up -d
```

---

## Environment Files Overview

| File | Purpose | Committed to Git? |
|------|---------|-------------------|
| `.env.example` | Development template | ✅ Yes |
| `.env.staging.example` | Staging template | ✅ Yes |
| `.env.production.example` | Production template | ✅ Yes |
| `.env` | Your actual dev config | ❌ No |
| `.env.staging` | Your actual staging config | ❌ No |
| `.env.production` | Your actual prod config | ❌ No |

---

## Key Differences by Environment

### Development
- **URLs**: localhost
- **Security**: Disabled (for easy development)
- **Resources**: Minimal (512MB RAM for OpenSearch)
- **TLS**: HTTP only
- **Logs**: Verbose (DEBUG level)

### Staging
- **URLs**: staging.example.com
- **Security**: Enabled (test security features)
- **Resources**: Moderate (2GB RAM for OpenSearch)
- **TLS**: HTTPS with self-signed or staging certs
- **Logs**: INFO level

### Production
- **URLs**: example.com
- **Security**: Fully enabled + hardened
- **Resources**: High (4-8GB RAM for OpenSearch)
- **TLS**: HTTPS with valid certificates
- **Logs**: WARNING level (reduce noise)

---

## Configuration Examples

### Development (.env)
```bash
ENVIRONMENT=development
OPENSEARCH_HOST=opensearch-node-1
API_BASE_URL=http://localhost:8000
OPENSEARCH_SECURITY_ENABLED=false
```

### Staging (.env.staging)
```bash
ENVIRONMENT=staging
OPENSEARCH_HOST=opensearch.staging.internal
API_BASE_URL=https://api.staging.example.com
OPENSEARCH_SECURITY_ENABLED=true
```

### Production (.env.production)
```bash
ENVIRONMENT=production
OPENSEARCH_HOST=opensearch.prod.internal
API_BASE_URL=https://api.example.com
OPENSEARCH_SECURITY_ENABLED=true
OPENSEARCH_ADMIN_PASSWORD=${VAULT_PASSWORD}  # From secrets manager
```

---

## URL Configuration Patterns

### Internal Communication (Docker Network)
```bash
# Services talk to each other using Docker network names
OPENSEARCH_HOST=opensearch-node-1
FLUENT_BIT_OPENSEARCH_HOST=opensearch-node-1
```

### External Access (Public URLs)
```bash
# Users and external systems use public URLs
OPENSEARCH_DASHBOARDS_PUBLIC_URL=https://logs.example.com
API_BASE_URL=https://api.example.com
GRAFANA_ROOT_URL=https://grafana.example.com
```

---

## Secrets Management

### ❌ Bad (Hardcoded in .env)
```bash
OPENSEARCH_ADMIN_PASSWORD=mysecretpassword123
```

### ✅ Good (Reference to secrets manager)
```bash
# Using HashiCorp Vault
OPENSEARCH_ADMIN_PASSWORD=${VAULT_OPENSEARCH_PASSWORD}

# Using environment variable injection
OPENSEARCH_ADMIN_PASSWORD=${SECRET_OPENSEARCH_PASSWORD}

# Load from external source at runtime
# secrets.sh will inject these variables
```

### Loading Secrets

**Option 1: Environment Variables**
```bash
# Load from secrets manager before starting
export OPENSEARCH_ADMIN_PASSWORD=$(vault read -field=password secret/opensearch)
docker compose up -d
```

**Option 2: Secrets File**
```bash
# Create secrets file (not committed)
cat > .secrets <<EOF
export OPENSEARCH_ADMIN_PASSWORD="actual-password"
export API_SECRET_KEY="actual-secret-key"
EOF

# Load and deploy
source .secrets
docker compose up -d
```

---

## Deployment Workflow

### Development → Staging

1. **Prepare Staging Environment**
   ```bash
   cp .env.staging.example .env.staging
   ```

2. **Update URLs**
   ```bash
   # Edit .env.staging
   OPENSEARCH_HOST=opensearch.staging.internal
   API_BASE_URL=https://api.staging.example.com
   ```

3. **Test Connectivity**
   ```bash
   # Verify URLs are reachable
   curl https://api.staging.example.com/health
   ```

4. **Deploy**
   ```bash
   docker compose --env-file .env.staging up -d
   ```

5. **Verify**
   ```bash
   ./scripts/ops/health-check.sh
   ```

### Staging → Production

1. **Security Review**
   - [ ] All secrets rotated
   - [ ] TLS certificates valid
   - [ ] Firewall rules configured
   - [ ] Backups tested

2. **Configuration**
   ```bash
   cp .env.production.example .env.production
   # Edit with production values
   ```

3. **Dry Run**
   ```bash
   # Validate without starting
   docker compose --env-file .env.production config
   ```

4. **Deploy**
   ```bash
   docker compose --env-file .env.production up -d
   ```

5. **Monitor**
   ```bash
   # Watch logs during deployment
   docker compose logs -f
   ```

---

## Troubleshooting

### Wrong Environment Loaded

**Problem**: Running production config in development

**Solution**: Always specify env file explicitly
```bash
# Bad (uses .env by default)
docker compose up -d

# Good (explicit)
docker compose --env-file .env.staging up -d
```

### URLs Not Updating

**Problem**: Changed .env but services still use old URLs

**Solution**: Recreate containers
```bash
docker compose down
docker compose --env-file .env.staging up -d --force-recreate
```

### Can't Connect to Service

**Problem**: Service unreachable after changing hostname

**Check**:
```bash
# 1. Verify environment variable loaded
docker compose config | grep OPENSEARCH_HOST

# 2. Check DNS resolution
nslookup opensearch.staging.internal

# 3. Test connectivity
telnet opensearch.staging.internal 9200
```

---

## Environment Variables Cheat Sheet

| Variable | Dev | Staging | Production |
|----------|-----|---------|------------|
| `ENVIRONMENT` | development | staging | production |
| `OPENSEARCH_HOST` | opensearch-node-1 | opensearch.staging.internal | opensearch.prod.internal |
| `OPENSEARCH_SCHEME` | http | https | https |
| `OPENSEARCH_SECURITY_ENABLED` | false | true | true |
| `API_BASE_URL` | http://localhost:8000 | https://api.staging.example.com | https://api.example.com |
| `API_LOG_LEVEL` | DEBUG | INFO | WARNING |
| `API_WORKERS` | 2 | 4 | 8 |
| `LOG_RETENTION_DAYS` | 7 | 30 | 90 |
| `BACKUP_ENABLED` | false | true | true |

---

## Best Practices

1. **Never commit `.env.production`** - Add to .gitignore
2. **Use templates** - Commit `.env.production.example` instead
3. **Rotate secrets** - Different passwords for each environment
4. **Test in staging** - Deploy to staging before production
5. **Document changes** - Update templates when adding new variables
6. **Validate configs** - Run validation scripts before deployment
7. **Use secrets managers** - Don't hardcode passwords in .env files

---

## Quick Commands

```bash
# View current configuration (without secrets)
docker compose config

# Check which environment is loaded
docker compose config | grep ENVIRONMENT

# Validate environment file syntax
set -a; source .env.production; set +a

# Start with specific environment
docker compose --env-file .env.staging up -d

# Reload configuration (restart services)
docker compose --env-file .env.staging up -d --force-recreate

# Stop services
docker compose down
```

---

## Related Documentation

- [Configuration Reference](./configuration.md) - Complete variable list
- [Security Hardening Checklist](../operations/security-hardening-checklist.md) - Security best practices
- [Secrets Management](../operations/secrets-management.md) - Credentials and secrets

---

**Last Updated**: 2026-02-17
