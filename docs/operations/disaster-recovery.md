# Disaster Recovery Guide

This document describes backup strategies, restore procedures, and recovery objectives for the Vaultize Analytics Platform.

## Recovery Objectives

| Metric | Target | Notes |
|--------|--------|-------|
| **RPO** (Recovery Point Objective) | 1 hour | Maximum acceptable data loss |
| **RTO** (Recovery Time Objective) | 30 minutes | Maximum acceptable downtime |
| **Backup Frequency** | Every 6 hours | Automated via cron |

## Backup Strategy

### What Gets Backed Up

| Data | Method | Location | Frequency |
|------|--------|----------|-----------|
| Log indices (`logs-*`) | OpenSearch snapshots | `/mnt/snapshots` | Every 6 hours |
| Alert state (`.alerts-*`) | OpenSearch snapshots | `/mnt/snapshots` | Every 6 hours |
| Alert rules (`configs/`) | Git version control | Remote repository | On change |
| Dashboard configs | Git version control | Remote repository | On change |
| Platform configs | Git version control | Remote repository | On change |
| Docker volumes | Host filesystem backup | External storage | Daily |

### What Does NOT Need Backup

- **OpenSearch system indices**: Recreated automatically on startup
- **Prometheus metrics**: Short-term data, not critical for DR
- **Grafana dashboards**: Provisioned from files on startup
- **Fluent Bit state**: Position tracking DBs are transient

## Backup Procedures

### Automated Snapshots

Set up a cron job to create snapshots every 6 hours:

```bash
# Add to crontab (crontab -e)
0 */6 * * * cd /path/to/vaultize && python scripts/ops/backup_opensearch.py >> /var/log/vaultize-backup.log 2>&1
```

### Manual Snapshot

```bash
# Create a snapshot
python scripts/ops/backup_opensearch.py

# List existing snapshots
python scripts/ops/backup_opensearch.py --list

# Verify a snapshot
python scripts/ops/backup_opensearch.py --verify vaultize-backup-20260217-120000
```

### Docker Volume Backup

```bash
# Stop services first (optional but recommended for consistency)
docker compose stop

# Backup OpenSearch data volumes
docker run --rm -v opensearch-data-1:/data -v /backup:/backup \
    alpine tar czf /backup/opensearch-data-1.tar.gz -C /data .

# Restart services
docker compose up -d
```

## Restore Procedures

### Restore from Snapshot (Preferred)

```bash
# List available snapshots
python scripts/ops/backup_opensearch.py --list

# Restore specific indices
python scripts/ops/restore_opensearch.py vaultize-backup-20260217-120000 \
    --indices "logs-*"

# Restore everything (close existing indices first)
python scripts/ops/restore_opensearch.py vaultize-backup-20260217-120000 \
    --close-first --indices "logs-*,alerts-*,.alerts-*"

# Restore with rename (to compare before replacing)
python scripts/ops/restore_opensearch.py vaultize-backup-20260217-120000 \
    --rename
```

### Full Platform Restore

If the entire platform needs rebuilding:

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd vaultize-analytics-dashboard
   ```

2. **Restore configuration**
   ```bash
   # Copy .env file from secure backup
   cp /backup/.env .
   ```

3. **Start services**
   ```bash
   docker compose up -d
   ```

4. **Wait for cluster health**
   ```bash
   python scripts/ops/health_check.py --verbose
   ```

5. **Bootstrap (templates, ILM, dashboards)**
   ```bash
   bash scripts/ops/bootstrap.sh --skip-data
   ```

6. **Restore data from snapshot**
   ```bash
   python scripts/ops/restore_opensearch.py <latest-snapshot>
   ```

7. **Verify restoration**
   ```bash
   # Check cluster health
   curl http://localhost:9200/_cluster/health?pretty

   # Check index count
   curl http://localhost:9200/_cat/indices?v

   # Run health check
   python scripts/ops/health_check.py --verbose
   ```

## Snapshot Repository Setup

### Local Filesystem (Default)

The snapshot repository uses a Docker volume mount. Add to `docker-compose.yml`:

```yaml
volumes:
  - snapshot-data:/mnt/snapshots

# In OpenSearch node config:
environment:
  - path.repo=/mnt/snapshots
```

### S3-Compatible Storage

For production, consider using S3-compatible storage (MinIO for on-prem):

```bash
# Register S3 repository
curl -X PUT "http://localhost:9200/_snapshot/s3_backups" -H 'Content-Type: application/json' -d '{
  "type": "s3",
  "settings": {
    "bucket": "vaultize-backups",
    "endpoint": "minio:9000",
    "protocol": "http"
  }
}'
```

## Failure Scenarios

### Scenario 1: Single Node Failure

**Impact**: Minimal — 3-node cluster continues operating.

**Recovery**:
1. Identify failed node: `curl localhost:9200/_cat/nodes?v`
2. Restart the node: `docker compose restart opensearch-node-X`
3. Wait for shard recovery: `curl localhost:9200/_cat/recovery?v`

### Scenario 2: Full Cluster Failure

**Impact**: All services down.

**Recovery**:
1. `docker compose down`
2. `docker compose up -d`
3. Wait for green status
4. Verify with `python scripts/ops/health_check.py`

### Scenario 3: Data Corruption

**Impact**: Indices unreadable.

**Recovery**:
1. Close corrupted indices: `curl -X POST localhost:9200/corrupted-index/_close`
2. Restore from last good snapshot
3. Accept data loss since last snapshot (up to RPO)

### Scenario 4: Complete Data Loss

**Impact**: All data gone.

**Recovery**:
1. Rebuild platform from scratch (git clone + docker compose)
2. Run bootstrap script
3. Restore from off-site backup
4. If no backup: data is lost, platform is operational with empty indices

## Testing DR Procedures

Test disaster recovery quarterly:

1. Create a snapshot
2. Destroy the cluster (`docker compose down -v`)
3. Rebuild from scratch
4. Restore from snapshot
5. Verify data integrity
6. Document results and update this guide
