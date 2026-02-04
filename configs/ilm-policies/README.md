# Index Lifecycle Management (ILM) Policies

> Automated index lifecycle management for the Vaultize Analytics Platform

**Authors**: Balaji Rajan and Claude (Anthropic)
**Last Updated**: 2026-02-04

---

## Overview

ILM policies automate index management through different lifecycle phases: **Hot** → **Warm** → **Cold** → **Delete**

This ensures:
- Optimal performance for recent data
- Efficient storage for older data
- Automatic cleanup of expired data
- Cost optimization (less resources for old data)

---

## Available Policies

### logs-lifecycle-policy.json

**Purpose**: Standard lifecycle for application and system logs

**Phases**:

| Phase | Age | Actions | Purpose |
|-------|-----|---------|---------|
| **Hot** | 0-3 days | Rollover at 1d or 50GB<br>High priority (100) | Active indexing and querying |
| **Warm** | 3-7 days | Reduce priority (50)<br>Force merge to 1 segment<br>Shrink to 1 shard<br>Read-only | Occasional queries, optimized storage |
| **Cold** | 7-30 days | Lowest priority (0)<br>No replicas<br>Read-only | Rare access, minimal resources |
| **Delete** | 30+ days | Delete index | Free up storage |

**Retention**: 30 days total

**Disk Space Optimization**:
- Force merge reduces segment overhead
- Shrink reduces shard count
- Replica removal in cold phase saves 50% storage

---

## Lifecycle Phases Explained

### Hot Phase (Active Data)

**Purpose**: High-performance indexing and searching

**Actions**:
- **Rollover**: Create new index when:
  - Age > 1 day, OR
  - Size > 50GB, OR
  - Doc count > 100M
- **Set Priority**: 100 (highest)

**Characteristics**:
- Most recent data
- Frequent reads and writes
- Multiple shards for performance
- Full replicas for availability

---

### Warm Phase (Recent Historical Data)

**Purpose**: Optimize for storage efficiency

**Actions**:
- **Set Priority**: 50 (medium)
- **Allocate**: Maintain 1 replica
- **Read-only**: Prevent further writes
- **Force Merge**: Merge to 1 segment (reduces overhead)
- **Shrink**: Reduce to 1 shard (less resources)

**Characteristics**:
- Occasional queries
- No new data
- Optimized for storage
- Slower query performance (acceptable for old data)

---

### Cold Phase (Archival Data)

**Purpose**: Minimize resource usage

**Actions**:
- **Set Priority**: 0 (lowest)
- **Allocate**: 0 replicas (single copy)
- **Read-only**: No writes allowed

**Characteristics**:
- Rare access
- Minimal disk and memory usage
- No fault tolerance (single copy)
- Slowest query performance

---

### Delete Phase (Cleanup)

**Purpose**: Free up storage

**Actions**:
- **Delete**: Permanently remove index

**Characteristics**:
- Data beyond retention period
- Frees disk space
- Irreversible

---

## Applying ILM Policies

### Via API

```bash
# Create the policy
curl -X PUT "http://localhost:9200/_plugins/_ism/policies/logs-lifecycle-policy" \
  -H 'Content-Type: application/json' \
  -d @logs-lifecycle-policy.json

# Verify policy was created
curl http://localhost:9200/_plugins/_ism/policies/logs-lifecycle-policy
```

### Via Script

```bash
# Apply all ILM policies
./scripts/ops/apply-ilm-policies.sh
```

### Attach to Index Template

Already configured in `logs-template.json`:
```json
"settings": {
  "index": {
    "lifecycle": {
      "name": "logs-lifecycle-policy",
      "rollover_alias": "logs"
    }
  }
}
```

---

## Monitoring ILM

### Check Policy Status

```bash
# List all policies
curl http://localhost:9200/_plugins/_ism/policies

# Explain lifecycle for specific index
curl http://localhost:9200/logs-2026.02.01/_plugins/_ism/explain
```

### Check Index Phases

```bash
# See which phase each index is in
curl http://localhost:9200/_cat/indices/logs-*?v&h=index,pri,rep,docs.count,store.size,creation.date

# Check specific index
curl http://localhost:9200/logs-2026.02.01/_ilm/explain
```

---

## Customizing Policies

### Adjust Retention Period

Change `delete` phase `min_age`:
```json
"delete": {
  "min_age": "90d",  // Keep for 90 days instead of 30
  "actions": {
    "delete": {}
  }
}
```

### Disable Phase

Remove the phase entirely:
```json
{
  "policy": {
    "phases": {
      "hot": { ... },
      "warm": { ... }
      // No cold or delete phases
    }
  }
}
```

### Adjust Rollover Criteria

```json
"hot": {
  "actions": {
    "rollover": {
      "max_age": "7d",        // Rollover weekly instead of daily
      "max_primary_shard_size": "100gb",  // Larger shards
      "max_docs": 500000000   // More docs per shard
    }
  }
}
```

---

## Best Practices

1. **Start Conservative**
   - Begin with longer retention (90d)
   - Reduce as you understand usage patterns
   - Easier to keep data than recover deleted data

2. **Match Business Requirements**
   - Legal retention requirements
   - Compliance mandates (GDPR, HIPAA, etc.)
   - Operational needs (how far back do you query?)

3. **Monitor Disk Usage**
   ```bash
   # Check cluster disk usage
   curl http://localhost:9200/_cat/allocation?v

   # Check index sizes
   curl http://localhost:9200/_cat/indices?v&s=store.size:desc
   ```

4. **Test Phase Transitions**
   - Manually move index to next phase
   - Verify performance impact
   - Ensure queries still work

5. **Balance Performance vs Cost**
   - Hot phase: Fast, expensive
   - Warm phase: Slower, cheaper
   - Cold phase: Slowest, cheapest
   - Delete: Free (but data is gone)

---

## Troubleshooting

### Index Not Transitioning

**Problem**: Index stuck in a phase

**Solutions**:
```bash
# Check for errors
curl http://localhost:9200/logs-2026.02.01/_plugins/_ism/explain

# Retry policy
curl -X POST "http://localhost:9200/_plugins/_ism/retry/logs-2026.02.01"

# Manually move to next phase (testing only)
curl -X POST "http://localhost:9200/_plugins/_ism/change_policy/logs-2026.02.01" \
  -H 'Content-Type: application/json' \
  -d '{"policy_id": "logs-lifecycle-policy", "state": "warm"}'
```

### Force Merge Failures

**Problem**: Force merge times out or fails

**Solutions**:
- Increase `max_num_segments` (e.g., 5 instead of 1)
- Run during low-traffic periods
- Ensure sufficient disk space (needs 2x index size temporarily)

### Shrink Failures

**Problem**: Shrink operation fails

**Solutions**:
- Ensure index is read-only
- Target shard count must divide evenly into source shard count
- Sufficient resources on target node

---

## Example Workflows

### Create New Log Index with ILM

```bash
# Create initial index with alias
PUT /logs-000001
{
  "aliases": {
    "logs": {
      "is_write_index": true
    }
  }
}

# Index uses template, template has ILM policy
# ILM handles rollover automatically
```

### Query Across All Phases

```bash
# Query all log indices regardless of phase
GET /logs-*/_search
{
  "query": {
    "match": {
      "level": "ERROR"
    }
  }
}

# Or use alias
GET /logs-all/_search
```

---

## Storage Calculations

**Example**: 1GB/day of logs, 30-day retention

| Phase | Days | Size/Day | Total Size | Notes |
|-------|------|----------|------------|-------|
| Hot | 3 | 1GB | 3GB | Full indexing overhead |
| Warm | 4 | 0.5GB | 2GB | Force merged, shrunk |
| Cold | 23 | 0.25GB | 5.75GB | No replicas |
| **Total** | **30** | | **~11GB** | vs 30GB without ILM |

**Savings**: ~60% disk space with ILM

---

## Related Files

- [Index Templates](../index-templates/README.md) - Index structure and mappings
- [Bootstrap Script](../../scripts/ops/bootstrap.sh) - Applies policies on startup
- [OpenSearch ILM Documentation](https://opensearch.org/docs/latest/im-plugin/)

---

**Last Updated**: 2026-02-04
