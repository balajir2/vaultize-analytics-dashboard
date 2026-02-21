# Resource Sizing Guide

Recommended resource allocations for different deployment sizes of the Vaultize Analytics Platform.

## Deployment Profiles

### Small (Development / POC)

**Capacity**: Up to 10 GB/day log ingestion, ~10 users

| Component | CPU | Memory | Storage | Instances |
|-----------|-----|--------|---------|-----------|
| OpenSearch | 2 cores | 4 GB | 50 GB SSD | 3 nodes |
| OpenSearch Dashboards | 1 core | 1 GB | - | 1 |
| Fluent Bit | 0.5 core | 256 MB | - | 1 |
| Analytics API | 1 core | 512 MB | - | 1 |
| Alerting Service | 0.5 core | 256 MB | - | 1 |
| Prometheus (optional) | 0.5 core | 512 MB | 10 GB | 1 |
| Grafana (optional) | 0.5 core | 256 MB | 1 GB | 1 |
| OpenSearch Exporter (optional) | 0.25 core | 128 MB | - | 1 |
| **Total** | **6-7 cores** | **7-8 GB** | **60+ GB** | |

**Host Requirements**: 8-core CPU, 16 GB RAM, 100 GB SSD

### Medium (Production / Small Team)

**Capacity**: Up to 50 GB/day log ingestion, ~50 users

| Component | CPU | Memory | Storage | Instances |
|-----------|-----|--------|---------|-----------|
| OpenSearch | 4 cores | 8 GB | 200 GB SSD | 3 nodes |
| OpenSearch Dashboards | 2 cores | 2 GB | - | 1 |
| Fluent Bit | 1 core | 512 MB | - | 1 |
| Analytics API | 2 cores | 1 GB | - | 2 (behind LB) |
| Alerting Service | 1 core | 512 MB | - | 1 |
| Prometheus | 1 core | 2 GB | 50 GB | 1 |
| Grafana | 1 core | 512 MB | 5 GB | 1 |
| OpenSearch Exporter | 0.5 core | 256 MB | - | 1 |
| **Total** | **20+ cores** | **30+ GB** | **650+ GB** | |

**Host Requirements**: Dedicated server or VMs — 32-core CPU, 64 GB RAM, 1 TB SSD

### Large (Enterprise / High Volume)

**Capacity**: Up to 500 GB/day log ingestion, ~200 users

| Component | CPU | Memory | Storage | Instances |
|-----------|-----|--------|---------|-----------|
| OpenSearch (data) | 8 cores | 32 GB | 1 TB NVMe | 5+ nodes |
| OpenSearch (manager) | 4 cores | 8 GB | 50 GB SSD | 3 nodes |
| OpenSearch Dashboards | 4 cores | 4 GB | - | 2 (behind LB) |
| Fluent Bit | 2 cores | 1 GB | - | per-host |
| Analytics API | 4 cores | 2 GB | - | 4 (behind LB) |
| Alerting Service | 2 cores | 1 GB | - | 2 (HA) |
| Prometheus | 4 cores | 8 GB | 200 GB | 1 |
| Grafana | 2 cores | 1 GB | 10 GB | 2 (behind LB) |
| OpenSearch Exporter | 0.5 core | 256 MB | - | 1 |
| **Total** | **60+ cores** | **120+ GB** | **5+ TB** | |

**Host Requirements**: Multiple servers or VMs, load balancer, dedicated storage

## OpenSearch Tuning

### JVM Heap

Set JVM heap to **50% of available memory**, max 32 GB:

```yaml
environment:
  - OPENSEARCH_JAVA_OPTS=-Xms4g -Xmx4g  # Small
  - OPENSEARCH_JAVA_OPTS=-Xms8g -Xmx8g  # Medium
  - OPENSEARCH_JAVA_OPTS=-Xms16g -Xmx16g  # Large
```

### Shard Sizing

- **Target shard size**: 10-50 GB
- **Shards per index**: 1 (small), 3 (medium), 5+ (large)
- **Replicas**: 1 (standard), 2 (high availability)

### Index Settings

```json
{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1,
    "refresh_interval": "5s",
    "translog.flush_threshold_size": "512mb"
  }
}
```

## Storage Estimation

### Formula

```
Daily storage = (daily_log_volume_GB) × (1 + replicas) × 1.1 (overhead)
Total storage = daily_storage × retention_days
```

### Examples

| Daily Ingestion | Replicas | Retention | Total Storage |
|----------------|----------|-----------|---------------|
| 10 GB/day | 1 | 30 days | ~660 GB |
| 50 GB/day | 1 | 30 days | ~3.3 TB |
| 100 GB/day | 1 | 30 days | ~6.6 TB |
| 100 GB/day | 1 | 90 days | ~19.8 TB |

## Docker Compose Resource Limits

For Docker Compose deployments, set resource limits:

```yaml
services:
  opensearch-node-1:
    deploy:
      resources:
        limits:
          memory: 8g
          cpus: "4.0"
        reservations:
          memory: 4g
          cpus: "2.0"
```

## Monitoring Resource Usage

```bash
# Docker container stats
docker stats

# OpenSearch cluster stats
curl localhost:9200/_nodes/stats/os,jvm?pretty

# Check disk usage
curl localhost:9200/_cat/allocation?v
```
