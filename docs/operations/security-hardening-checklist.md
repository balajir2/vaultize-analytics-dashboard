# Security Hardening Checklist

Step-by-step checklist for hardening the Vaultize Analytics Platform for production deployment.

## Pre-Deployment

### Secrets & Credentials

- [ ] Generate strong `API_SECRET_KEY` (256-bit random): `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- [ ] Set unique `AUTH_ADMIN_PASSWORD` (not default "admin")
- [ ] Set unique `OPENSEARCH_ADMIN_PASSWORD`
- [ ] Set unique `GRAFANA_ADMIN_PASSWORD`
- [ ] Set unique `ALERTING_SECRET_KEY`
- [ ] Store all secrets in `.env` file with `chmod 600` permissions
- [ ] Verify `.env` is in `.gitignore`

### TLS Certificates

- [ ] Generate CA and server certificates: `bash scripts/ops/generate_certs.sh` or `python scripts/ops/generate_certs.py`
- [ ] Verify certificates in `infrastructure/certs/`
- [ ] Set appropriate file permissions on private keys (`chmod 600 *.key`)

### Authentication

- [ ] Set `AUTH_ENABLED=true` in `.env`
- [ ] Verify JWT authentication works: login → get token → access protected endpoint
- [ ] Verify unauthorized access returns 401

### OpenSearch Security

- [ ] Start with security overlay: `bash scripts/ops/start_secure.sh`
- [ ] Initialize security config: `bash scripts/ops/initialize_security.sh`
- [ ] Verify security plugin is active: check for HTTPS and auth prompts
- [ ] Update default passwords in `internal_users.yml` (hash with `securityadmin` tool)
- [ ] Verify role-based access: Fluent Bit can write logs, API can read logs

## Network Security

### CORS

- [ ] Set `API_CORS_ORIGINS` to specific allowed domains (not `*`)
- [ ] Set `ENVIRONMENT=production` to enforce restrictive CORS
- [ ] Verify CORS headers in API responses

### Rate Limiting

- [ ] Set `API_RATE_LIMIT_ENABLED=true`
- [ ] Configure `API_RATE_LIMIT_PER_MINUTE` to appropriate value (default: 1000)
- [ ] Verify rate limiting works: exceed limit → get 429 response

### Port Exposure

- [ ] Only expose necessary ports to the host network
- [ ] Consider using a reverse proxy (nginx) for external access
- [ ] Disable direct OpenSearch port access (9200) from external networks

## Data Protection

### Backups

- [ ] Configure snapshot repository: `python scripts/ops/backup_opensearch.py`
- [ ] Test backup creation and verification
- [ ] Set up automated backup schedule (cron job)
- [ ] Test restore procedure: `python scripts/ops/restore_opensearch.py`
- [ ] Store backups on separate storage (not same disk as data)

### Index Lifecycle

- [ ] Verify ILM policies are applied to log indices
- [ ] Confirm delete phase has appropriate retention (minimum 30 days)
- [ ] Test ILM transitions work correctly

## Monitoring

### Health Checks

- [ ] Run platform health check: `python scripts/ops/health_check.py --verbose`
- [ ] All required services pass health checks
- [ ] Set up automated health monitoring (cron + alerting)

### Logging

- [ ] Set `API_LOG_LEVEL=WARNING` for production (reduce noise)
- [ ] Ensure application logs don't contain sensitive data (passwords, tokens)
- [ ] Set up log rotation for application log files

## Post-Deployment Verification

- [ ] Run regression tests: `python -m pytest tests/regression/`
- [ ] Run E2E tests (with services running): `python -m pytest tests/e2e/`
- [ ] Verify OpenSearch cluster is green: `curl https://localhost:9200/_cluster/health`
- [ ] Verify dashboards load correctly in OpenSearch Dashboards
- [ ] Verify alert rules are evaluating correctly
- [ ] Test webhook notifications reach their destination

## Ongoing Maintenance

- [ ] Review and rotate secrets quarterly
- [ ] Update TLS certificates before expiry
- [ ] Monitor disk usage on OpenSearch data volumes
- [ ] Review and update ILM retention policies
- [ ] Keep Docker images up to date with security patches
- [ ] Test disaster recovery procedures quarterly
