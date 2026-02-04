# User Guides

> End-user documentation for using the Vaultize Analytics Platform

---

## Overview

These guides help users effectively search logs, create dashboards, set up alerts, and get the most out of the platform.

---

## Documents

### [Getting Started](./getting-started.md)
Your first steps with the platform.

**Topics Covered**:
- Logging in to OpenSearch Dashboards
- Understanding the interface
- Your first search
- Basic navigation
- Key concepts and terminology

**Status**: 🔴 Not Started

---

### [Searching Logs](./searching-logs.md)
Master log search capabilities.

**Topics Covered**:
- Search syntax
- Time range selection
- Field-based filtering
- Full-text search
- Boolean operators
- Wildcard and regex searches
- Search best practices

**Status**: 🔴 Not Started

---

### [Creating Dashboards](./creating-dashboards.md)
Build custom dashboards for your use cases.

**Topics Covered**:
- Dashboard basics
- Adding visualizations
- Layout and organization
- Time range controls
- Filters and parameters
- Sharing dashboards
- Dashboard best practices

**Status**: 🔴 Not Started

---

### [Setting Up Alerts](./setting-up-alerts.md)
Configure alerts for important events.

**Topics Covered**:
- Alert concepts
- Creating alert rules
- Threshold configuration
- Notification channels (webhook, email, etc.)
- Testing alerts
- Managing alert fatigue

**Status**: 🔴 Not Started

---

### [Using Visualizations](./visualizations.md)
Create effective visualizations.

**Topics Covered**:
- Visualization types (line, bar, pie, table, etc.)
- Metric visualizations
- Aggregation-based charts
- Time series visualizations
- Heatmaps and histograms
- Customization options

**Status**: 🔴 Not Started

---

### [Saved Searches](./saved-searches.md)
Save and reuse common searches.

**Topics Covered**:
- Creating saved searches
- Organizing searches
- Sharing searches with team
- Parameterized searches
- Scheduled searches

**Status**: 🔴 Not Started

---

### [Best Practices](./best-practices.md)
Tips for effective log analysis.

**Topics Covered**:
- Efficient search strategies
- Dashboard design principles
- Alert tuning
- Performance optimization
- Common pitfalls to avoid

**Status**: 🔴 Not Started

---

## Quick Start Guide

### 1. Access the Platform
```
OpenSearch Dashboards: http://localhost:5601
Default credentials: admin / admin (change immediately)
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

## Common Use Cases

### Use Case 1: Monitor Application Errors
**Goal**: Track error rates across services

**Steps**:
1. Create search: `level:ERROR`
2. Create time series visualization counting errors
3. Add to dashboard
4. Set up alert when errors > 100 in 5 minutes

**Outcome**: Real-time error monitoring with automated alerts

---

### Use Case 2: Investigate Performance Issues
**Goal**: Find slow API requests

**Steps**:
1. Create search: `response_time_ms:>1000`
2. Add filters for specific service
3. Sort by response time descending
4. Analyze common patterns in slow requests

**Outcome**: Identify bottlenecks and optimization opportunities

---

### Use Case 3: Security Audit
**Goal**: Monitor authentication failures

**Steps**:
1. Create search: `event:"authentication_failed"`
2. Aggregate by source IP
3. Create visualization showing top failed IPs
4. Set alert for suspicious patterns

**Outcome**: Detect potential security threats

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
A: Depends on retention policy. Default is 30 days, configurable.

**Q: Can I export search results?**
A: Yes, use the "Export" button or API.

**Q: How do I share a dashboard?**
A: Use the "Share" button to get a shareable link.

**Q: Can I schedule reports?**
A: Yes, via the reporting feature (if enabled).

**Q: What's the difference between Discover and Dashboard?**
A: Discover is for ad-hoc searching, Dashboard is for monitoring.

---

## Learning Path

**Beginner** (Week 1):
1. Complete Getting Started guide
2. Practice basic searches
3. Create your first visualization
4. Build a simple dashboard

**Intermediate** (Week 2-3):
1. Master advanced search syntax
2. Create complex visualizations
3. Set up alerts
4. Organize saved searches

**Advanced** (Week 4+):
1. Build comprehensive monitoring dashboards
2. Optimize query performance
3. Create parameterized searches
4. Integrate with external tools via API

---

## Additional Resources

- [Video Tutorials](./video-tutorials.md) (Coming soon)
- [FAQ](./faq.md)
- [Keyboard Shortcuts](./keyboard-shortcuts.md)
- [Troubleshooting Guide](../operations/troubleshooting.md)

---

## Feedback and Support

Found an issue or have a suggestion? Please:
- Check [Known Issues](../operations/known-issues.md)
- Review [Troubleshooting Guide](../operations/troubleshooting.md)
- Contact your platform administrator

---

**Last Updated**: 2026-02-04
