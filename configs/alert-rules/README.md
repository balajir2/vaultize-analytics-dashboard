# Alert Rules

> Alert rule definitions for the Vaultize Analytics Platform

**Authors**: Balaji Rajan and Claude (Anthropic)
**Last Updated**: 2026-02-04

---

## Overview

Alert rules define conditions that trigger notifications when anomalies or issues are detected in logs.

**Alert Flow**:
```
Scheduled Query → Condition Check → Action (Webhook) → Notification
```

---

## Available Alert Rules

| Rule | Severity | Schedule | Condition | Action |
|------|----------|----------|-----------|--------|
| high-error-rate.json | High | 5m | Error count > 100 in 5min | Webhook |
| slow-api-response.json | Medium | 5m | P95 response time > 1000ms | Webhook |

---

## Alert Rule Structure

```json
{
  "name": "Alert Name",
  "description": "What this alert detects",
  "enabled": true,
  "schedule": {
    "interval": "5m"           // How often to check
  },
  "query": {
    "index": ["logs-*"],       // Which indices to query
    "time_field": "@timestamp",
    "time_range": {
      "from": "now-5m",
      "to": "now"
    },
    "filter": { ... },          // OpenSearch query
    "aggregation": { ... }      // Optional aggregation
  },
  "condition": {
    "type": "threshold",
    "operator": "gt",           // gt, lt, eq, gte, lte
    "value": 100
  },
  "actions": [
    {
      "type": "webhook",
      "webhook": {
        "url": "https://...",
        "body": { ... }
      }
    }
  ],
  "throttle": {
    "value": 15,
    "unit": "minutes"           // Prevent alert spam
  },
  "metadata": {
    "severity": "high",
    "category": "application",
    "owner": "team-name",
    "runbook": "https://..."
  }
}
```

---

## Alert Components

### 1. Schedule

How often the alert runs:
```json
"schedule": {
  "interval": "5m"    // Options: 1m, 5m, 15m, 1h, etc.
}
```

**Recommendations**:
- Critical alerts: 1-5 minutes
- Important alerts: 5-15 minutes
- Informational: 15-60 minutes

---

### 2. Query

OpenSearch query to fetch data:
```json
"query": {
  "index": ["logs-*"],
  "time_field": "@timestamp",
  "time_range": {
    "from": "now-5m",
    "to": "now"
  },
  "filter": {
    "bool": {
      "must": [
        { "match": { "level": "ERROR" } },
        { "term": { "service": "api" } }
      ]
    }
  }
}
```

**Query Types**:
- **Count**: How many logs match?
- **Aggregation**: Calculate metrics (avg, sum, percentiles)
- **Existence**: Does a field exist?

---

### 3. Condition

When to trigger the alert:
```json
"condition": {
  "type": "threshold",
  "operator": "gt",
  "value": 100
}
```

**Operators**:
- `gt`: Greater than
- `gte`: Greater than or equal
- `lt`: Less than
- `lte`: Less than or equal
- `eq`: Equal

---

### 4. Actions

What to do when alert fires:
```json
"actions": [
  {
    "type": "webhook",
    "name": "slack_notification",
    "webhook": {
      "url": "${ALERT_WEBHOOK_URL}",
      "method": "POST",
      "headers": {
        "Content-Type": "application/json"
      },
      "body": {
        "text": "Alert message here"
      }
    }
  }
]
```

**Action Types**:
- `webhook`: POST to URL (Slack, Teams, PagerDuty, custom)
- `email`: Send email (future)
- `log`: Write to logs (debugging)

---

### 5. Throttle

Prevent alert spam:
```json
"throttle": {
  "value": 15,
  "unit": "minutes"
}
```

If alert fires, don't fire again for 15 minutes even if condition is still true.

---

## Creating Alert Rules

### Step 1: Define the Problem

What are you trying to detect?
- High error rate
- Slow response times
- Failed logins
- Disk space low
- Service unavailable

### Step 2: Write the Query

Test in OpenSearch Dashboards Discover:
```json
GET /logs-*/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "level": "ERROR" } },
        { "range": { "@timestamp": { "gte": "now-5m" } } }
      ]
    }
  }
}
```

### Step 3: Define the Condition

When is it a problem?
- More than X errors in Y minutes
- Response time > Z milliseconds
- Count == 0 (service down)

### Step 4: Configure Actions

Where to send notifications?
- Slack webhook
- Teams webhook
- PagerDuty integration
- Email (requires SMTP config)

### Step 5: Test

1. Create rule with `enabled: false`
2. Manually test query
3. Verify webhook works
4. Enable rule

---

## Example Alert Rules

### High Error Rate (Count-based)

```json
{
  "name": "High Error Rate",
  "query": {
    "filter": {
      "match": { "level": "ERROR" }
    }
  },
  "condition": {
    "operator": "gt",
    "value": 100
  }
}
```

**Triggers when**: More than 100 errors in time window

---

### Slow Queries (Aggregation-based)

```json
{
  "name": "Slow Database Queries",
  "query": {
    "aggregation": {
      "avg": {
        "field": "query_time_ms"
      }
    }
  },
  "condition": {
    "aggregation_field": "avg",
    "operator": "gt",
    "value": 500
  }
}
```

**Triggers when**: Average query time > 500ms

---

### Service Down (Existence-based)

```json
{
  "name": "Service Heartbeat Missing",
  "query": {
    "filter": {
      "match": { "message": "heartbeat" }
    }
  },
  "condition": {
    "operator": "lt",
    "value": 1
  }
}
```

**Triggers when**: No heartbeat logs in time window

---

## Webhook Integrations

### Slack

```bash
# Create incoming webhook in Slack
# https://api.slack.com/messaging/webhooks

# Use in alert rule
{
  "webhook": {
    "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    "body": {
      "text": "Alert: {{alert.name}}",
      "blocks": [
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": "*{{alert.name}}*\n{{alert.description}}"
          }
        }
      ]
    }
  }
}
```

### Microsoft Teams

```json
{
  "webhook": {
    "url": "https://outlook.office.com/webhook/...",
    "body": {
      "@type": "MessageCard",
      "@context": "http://schema.org/extensions",
      "themeColor": "0076D7",
      "summary": "{{alert.name}}",
      "sections": [{
        "activityTitle": "{{alert.name}}",
        "text": "{{alert.description}}"
      }]
    }
  }
}
```

### PagerDuty

```json
{
  "webhook": {
    "url": "https://events.pagerduty.com/v2/enqueue",
    "headers": {
      "Content-Type": "application/json"
    },
    "body": {
      "routing_key": "YOUR_INTEGRATION_KEY",
      "event_action": "trigger",
      "payload": {
        "summary": "{{alert.name}}",
        "severity": "{{alert.severity}}",
        "source": "vaultize-analytics"
      }
    }
  }
}
```

---

## Best Practices

1. **Start Conservative**
   - Higher thresholds initially
   - Adjust based on actual alert volume
   - Avoid alert fatigue

2. **Meaningful Names**
   - Clear, descriptive alert names
   - Include what's wrong and where

3. **Actionable Alerts**
   - Include runbook link
   - Provide context in message
   - Make it clear what to do

4. **Appropriate Severity**
   - **Critical**: Service down, data loss
   - **High**: Significant degradation
   - **Medium**: Performance issues
   - **Low**: Warnings, informational

5. **Use Throttling**
   - Prevent alert storms
   - 10-15 minute throttle for most alerts
   - Longer for less critical alerts

6. **Test Thoroughly**
   - Verify query returns expected results
   - Test webhook actually sends
   - Confirm message format looks good

7. **Document Everything**
   - Add metadata (owner, runbook, tags)
   - Keep descriptions clear
   - Update when behavior changes

---

## Troubleshooting

### Alert Not Firing

**Check**:
1. Is alert enabled?
2. Does query return results?
3. Is condition actually met?
4. Check alerting service logs

```bash
# Test query manually
curl -X POST "http://localhost:9200/logs-*/_search" \
  -H 'Content-Type: application/json' \
  -d '{ ... query from alert rule ... }'

# Check alerting service logs
docker logs alerting-service
```

### Webhook Failing

**Check**:
1. Is URL correct and accessible?
2. Are headers correct?
3. Is payload format valid?
4. Check webhook service logs

```bash
# Test webhook manually
curl -X POST "https://hooks.slack.com/..." \
  -H 'Content-Type: application/json' \
  -d '{"text": "test"}'
```

### Too Many Alerts

**Solutions**:
1. Increase threshold
2. Extend time window
3. Add throttling
4. Add more specific filters
5. Combine related alerts

---

## Related Files

- [Alerting Service](../../analytics/alerting/) - Alert evaluation engine
- [Bootstrap Script](../../scripts/ops/bootstrap.sh) - Loads alert rules
- [API Documentation](../../docs/api/alerts.md) - Alert management API

---

**Last Updated**: 2026-02-04
