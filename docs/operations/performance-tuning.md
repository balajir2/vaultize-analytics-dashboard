# Performance Tuning Guide

Optimization recommendations for each component of the Vaultize Analytics Platform.

## OpenSearch Tuning

### Index Settings

For log data with high write throughput:

```json
{
  "settings": {
    "refresh_interval": "5s",
    "number_of_replicas": 1,
    "translog.durability": "async",
    "translog.flush_threshold_size": "512mb",
    "merge.policy.max_merged_segment": "5gb"
  }
}
```

### Query Performance

- Use `keyword` fields for filtering and aggregations
- Use `text` fields only for full-text search
- Avoid `wildcard` queries on large datasets
- Use `filter` context instead of `query` context when scoring isn't needed
- Limit `size` parameter — don't fetch more documents than needed

### Bulk Indexing

- **Batch size**: 5,000-10,000 documents per bulk request
- **Request size**: Keep under 100 MB per bulk request
- **Parallelism**: 2-4 concurrent bulk threads per node
- **Refresh**: Use `refresh=false` during bulk loads, refresh manually after

```python
# Good: Batch documents
for batch in chunks(documents, 5000):
    opensearch.bulk(body=batch, refresh=False)
opensearch.indices.refresh(index="logs-*")
```

### Memory

- Set JVM heap to 50% of available RAM (max 32 GB)
- Leave remaining RAM for OS filesystem cache
- Disable swap: `bootstrap.memory_lock: true`
- Use `-XX:+UseG1GC` for heaps > 8 GB

## Fluent Bit Tuning

### Buffer Management

```ini
[SERVICE]
    Flush         1
    Grace         5
    Log_Level     warn
    storage.type  filesystem
    storage.path  /var/log/flb-storage/
    storage.sync  normal
    storage.checksum off
    storage.max_chunks_up 128
```

### Output Tuning

```ini
[OUTPUT]
    Name          opensearch
    Match         *
    Workers       2
    Buffer_Size   5MB
    Retry_Limit   5
```

### Key Settings

| Setting | Default | Recommended | Purpose |
|---------|---------|-------------|---------|
| `Flush` | 1s | 1-5s | Flush interval |
| `Mem_Buf_Limit` | 5MB | 10-50MB | Per-input buffer |
| `Workers` | 1 | 2-4 | Output parallelism |
| `Buffer_Size` | - | 5MB | HTTP output buffer |

## Analytics API Tuning

### Uvicorn Workers

```bash
# Workers = 2 * CPU_CORES + 1
API_WORKERS=9  # For a 4-core machine
```

### Connection Pool

```python
# In config.py
opensearch_max_connections: int = 100  # Increase for high concurrency
opensearch_timeout: int = 30           # Reduce for faster failure detection
```

### Rate Limiting

```bash
# Adjust based on expected traffic
API_RATE_LIMIT_PER_MINUTE=1000  # Default
API_RATE_LIMIT_PER_MINUTE=5000  # High traffic
```

## Alerting Service Tuning

### Evaluation Interval

Balance freshness vs. OpenSearch load:

```json
{
  "schedule": {
    "interval": "60s"    // Default: evaluate every minute
  }
}
```

For high-priority alerts, use shorter intervals (30s). For trend-based alerts, use longer intervals (5m).

### Query Optimization

- Use time-bounded queries (last 5m, last 15m)
- Aggregate at the query level, not in Python
- Use `filter` aggregations for conditional counting

## Operating System Tuning

### Linux (Docker Host)

```bash
# /etc/sysctl.conf
vm.max_map_count=262144          # Required for OpenSearch
vm.swappiness=1                  # Minimize swap usage
net.core.somaxconn=65535         # TCP connection backlog
net.ipv4.tcp_max_syn_backlog=65535

# /etc/security/limits.conf
opensearch soft nofile 65536
opensearch hard nofile 65536
opensearch soft memlock unlimited
opensearch hard memlock unlimited
```

### Docker Desktop (Windows/Mac)

In Docker Desktop settings:
- **Memory**: At least 8 GB (16 GB recommended)
- **CPUs**: At least 4 cores
- **Disk**: Use SSD for Docker volumes

## Monitoring Performance

### Key Metrics to Watch

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Cluster status | yellow | red | Check shard allocation |
| Heap usage | >75% | >85% | Increase heap or add nodes |
| Disk usage | >75% | >85% | Add storage or adjust ILM |
| Search latency (p95) | >500ms | >2s | Optimize queries |
| Indexing rate drops | >20% drop | >50% drop | Check Fluent Bit, disk I/O |
| Rejected threads | any | sustained | Increase thread pool or reduce load |

### Health Check Commands

```bash
# Cluster health
curl localhost:9200/_cluster/health?pretty

# Node stats
curl localhost:9200/_nodes/stats?pretty

# Hot threads (identify slow queries)
curl localhost:9200/_nodes/hot_threads

# Pending tasks
curl localhost:9200/_cluster/pending_tasks?pretty

# Shard allocation
curl localhost:9200/_cat/shards?v&s=state
```
