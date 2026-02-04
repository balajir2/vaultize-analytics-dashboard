# Index Templates

> OpenSearch index templates for the Vaultize Analytics Platform

**Authors**: Balaji Rajan and Claude (Anthropic)
**Last Updated**: 2026-02-04

---

## Overview

Index templates define the structure, settings, and mappings for indices before they are created. This ensures consistency across time-based indices.

---

## Available Templates

### logs-template.json

**Pattern**: `logs-*`
**Purpose**: Application and system logs

**Key Features**:
- Optimized for log data (text search + keyword filtering)
- Time-series oriented (@timestamp field)
- Automatic lifecycle management (ILM)
- Structured error and exception tracking
- HTTP request/response tracking
- Kubernetes and Docker metadata support

**Field Mappings**:
- `@timestamp`, `timestamp` - Date fields
- `level`, `severity` - Log levels (keyword)
- `message` - Main log message (text + keyword)
- `service`, `host`, `environment` - Context (keyword)
- `error`, `exception` - Structured error tracking
- `http` - HTTP request/response data
- `kubernetes`, `docker` - Container metadata

**Settings**:
- 3 primary shards, 1 replica
- Best compression codec
- 5-second refresh interval
- Linked to `logs-lifecycle-policy`

---

## Applying Templates

### Via API

```bash
# Apply logs template
curl -X PUT "http://localhost:9200/_index_template/logs-template" \
  -H 'Content-Type: application/json' \
  -d @logs-template.json
```

### Via Script

```bash
# Apply all templates
./scripts/ops/apply-index-templates.sh
```

---

## Template Structure

```json
{
  "index_patterns": ["logs-*"],
  "template": {
    "settings": { ... },
    "mappings": { ... },
    "aliases": { ... }
  },
  "priority": 100,
  "version": 1,
  "_meta": { ... }
}
```

**Fields Explained**:
- `index_patterns`: Which indices this template applies to
- `template.settings`: Index configuration (shards, replicas, ILM, etc.)
- `template.mappings`: Field types and analyzers
- `template.aliases`: Index aliases for easy querying
- `priority`: Template priority (higher = preferred)
- `version`: Template version for tracking changes
- `_meta`: Metadata about the template

---

## Field Type Reference

| OpenSearch Type | Use Case | Example Fields |
|-----------------|----------|----------------|
| `keyword` | Exact matching, aggregations | level, service, host |
| `text` | Full-text search | message, error.message |
| `date` | Time-based queries | @timestamp, timestamp |
| `long` | Large numbers | http.response_time_ms |
| `integer` | Numbers | http.status_code |
| `ip` | IP addresses | ip_address, client_ip |
| `object` | Nested structures | error, http, kubernetes |

---

## Best Practices

1. **Use keyword for exact matching**
   - Service names, hostnames, log levels
   - Enables fast aggregations and filtering

2. **Use text for full-text search**
   - Log messages, error messages
   - Allows searching for phrases and terms

3. **Use multi-fields when needed**
   ```json
   "message": {
     "type": "text",
     "fields": {
       "keyword": {
         "type": "keyword",
         "ignore_above": 256
       }
     }
   }
   ```

4. **Set `index: false` for large fields**
   - Stack traces, raw data that doesn't need searching
   - Saves storage and indexing time

5. **Use dynamic templates sparingly**
   - Explicit mappings prevent mapping explosions
   - Better performance and predictability

---

## Modifying Templates

### Add a New Field

Edit the template JSON:
```json
"mappings": {
  "properties": {
    "new_field": {
      "type": "keyword"
    }
  }
}
```

Then reapply:
```bash
curl -X PUT "http://localhost:9200/_index_template/logs-template" \
  -H 'Content-Type: application/json' \
  -d @logs-template.json
```

**Note**: Changes only affect NEW indices, not existing ones.

### Update Existing Indices

To apply to existing indices, you must reindex:
```bash
POST /_reindex
{
  "source": {
    "index": "logs-2026.02.01"
  },
  "dest": {
    "index": "logs-2026.02.01-reindexed"
  }
}
```

---

## Viewing Templates

```bash
# List all index templates
curl http://localhost:9200/_index_template

# View specific template
curl http://localhost:9200/_index_template/logs-template

# List indices using this template
curl http://localhost:9200/logs-*/_settings
```

---

## Troubleshooting

### Template Not Applying

**Problem**: New indices don't use the template

**Solutions**:
1. Check pattern matches index name
2. Verify template priority (higher wins)
3. Ensure template was applied successfully

### Mapping Conflicts

**Problem**: Field has different types in different indices

**Solutions**:
1. Use consistent field names and types
2. Reindex old data with correct mapping
3. Use index aliases to query across versions

### Performance Issues

**Problem**: Indexing or querying is slow

**Solutions**:
1. Reduce number of shards for small datasets
2. Use `keyword` instead of `text` where possible
3. Disable indexing for large unused fields
4. Tune `refresh_interval` (higher = better performance)

---

## Related Files

- [ILM Policies](../ilm-policies/README.md) - Index lifecycle management
- [Schemas](../schemas/README.md) - Log schemas and validation
- [Bootstrap Script](../../scripts/ops/bootstrap.sh) - Applies templates on startup

---

**Last Updated**: 2026-02-04
