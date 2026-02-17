# User Guides

> End-user documentation for using the Vaultize Analytics Platform

**Last Updated**: 2026-02-17

---

## Quick Start

### 1. Access the Platform
```
OpenSearch Dashboards: http://localhost:5601
Analytics API Docs:    http://localhost:8000/docs
Default credentials:   admin / admin (change immediately)
```

### 2. Your First Search
1. Click "Discover" in the left sidebar
2. Select time range (e.g., "Last 15 minutes")
3. Enter search query in the search bar: `level:ERROR`
4. Click "Search" or press Enter
5. Review results

### 3. Create a Visualization
1. Click "Visualize" in the left sidebar
2. Click "Create visualization"
3. Select visualization type (e.g., "Vertical bar")
4. Choose data source (index pattern)
5. Configure metrics and buckets
6. Click "Save" to save visualization

### 4. Build a Dashboard
1. Click "Dashboard" in the left sidebar
2. Click "Create dashboard"
3. Click "Add" to add existing visualizations
4. Arrange visualizations by dragging
5. Click "Save" to save dashboard

---

## Search Cheat Sheet

| Query | Description |
|-------|-------------|
| `error` | Full-text search for "error" |
| `level:ERROR` | Exact field match |
| `level:ERROR OR level:FATAL` | Boolean OR |
| `level:ERROR AND service:api` | Boolean AND |
| `message:"connection timeout"` | Phrase search |
| `status_code:[400 TO 499]` | Range query |
| `NOT level:DEBUG` | Negation |
| `service:api*` | Wildcard |
| `message:/timeout\|error/` | Regex |

---

## Common Use Cases

### Monitor Application Errors
**Goal**: Track error rates across services

1. Create search: `level:ERROR`
2. Create time series visualization counting errors
3. Add to dashboard
4. Set up alert when errors > 100 in 5 minutes

### Investigate Performance Issues
**Goal**: Find slow API requests

1. Create search: `response_time_ms:>1000`
2. Add filters for specific service
3. Sort by response time descending
4. Analyze common patterns in slow requests

### Security Audit
**Goal**: Monitor authentication failures

1. Create search: `event:"authentication_failed"`
2. Aggregate by source IP
3. Create visualization showing top failed IPs
4. Set alert for suspicious patterns

---

## Dashboard Best Practices

1. **Keep it focused**: One dashboard per use case
2. **Start with time series**: Trends over time are most valuable
3. **Use consistent colors**: Same meaning = same color
4. **Add context**: Include totals and averages
5. **Optimize performance**: Limit visualizations per dashboard
6. **Set appropriate time ranges**: Match the use case

---

## Alert Best Practices

1. **Start conservative**: Avoid alert fatigue with high thresholds
2. **Use meaningful names**: Alert name should explain the issue
3. **Add context to notifications**: Include relevant details
4. **Test before enabling**: Verify alerts work as expected
5. **Review and tune**: Adjust based on false positives/negatives
6. **Document runbooks**: Link to resolution procedures

---

## Common Questions

**Q: How far back can I search?**
A: Depends on retention policy. Default is 30 days, configurable via ILM policies.

**Q: Can I export search results?**
A: Yes, use the "Export" button in Dashboards or the Analytics API.

**Q: How do I share a dashboard?**
A: Use the "Share" button to get a shareable link.

**Q: What's the difference between Discover and Dashboard?**
A: Discover is for ad-hoc searching. Dashboard is for monitoring with saved visualizations.

---

## Learning Path

**Beginner** (Week 1):
1. Practice basic searches in Discover
2. Create your first visualization
3. Build a simple dashboard

**Intermediate** (Week 2-3):
1. Master advanced search syntax (Boolean, range, regex)
2. Create complex visualizations
3. Set up alerts via the alerting service
4. Use the Analytics API for programmatic access

**Advanced** (Week 4+):
1. Build comprehensive monitoring dashboards
2. Optimize query performance
3. Integrate with external tools via API and webhooks
4. Configure custom alert rules and ILM policies
