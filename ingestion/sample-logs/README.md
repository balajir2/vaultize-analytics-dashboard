# Sample Logs Directory

> Drop log files here for automatic ingestion into OpenSearch via Fluent Bit.

## Supported Formats

| Extension | Parser | Format |
|-----------|--------|--------|
| `*.log` | `app_json` | JSON objects, one per line. Must have a `timestamp` field in ISO 8601 format. |
| `*.txt` | `app_structured` | Structured text: `TIMESTAMP [LEVEL] [SERVICE] message` |

## JSON Log Example (`*.log`)

```json
{"timestamp": "2026-02-17T10:00:00.000Z", "level": "INFO", "service": "api-service", "message": "Request processed successfully"}
{"timestamp": "2026-02-17T10:00:01.000Z", "level": "ERROR", "service": "db-service", "message": "Connection timeout after 30s"}
```

## Structured Text Example (`*.txt`)

```
2026-02-17T10:00:00.000Z [INFO] [api-service] Request processed successfully
2026-02-17T10:00:01.000Z [ERROR] [db-service] Connection timeout after 30s
```

## How It Works

1. Fluent Bit tails all files in this directory (mounted as `/var/log/app-logs/` in the container)
2. New lines are parsed using the appropriate parser based on file extension
3. Parsed logs are forwarded to OpenSearch into `logs-YYYY.MM.DD` indices
4. Fluent Bit tracks its read position in a DB file, so it won't re-read old entries on restart

## Notes

- Files are read from the beginning (`Read_from_Head: True`)
- Fluent Bit checks for new data every 5 seconds
- Maximum line length is enforced (`Skip_Long_Lines: On`)
- This directory is mounted read-only into the Fluent Bit container
